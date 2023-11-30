from spyral_utils.nuclear.momentum import (
    momentum_4_vec_from_cartesian,
    momentum_4_vec_from_spherical,
    get_transform_to_CoM,
    apply_transform,
)
from math import sin, cos
import numpy as np


def test_momentum_generation():
    p = 3.0
    polar = 0.45
    azim = 0.0
    energy = 9.0 + 1.0

    px = p * sin(polar) * cos(azim)
    py = p * sin(polar) * sin(azim)
    pz = p * cos(polar)

    cart_vec = momentum_4_vec_from_cartesian(px, py, pz, energy)
    pol_vec = momentum_4_vec_from_spherical(polar, azim, p, energy)

    assert np.array_equal(cart_vec, pol_vec)


def test_lorentz_transform():
    PRECISION = 1.0e-10

    p = 3.0
    polar = 0.45
    azim = 0.0
    energy = 9.0 + 1.0

    vec = momentum_4_vec_from_spherical(polar, azim, p, energy)

    transform = get_transform_to_CoM(vec)
    boosted = apply_transform(transform, vec)

    print(boosted)

    assert abs(boosted[0]) < PRECISION
    assert abs(boosted[1]) < PRECISION
    assert abs(boosted[2]) < PRECISION
