
import tensorflow as tf
from diffusion_model import PaddedConv2D , ResBlock ,Downsample , SpatialTransformer , apply_seq 


class HintNet(tf.keras.models.Model):
    def __init__(self):
        super().__init__()
        
        self.blocks = [
            PaddedConv2D(16, kernel_size=3, padding=1),
            tf.keras.activations.swish,
            PaddedConv2D(16, kernel_size=3, padding=1),
            tf.keras.activations.swish,
            PaddedConv2D(32, kernel_size=3, padding=1, stride=2),
            tf.keras.activations.swish,
            PaddedConv2D(32, kernel_size=3, padding=1),
            tf.keras.activations.swish,
            PaddedConv2D(96, kernel_size=3, padding=1, stride=2),
            tf.keras.activations.swish,
            PaddedConv2D(96, kernel_size=3, padding=1),
            tf.keras.activations.swish,
            PaddedConv2D(256, kernel_size=3, padding=1, stride=2),
            tf.keras.activations.swish,
            PaddedConv2D(320, kernel_size=3, padding=1),
        ]

    def call(self, inputs):
      x = inputs
      for l in self.blocks:
        x = l(x)
      return x 
        
        

class ControlNet(tf.keras.models.Model):
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

        self.zero_convs = [ PaddedConv2D(320, kernel_size=1, padding=0),
                           PaddedConv2D(320, kernel_size=1, padding=0),
                           PaddedConv2D(320, kernel_size=1, padding=0),
                           PaddedConv2D(320, kernel_size=1, padding=0),
                           PaddedConv2D(640, kernel_size=1, padding=0),
                           PaddedConv2D(640, kernel_size=1, padding=0),
                           PaddedConv2D(640, kernel_size=1, padding=0),
                           PaddedConv2D(1280, kernel_size=1, padding=0),
                           PaddedConv2D(1280, kernel_size=1, padding=0),
                           PaddedConv2D(1280, kernel_size=1, padding=0),
                           PaddedConv2D(1280, kernel_size=1, padding=0),
                           PaddedConv2D(1280, kernel_size=1, padding=0),
                           PaddedConv2D(1280, kernel_size=1, padding=0)
                            ]
       

    def call(self, inputs):
        x, t_emb, context, hint_out = inputs
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
                if i == 0:
                  x = x + hint_out
            saved_inputs.append(x)

        for layer in self.middle_block:
            x = apply(x, layer)
        saved_inputs.append(x)

        assert len(saved_inputs) == 13 

        outs = []
        for i,x in enumerate(saved_inputs):
           outs.append( self.zero_convs[i](x) )
        
        return outs 

        
