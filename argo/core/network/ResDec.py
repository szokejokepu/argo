import tensorflow as tf
import sonnet as snt
from ..keras_models.keras_utils import get_renorm_clipping
from .build_utils import residual_stack
from .AbstractResNetLayer import AbstractResNetLayer


class ResDec(AbstractResNetLayer):
    """
    res dec used in VQ
    """

    def __init__(self, num_hiddens, num_residual_layers, num_residual_hiddens,
                 activation,
                 is_training,
                 name='ResDec',
                 prob_drop=0.1,
                 bn_momentum=0.99,
                 bn_renormalization=True,
                 **extra_params):

        super().__init__(num_hiddens,
                         num_residual_layers,
                         num_residual_hiddens,
                         activation,
                         is_training,
                         name=name,
                         prob_drop=prob_drop,
                         bn_momentum=bn_momentum,
                         bn_renormalization=bn_renormalization,
                         **extra_params)

    def _build(self, x):
        h = snt.Conv2D(
            output_channels=self._num_hiddens,
            kernel_shape=(3, 3),
            stride=(1, 1),
            name="dec_1")(x)

        h = self._dropout(h, training=self._is_training)
        h = tf.layers.batch_normalization(h, training=self._is_training,
                                            momentum=self._bn_momentum,
                                            renorm=self._bn_renormalization,
                                            renorm_momentum=self._bn_momentum,
                                            renorm_clipping=self._renorm_clipping,
                                            name="batch_norm_1")

        h = residual_stack(
                h,
                self._num_hiddens,
                self._num_residual_layers,
                self._num_residual_hiddens,
                activation = self._activation,
                training=self._is_training,
                prob_drop=self._prob_drop,
                momentum=self._bn_momentum,
                renorm=self._bn_renormalization,
                renorm_momentum=self._bn_momentum,
                renorm_clipping=self._renorm_clipping
        )

        h = snt.Conv2DTranspose(
            output_channels=int(self._num_hiddens / 2),
            output_shape=None,
            kernel_shape=(4, 4),
            stride=(2, 2),
            name="dec_2")(h)

        h = self._dropout(h, training=self._is_training)
        h = tf.layers.batch_normalization(h, training=self._is_training,
                                            momentum=self._bn_momentum,
                                            renorm=self._bn_renormalization,
                                            renorm_momentum=self._bn_momentum,
                                            renorm_clipping=self._renorm_clipping,
                                            name="batch_norm_2")

        h = self._activation(h)

        x_recon = snt.Conv2DTranspose(
            output_channels=3,
            output_shape=None,
            kernel_shape=(4, 4),
            stride=(2, 2),
            name="dec_3")(h)

        return x_recon
