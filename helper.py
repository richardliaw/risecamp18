import numpy as np
import keras
from keras.datasets import mnist
from keras.preprocessing.image import ImageDataGenerator
from keras import backend as K
import itertools

def load_data(limit_threads=4, generator=True, iter_limit=200):
    if limit_threads:
        K.set_session(
            K.tf.Session(
                config=K.tf.ConfigProto(
                    intra_op_parallelism_threads=limit_threads,
                    inter_op_parallelism_threads=limit_threads)))
    num_classes = 10

    # input image dimensions
    img_rows, img_cols = 28, 28

    # the data, split between train and test sets
    (x_train, y_train), (x_test, y_test) = mnist.load_data()

    if K.image_data_format() == 'channels_first':
        x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols)
        x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)
        input_shape = (1, img_rows, img_cols)
    else:
        x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
        x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
        input_shape = (img_rows, img_cols, 1)

    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255
    print('x_train shape:', x_train.shape)
    print(x_train.shape[0], 'train samples')
    print(x_test.shape[0], 'test samples')

    # convert class vectors to binary class matrices
    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)
    if generator:
        datagen = ImageDataGenerator()
        return itertools.islice(datagen.flow(x_train, y_train), iter_limit)
    return x_train, x_test, y_train, y_test


class TuneCallback(keras.callbacks.Callback):
    def __init__(self, reporter, logs={}):
        self.reporter = reporter

    def on_train_end(self, epoch, logs={}):
        self.reporter(done=1, mean_accuracy=logs["acc"])

    def on_batch_end(self, batch, logs={}):
        self.reporter(mean_accuracy=logs["acc"])
