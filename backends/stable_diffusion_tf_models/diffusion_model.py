import tensorflow as tf
from group_norm import GroupNormalization

from layers import PaddedConv2D, apply_seq, td_dot, GEGLU


class ResBlock(tf.keras.layers.Layer):
    def __init__(self, channels, out_channels):
        super().__init__()
        self.in_layers = [
            GroupNormalization(epsilon=1e-5),
            tf.keras.activations.swish,
            PaddedConv2D(out_channels, 3, padding=1),
        ]
        self.emb_layers = [
            tf.keras.activations.swish,
            tf.keras.layers.Dense(out_channels),
        ]
        self.out_layers = [
            GroupNormalization(epsilon=1e-5),
            tf.keras.activations.swish,
            PaddedConv2D(out_channels, 3, padding=1),
        ]
        self.skip_connection = (
            PaddedConv2D(out_channels, 1) if channels != out_channels else lambda x: x
        )

    def call(self, inputs):
        x, emb = inputs
        h = apply_seq(x, self.in_layers)
        emb_out = apply_seq(emb, self.emb_layers)
        h = h + emb_out[:, None, None]
        h = apply_seq(h, self.out_layers)
        ret = self.skip_connection(x) + h
        return ret


def td_split( x , n_splits=1):
    if n_splits == 1:
        return [x]
    else:
        n = x.shape[1]
        assert n%2 == 0
        x1 = x[: , :n//2]
        x2 = x[: , n//2:]
        return td_split(x1 , n_splits-1 ) + td_split(x2 , n_splits-1 )

class CrossAttention(tf.keras.layers.Layer):
    def __init__(self, n_heads, d_head):
        super().__init__()
        self.to_q = tf.keras.layers.Dense(n_heads * d_head, use_bias=False)
        self.to_k = tf.keras.layers.Dense(n_heads * d_head, use_bias=False)
        self.to_v = tf.keras.layers.Dense(n_heads * d_head, use_bias=False)
        self.scale = d_head**-0.5
        self.num_heads = n_heads
        self.head_size = d_head
        self.to_out = [tf.keras.layers.Dense(n_heads * d_head)]

    def call(self, inputs):
        assert type(inputs) is list
        if len(inputs) == 1:
            inputs = inputs + [None]
        x, context = inputs
        context = x if context is None else context
        q, k, v = self.to_q(x), self.to_k(context), self.to_v(context)
        assert len(x.shape) == 3
        q = tf.reshape(q, (-1, x.shape[1], self.num_heads, self.head_size))
        k = tf.reshape(k, (-1, context.shape[1], self.num_heads, self.head_size))
        v = tf.reshape(v, (-1, context.shape[1], self.num_heads, self.head_size))

        q = tf.keras.layers.Permute((2, 1, 3))(q)  # (bs, num_heads, time, head_size)
        k = tf.keras.layers.Permute((2, 3, 1))(k)  # (bs, num_heads, head_size, time)
        v = tf.keras.layers.Permute((2, 1, 3))(v)  # (bs, num_heads, time, head_size)

        nspl = 1
        num_heads = v.shape[1]
        ntime = v.shape[2]
    
        if num_heads * ntime * ntime >= 8*4096*4096 - 1000:
            nspl = 2
        if num_heads * ntime * ntime >= 16*4096*4096 - 1000:
            nspl = 3
        if num_heads * ntime * ntime >= 32*4096*4096 - 1000:
            nspl = 4

        qs = td_split(q , nspl )
        ks = td_split(k , nspl )
        vs = td_split(v , nspl )

        scores = [td_dot(q_, k_) * self.scale for q_, k_ in zip(qs , ks) ]
        #score = td_dot(q, k) * self.scale

        # weights = tf.keras.activations.softmax(score)  # (bs, num_heads, time, time)
        weightss = [tf.keras.activations.softmax(s_) for s_ in  scores  ]
        attentions = [td_dot(w_, v_) for w_,v_ in zip(weightss , vs)]
        attention = tf.concat(attentions , axis=1)
        attention = tf.keras.layers.Permute((2, 1, 3))(
            attention
        )  # (bs, time, num_heads, head_size)
        h_ = tf.reshape(attention, (-1, x.shape[1], self.num_heads * self.head_size))
        return apply_seq(h_, self.to_out)


class BasicTransformerBlock(tf.keras.layers.Layer):
    def __init__(self, dim, n_heads, d_head):
        super().__init__()
        self.norm1 = tf.keras.layers.LayerNormalization(epsilon=1e-5)
        self.attn1 = CrossAttention(n_heads, d_head)

        self.norm2 = tf.keras.layers.LayerNormalization(epsilon=1e-5)
        self.attn2 = CrossAttention(n_heads, d_head)

        self.norm3 = tf.keras.layers.LayerNormalization(epsilon=1e-5)
        self.geglu = GEGLU(dim * 4)
        self.dense = tf.keras.layers.Dense(dim)

    def call(self, inputs):
        x, context = inputs
        x = self.attn1([self.norm1(x)]) + x
        x = self.attn2([self.norm2(x), context]) + x
        return self.dense(self.geglu(self.norm3(x))) + x


class SpatialTransformer(tf.keras.layers.Layer):
    def __init__(self, channels, n_heads, d_head):
        super().__init__()
        self.norm = GroupNormalization(epsilon=1e-5)
        assert channels == n_heads * d_head
        self.proj_in = PaddedConv2D(n_heads * d_head, 1)
        self.transformer_blocks = [BasicTransformerBlock(channels, n_heads, d_head)]
        self.proj_out = PaddedConv2D(channels, 1)

    def call(self, inputs):
        x, context = inputs
        b, h, w, c = x.shape
        x_in = x
        x = self.norm(x)
        x = self.proj_in(x)
        x = tf.reshape(x, (-1, h * w, c))
        for block in self.transformer_blocks:
            x = block([x, context])
        x = tf.reshape(x, (-1, h, w, c))
        return self.proj_out(x) + x_in


class Downsample(tf.keras.layers.Layer):
    def __init__(self, channels):
        super().__init__()
        self.op = PaddedConv2D(channels, 3, stride=2, padding=1)

    def call(self, x):
        return self.op(x)


class Upsample(tf.keras.layers.Layer):
    def __init__(self, channels):
        super().__init__()
        self.ups = tf.keras.layers.UpSampling2D(size=(2, 2))
        self.conv = PaddedConv2D(channels, 3, padding=1)

    def call(self, x):
        x = self.ups(x)
        return self.conv(x)


class UNetModel(tf.keras.models.Model):
    def __init__(self):
        super().__init__()
        self.time_embed = [
            tf.keras.layers.Dense(1280),
            tf.keras.activations.swish,
            tf.keras.layers.Dense(1280),
        ]
        self.input_blocks = [
            [PaddedConv2D(320, kernel_size=3, padding=1)],
            [ResBlock(320, 320), SpatialTransformer(320, 8, 40)],
            [ResBlock(320, 320), SpatialTransformer(320, 8, 40)],
            [Downsample(320)],
            [ResBlock(320, 640), SpatialTransformer(640, 8, 80)],
            [ResBlock(640, 640), SpatialTransformer(640, 8, 80)],
            [Downsample(640)],
            [ResBlock(640, 1280), SpatialTransformer(1280, 8, 160)],
            [ResBlock(1280, 1280), SpatialTransformer(1280, 8, 160)],
            [Downsample(1280)],
            [ResBlock(1280, 1280)],
            [ResBlock(1280, 1280)],
        ]
        self.middle_block = [
            ResBlock(1280, 1280),
            SpatialTransformer(1280, 8, 160),
            ResBlock(1280, 1280),
        ]
        self.output_blocks = [
            [ResBlock(2560, 1280)],
            [ResBlock(2560, 1280)],
            [ResBlock(2560, 1280), Upsample(1280)],
            [ResBlock(2560, 1280), SpatialTransformer(1280, 8, 160)],
            [ResBlock(2560, 1280), SpatialTransformer(1280, 8, 160)],
            [
                ResBlock(1920, 1280),
                SpatialTransformer(1280, 8, 160),
                Upsample(1280),
            ],
            [ResBlock(1920, 640), SpatialTransformer(640, 8, 80)],  # 6
            [ResBlock(1280, 640), SpatialTransformer(640, 8, 80)],
            [
                ResBlock(960, 640),
                SpatialTransformer(640, 8, 80),
                Upsample(640),
            ],
            [ResBlock(960, 320), SpatialTransformer(320, 8, 40)],
            [ResBlock(640, 320), SpatialTransformer(320, 8, 40)],
            [ResBlock(640, 320), SpatialTransformer(320, 8, 40)],
        ]
        self.out = [
            GroupNormalization(epsilon=1e-5),
            tf.keras.activations.swish,
            PaddedConv2D(4, kernel_size=3, padding=1),
        ]

    def call(self, inputs):
        if len(inputs) == 3:
            x, t_emb, context = inputs
            controls = None
        elif len(inputs ) == (3+13):
            x = inputs[0]
            t_emb = inputs[1]
            context = inputs[2]
            controls = inputs[3:]
        else:
            raise ValueError("inalid no of inputs")

        emb = apply_seq(t_emb, self.time_embed)

        def apply(x, layer):
            if isinstance(layer, ResBlock):
                x = layer([x, emb])
            elif isinstance(layer, SpatialTransformer):
                x = layer([x, context])
            else:
                x = layer(x)
            return x

        saved_inputs = []
        for i,b in enumerate(self.input_blocks):
            for layer in b:
                x = apply(x, layer)
            saved_inputs.append(x)

        
        for layer in self.middle_block:
            x = apply(x, layer)

        if controls is not None:
            x = x + controls[12]
            assert len(saved_inputs) == 12
            for i in range(len(saved_inputs)):
                saved_inputs[i] = saved_inputs[i] + controls[i]

        for b in self.output_blocks:
            x = tf.concat([x, saved_inputs.pop()], axis=-1)
            for layer in b:
                x = apply(x, layer)
        return apply_seq(x, self.out)





class UNetModelV2(tf.keras.models.Model):
    def __init__(self):
        super().__init__()
        self.time_embed = [
            tf.keras.layers.Dense(1280),
            tf.keras.activations.swish,
            tf.keras.layers.Dense(1280),
        ]
        self.input_blocks = [
            [PaddedConv2D(320, kernel_size=3, padding=1)],
            [ResBlock(320, 320), SpatialTransformer(320, 5, 64)],
            [ResBlock(320, 320), SpatialTransformer(320, 5, 64)],
            [Downsample(320)],
            [ResBlock(320, 640), SpatialTransformer(640, 10, 64)],
            [ResBlock(640, 640), SpatialTransformer(640, 10, 64)],
            [Downsample(640)],
            [ResBlock(640, 1280), SpatialTransformer(1280, 20, 64)],
            [ResBlock(1280, 1280), SpatialTransformer(1280, 20, 64)],
            [Downsample(1280)],
            [ResBlock(1280, 1280)],
            [ResBlock(1280, 1280)],
        ]
        self.middle_block = [
            ResBlock(1280, 1280),
            SpatialTransformer(1280, 20, 64),
            ResBlock(1280, 1280),
        ]
        self.output_blocks = [
            [ResBlock(2560, 1280)],
            [ResBlock(2560, 1280)],
            [ResBlock(2560, 1280), Upsample(1280)],
            [ResBlock(2560, 1280), SpatialTransformer(1280, 20, 64)],
            [ResBlock(2560, 1280), SpatialTransformer(1280, 20, 64)],
            [
                ResBlock(1920, 1280),
                SpatialTransformer(1280, 20, 64),
                Upsample(1280),
            ],
            [ResBlock(1920, 640), SpatialTransformer(640, 10, 64)],  # 6
            [ResBlock(1280, 640), SpatialTransformer(640, 10, 64)],
            [
                ResBlock(960, 640),
                SpatialTransformer(640, 10, 64),
                Upsample(640),
            ],
            [ResBlock(960, 320), SpatialTransformer(320, 5, 64)],
            [ResBlock(640, 320), SpatialTransformer(320, 5, 64)],
            [ResBlock(640, 320), SpatialTransformer(320, 5, 64)],
        ]
        self.out = [
            GroupNormalization(epsilon=1e-5),
            tf.keras.activations.swish,
            PaddedConv2D(4, kernel_size=3, padding=1),
        ]

    def call(self, inputs):
        if len(inputs) == 3:
            x, t_emb, context = inputs
            controls = None
        elif len(inputs ) == (3+13):
            x = inputs[0]
            t_emb = inputs[1]
            context = inputs[2]
            controls = inputs[3:]
        else:
            raise ValueError("inalid no of inputs")

        emb = apply_seq(t_emb, self.time_embed)

        def apply(x, layer):
            if isinstance(layer, ResBlock):
                x = layer([x, emb])
            elif isinstance(layer, SpatialTransformer):
                x = layer([x, context])
            else:
                x = layer(x)
            return x

        saved_inputs = []
        for i,b in enumerate(self.input_blocks):
            for layer in b:
                x = apply(x, layer)
            saved_inputs.append(x)

        
        for layer in self.middle_block:
            x = apply(x, layer)

        if controls is not None:
            x = x + controls[12]
            assert len(saved_inputs) == 12
            for i in range(len(saved_inputs)):
                saved_inputs[i] = saved_inputs[i] + controls[i]

        for b in self.output_blocks:
            x = tf.concat([x, saved_inputs.pop()], axis=-1)
            for layer in b:
                x = apply(x, layer)
        return apply_seq(x, self.out)
