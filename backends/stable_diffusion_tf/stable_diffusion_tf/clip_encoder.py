import tensorflow as tf
from tensorflow import keras
import tensorflow_addons as tfa
import numpy as np

from .layers import quick_gelu


class CLIPAttention(keras.layers.Layer):
    def __init__(self):
        super().__init__()
        self.embed_dim = 768
        self.num_heads = 12
        self.head_dim = self.embed_dim // self.num_heads
        self.scale = self.head_dim**-0.5
        self.q_proj = keras.layers.Dense(self.embed_dim)
        self.k_proj = keras.layers.Dense(self.embed_dim)
        self.v_proj = keras.layers.Dense(self.embed_dim)
        self.out_proj = keras.layers.Dense(self.embed_dim)

    def _shape(self, tensor, seq_len: int, bsz: int):
        a = tf.reshape(tensor, (bsz, seq_len, self.num_heads, self.head_dim))
        return keras.layers.Permute((2, 1, 3))(a)  # bs , n_head , seq_len , head_dim

    def call(self, inputs):
        hidden_states, causal_attention_mask = inputs
        bsz, tgt_len, embed_dim = hidden_states.shape
        query_states = self.q_proj(hidden_states) * self.scale
        key_states = self._shape(self.k_proj(hidden_states), tgt_len, -1)
        value_states = self._shape(self.v_proj(hidden_states), tgt_len, -1)

        proj_shape = (-1, tgt_len, self.head_dim)
        query_states = self._shape(query_states, tgt_len, -1)
        query_states = tf.reshape(query_states, proj_shape)
        key_states = tf.reshape(key_states, proj_shape)

        src_len = tgt_len
        value_states = tf.reshape(value_states, proj_shape)
        attn_weights = query_states @ keras.layers.Permute((2, 1))(key_states)

        attn_weights = tf.reshape(attn_weights, (-1, self.num_heads, tgt_len, src_len))
        attn_weights = attn_weights + causal_attention_mask
        attn_weights = tf.reshape(attn_weights, (-1, tgt_len, src_len))

        attn_weights = tf.nn.softmax(attn_weights)
        attn_output = attn_weights @ value_states

        attn_output = tf.reshape(
            attn_output, (-1, self.num_heads, tgt_len, self.head_dim)
        )
        attn_output = keras.layers.Permute((2, 1, 3))(attn_output)
        attn_output = tf.reshape(attn_output, (-1, tgt_len, embed_dim))

        return self.out_proj(attn_output)


class CLIPEncoderLayer(keras.layers.Layer):
    def __init__(self):
        super().__init__()
        self.layer_norm1 = keras.layers.LayerNormalization(epsilon=1e-5)
        self.self_attn = CLIPAttention()
        self.layer_norm2 = keras.layers.LayerNormalization(epsilon=1e-5)
        self.fc1 = keras.layers.Dense(3072)
        self.fc2 = keras.layers.Dense(768)

    def call(self, inputs):
        hidden_states, causal_attention_mask = inputs
        residual = hidden_states

        hidden_states = self.layer_norm1(hidden_states)
        hidden_states = self.self_attn([hidden_states, causal_attention_mask])
        hidden_states = residual + hidden_states

        residual = hidden_states
        hidden_states = self.layer_norm2(hidden_states)

        hidden_states = self.fc1(hidden_states)
        hidden_states = quick_gelu(hidden_states)
        hidden_states = self.fc2(hidden_states)

        return residual + hidden_states


class CLIPEncoder(keras.layers.Layer):
    def __init__(self):
        super().__init__()
        self.layers = [CLIPEncoderLayer() for i in range(12)]

    def call(self, inputs):
        [hidden_states, causal_attention_mask] = inputs
        for l in self.layers:
            hidden_states = l([hidden_states, causal_attention_mask])
        return hidden_states


class CLIPTextEmbeddings(keras.layers.Layer):
    def __init__(self, n_words=77):
        super().__init__()
        self.token_embedding_layer = keras.layers.Embedding(
            49408, 768, name="token_embedding"
        )
        self.position_embedding_layer = keras.layers.Embedding(
            n_words, 768, name="position_embedding"
        )

    def call(self, inputs):
        input_ids, position_ids = inputs
        word_embeddings = self.token_embedding_layer(input_ids)
        position_embeddings = self.position_embedding_layer(position_ids)
        return word_embeddings + position_embeddings


class CLIPTextTransformer(keras.models.Model):
    def __init__(self, n_words=77):
        super().__init__()
        self.embeddings = CLIPTextEmbeddings(n_words=n_words)
        self.encoder = CLIPEncoder()
        self.final_layer_norm = keras.layers.LayerNormalization(epsilon=1e-5)
        self.causal_attention_mask = tf.constant(
            np.triu(np.ones((1, 1, 77, 77), dtype="float32") * -np.inf, k=1)
        )

    def call(self, inputs):
        input_ids, position_ids = inputs
        x = self.embeddings([input_ids, position_ids])
        x = self.encoder([x, self.causal_attention_mask])
        return self.final_layer_norm(x)
