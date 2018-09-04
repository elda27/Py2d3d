import numpy as np
import vtk


def convert_numpy_matrix4x4(m: np.ndarray):
    """Convert numpy array to vtkMatrix4x4

    Args:
        m (np.ndarray): An array will be converted vtkMatrix4x4.

    Returns:
        vtk.vtkMatrix4x4: Converted matrix
    """

    assert isinstance(m, np.ndarray)
    assert m.ndim == 2 and (m.shape == (4, 4) or m.shape == (3, 3))

    dst = vtk.vtkMatrix4x4()
    dst.SetElement(3, 3, 1.0)
    for i in range(m.size):
        index = np.unravel_index(i, m.shape)
        dst.SetElement(*index, m[index])
    return dst
