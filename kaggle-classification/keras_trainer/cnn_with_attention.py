"""Model class for a single layer CNN"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from keras.layers import Conv1D
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Embedding
from keras.layers import Flatten
from keras.layers import Input
from keras.layers import AveragePooling1D
from keras.layers import Activation
from keras.layers import Concatenate
from keras.layers import Multiply
from keras.models import Model
from keras.layers import Permute
from keras_trainer import base_model
from keras.layers import Activation


class CNNWithAttention(base_model.BaseModel):
  """Single Layer Based CNN

  hparams:
    embedding_dim
    vocab_size
    sequence_length
    dropout_rate
    train_embedding
  """

  def __init__(self, embeddings_matrix, hparams):
    self.embeddings_matrix = embeddings_matrix
    self.hparams = hparams

  def get_model(self):
    I = Input(shape=(self.hparams.sequence_length,), dtype='float32')
    E = Embedding(
        self.hparams.vocab_size,
        self.hparams.embedding_dim,
        weights=[self.embeddings_matrix],
        input_length=self.hparams.sequence_length,
        trainable=self.hparams.train_embedding)(I)
    X5 = Conv1D(128, 5, activation='relu', padding='same')(E)
    X4 = Conv1D(128, 4, activation='relu', padding='same')(E)
    X3 = Conv1D(128, 3, activation='relu', padding='same')(E)
    X = Concatenate(axis=-1)([X5, X4, X3])
    A = Dense(1)(X)
    # Permute trick to apply softmax to second to last layer.
    A = Permute((2,1))(A)
    A = Activation('softmax')(A)
    A = Permute((2,1))(A)
    X = Multiply()([A, X])
    X = AveragePooling1D(self.hparams.sequence_length, padding='same')(X)
    X = Flatten()(X)
    X = Dropout(self.hparams.dropout_rate)(X)
    X = Dense(128, activation='relu')(X)
    X = Dropout(self.hparams.dropout_rate)(X)
    toxic_out = Dense(1, activation='sigmoid', name='toxic')(X)
    severe_toxic_out = Dense(1, activation='sigmoid', name='severe_toxic')(X)
    obscene_out = Dense(1, activation='sigmoid', name='obscene')(X)
    threat_out = Dense(1, activation='sigmoid', name='threat')(X)
    insult_out = Dense(1, activation='sigmoid', name='insult')(X)
    identity_hate_out = Dense(1, activation='sigmoid', name='identity_hate')(X)

    model = Model(inputs=I, outputs=[toxic_out, severe_toxic_out, obscene_out, threat_out, insult_out, identity_hate_out])
    model.compile(optimizer='rmsprop',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    print(model.summary())
    return model
