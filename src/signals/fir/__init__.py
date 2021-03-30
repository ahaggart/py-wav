import math

from custom_types import Partial, Hz


def get_filter_order(fs: Partial,
                     transition_width: Partial,
                     passband_ripple: float,
                     stopband_attenuation: float):
    """
    https://dsp.stackexchange.com/questions/31066/how-many-taps-does-an-fir-filter-need
    """
    return (
            (2 / 3)
            * math.log10(1 / (10 * passband_ripple * stopband_attenuation))
            * fs / transition_width
    )


def get_filter_order_by_cutoff(fs: Partial,
                               cutoff: Hz,
                               passband_ripple: float,
                               stopband_attenuation: float):
    return get_filter_order(fs, cutoff/2, passband_ripple, stopband_attenuation)
