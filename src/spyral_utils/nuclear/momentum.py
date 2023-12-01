"""Module conaining functions for using momentum 4-vectors

Create numpy arrays for doing 4-vector math

Functions
---------
momentum_4_vec_from_cartesian(px: float, py: float, pz: float, E: float) -> ndarray
    Create a momentum 4-vector from cartesian momenta, energy
momentum_4_vec_from_spherical(polar: float, azimuthal: float, p: float, E: float) -> ndarray
    Create a momentum 4-vector from spherical angles, momentum, energy
get_transform_to_CoM(momentum: ndarray) -> ndarray:
    Get the center of mass transformation for a 4-vector
apply_transform(transform: ndarray, momentum: ndarray) -> ndarray:
    Apply a Lorentz transform to a 4-vector
"""

import numpy as np


def momentum_4_vec_from_cartesian(
    px: float, py: float, pz: float, E: float
) -> np.ndarray:
    """Create a momentum 4-vector from cartesian momenta, energy

    Create a momentum 4-vector from momentum x,y,z and energy

    Parameters
    ----------
    px: float
        Momentum along the x-coordinate
    py: float
        Momentum along the y-coordinate
    pz: float
        Momentum along the z-coordinate
    E: float
        Total energy

    Returns
    -------
    ndarray
        an array representing the four-vector (length 4, dtype float)
    """
    return np.array([px, py, pz, E])


def momentum_4_vec_from_spherical(
    polar: float, azimuthal: float, p: float, E: float
) -> np.ndarray:
    """Create a momentum 4-vector from spherical angles, momentum, energy

    Create a momentum 4-vector from the momentum magnitude, energy, and spherical coordinates angles

    Parameters
    ----------
    polar: float
        polar angle in radians
    azimuthal: float
        azimuthal angle in radians
    p: float
        magnitude of the 3-momentum
    E: float
        Total energy

    Returns
    -------
    ndarray
        an array representing the four-vector (length 4, dtype float)
    """
    return np.array(
        [
            p * np.sin(polar) * np.cos(azimuthal),
            p * np.sin(polar) * np.sin(azimuthal),
            p * np.cos(polar),
            E,
        ]
    )


def get_transform_to_CoM(momentum: np.ndarray) -> np.ndarray:
    """Get the center of mass transformation for a 4-vector

    Parameters
    ----------
    momentum: np.ndarray
        a length 4 momentum vector

    Returns
    -------
    ndarray
        a 4x4 matrix representing the transformation to the center of mass frame

    """
    beta_vec = -1.0 * momentum[:3] / momentum[3]
    beta = np.linalg.norm(beta_vec)
    gamma = 1.0 / np.sqrt(1.0 - beta**2.0)
    bgamma = gamma * gamma / (1.0 + gamma)
    bxy = beta_vec[0] * beta_vec[1]
    bxz = beta_vec[0] * beta_vec[2]
    byz = beta_vec[1] * beta_vec[2]
    return np.array(
        [
            [
                1.0 + bgamma * beta_vec[0] ** 2.0,
                bgamma * bxy,
                bgamma * bxz,
                gamma * beta_vec[0],
            ],
            [
                bgamma * bxy,
                1.0 + bgamma * beta_vec[1] ** 2.0,
                bgamma * byz,
                gamma * beta_vec[1],
            ],
            [
                bgamma * bxz,
                bgamma * byz,
                1.0 + bgamma * beta_vec[2] ** 2.0,
                gamma * beta_vec[2],
            ],
            [gamma * beta_vec[0], gamma * beta_vec[1], gamma * beta_vec[2], gamma],
        ]
    )


def apply_transform(transform: np.ndarray, momentum: np.ndarray) -> np.ndarray:
    """Apply a Lorentz transform to a 4-vector

    Parameters
    ----------
    transform: ndarray
        A 4x4 matrix representing the transformation
    momentum: ndarray
        A length 4 array representing the momentum 4-vector

    Returns
    -------
    ndarray
        A new length 4 array representing the transformed 4-vector
    """
    return transform @ momentum.T
