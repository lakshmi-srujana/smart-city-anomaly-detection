import numpy as np


def create_sequences(data: np.ndarray, seq_length: int = 24) -> tuple[np.ndarray, np.ndarray]:
    array = np.asarray(data)

    if seq_length <= 0:
        raise ValueError("seq_length must be greater than 0.")

    if array.ndim == 1:
        array = array.reshape(-1, 1)
    elif array.ndim != 2:
        raise ValueError("data must be a 1D or 2D NumPy array.")

    if len(array) < seq_length:
        raise ValueError("data length must be greater than or equal to seq_length.")

    n_samples = len(array) - seq_length + 1
    n_features = array.shape[1]

    X = np.empty((n_samples, seq_length, n_features), dtype=array.dtype)
    indices = np.arange(n_samples)

    for start_idx in range(n_samples):
        X[start_idx] = array[start_idx : start_idx + seq_length]

    return X, indices
