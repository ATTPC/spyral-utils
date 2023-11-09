import numpy as np

def momentum_4_vec_from_cartesian(px: float, py: float, pz: float, E: float) -> np.ndarray:
    return np.array([px, py, pz, E])

def momentum_4_vec_from_spherical(polar: float, azimuthal: float, p: float, E: float) ->  np.ndarray:
    return np.array([
        p * np.sin(polar) * np.cos(azimuthal),
        p * np.sin(polar) * np.sin(azimuthal),
        p * np.cos(polar),
        E
    ])

def get_transform_to_CoM(momentum: np.ndarray) -> np.ndarray:
    beta_vec = -1.0 * momentum[:3]/momentum[3]
    beta = np.linalg.norm(beta_vec)
    gamma = 1.0 / np.sqrt(1.0 - beta**2.0)
    bgamma = gamma * gamma / (1.0 + gamma)
    bxy = beta_vec[0] * beta_vec[1]
    bxz = beta_vec[0] * beta_vec[2]
    byz = beta_vec[1] * beta_vec[2]
    return np.array([
        [1.0 + bgamma * beta_vec[0], bgamma * bxy, bgamma * bxz, gamma * beta_vec[0]],
        [bgamma * bxy, 1.0 + bgamma * beta_vec[1], bgamma * byz, gamma * beta_vec[1]],
        [bgamma * bxz, bgamma * byz, 1.0 + bgamma * beta_vec[1], gamma * beta_vec[2]],
        [gamma * beta_vec[0], gamma * beta_vec[1], gamma * beta_vec[2], gamma]
    ])

def apply_transform(transform: np.ndarray, momentum: np.ndarray) -> np.ndarray:
    return transform @ momentum.T