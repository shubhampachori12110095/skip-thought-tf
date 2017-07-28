from __future__ import unicode_literals

import numpy as np
import tensorflow as tf


def pad_sequences(data, max_length, pad_value):
    """
    Pad sequence of indices with pad values to the length of max_length.

    Args:
        data (lists of lists of int): List of encoded lines.
        max_length (int): Padded sequence length.
        pad_value (int): Padding value.

    Returns:
        object (numpy.array): Padded array of indices.
    """
    data = [indices + [pad_value] * (max_length - len(indices)) for indices
            in data]
    return np.array(data)


def prepare_inputs_for_decoder(inputs, inputs_length, eos_token):
    """
    Take placeholder with padded _inputs and create decoder_inputs (prepended with eos)
    and decoder_targets (appended with eos).

    Args:
        inputs (tf.placeholder or tf.Tensor): Batch of padded sequences.
        inputs_length (1-D int32 tf.Tensor): Length of each sequence in batch.
        eos_token (int): EOS token index in vocabulary.

    Returns:
        (decoder_inputs, decoder_targets, targets_length)

    Notes:
        This function is inefficient because of two `tf.reverse_sequence` calls. If you know the better way how to
        append eos token at the end of sequence, please send pull request or write to persiyanov@phystech.edu.

    """
    batch_size = tf.shape(inputs)[0]
    eos_column = tf.ones([batch_size, 1], dtype=tf.int32) * eos_token

    decoder_inputs = tf.concat([eos_column, inputs], axis=1)

    reversed_inputs = tf.reverse_sequence(inputs, inputs_length, seq_axis=1)
    reversed_targets = tf.concat([eos_column, reversed_inputs], axis=1)
    decoder_targets = tf.reverse_sequence(reversed_targets, inputs_length + 1, seq_axis=1)

    return decoder_inputs, decoder_targets, inputs_length + 1


def create_embeddings_matrix(num_tokens, embedding_size, initialize_with=None, trainable=True):
    """
    Create tf.Variable which holds embeddings.

    Args:
        num_tokens (int): Number of words in vocabulary.
        embedding_size (int): Embedding size.
        initialize_with (numpy.array, optional): If passed, will be used for initializing embeddings.
        trainable (bool, optional): Flag indicating whether to train embeddings or not. Default to True, which means
            embedding matrix will be updated during training.

    Returns:
        tf.Variable with shape [num_tokens, embedding_size]
    """
    with tf.variable_scope('embeddings'):
        if initialize_with is not None:
            if initialize_with.shape != (num_tokens, embedding_size):
                shape = initialize_with.shape
                raise ValueError("initialize_with shape must be compatible with num_tokens and embedding_size,"
                                 "but [{}, {}] != [{}, {}]".format(num_tokens, embedding_size, shape[0], shape[1]))
            init = tf.constant_initializer(value=initialize_with)
        else:
            # Practical heuristic. U[-sqrt3, sqrt3] has variance=1.
            sqrt3 = np.sqrt(3)
            init = tf.random_uniform_initializer(-sqrt3, sqrt3)
        return tf.get_variable('embeddings_matrix', shape=[num_tokens, embedding_size],
                               initializer=init, trainable=trainable, dtype=tf.float32)
