from fractions import Fraction
from typing import Tuple


def rational_approximation(x: float, d_limit=100) -> Tuple[int, int]:
    frac = Fraction(x).limit_denominator(d_limit)
    return frac.numerator, frac.denominator
