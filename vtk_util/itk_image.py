import numpy as np
import SimpleITK as sitk
from typing import Tuple

_dtype_itk_depth_table = {
    'int8': sitk.sitkInt8,
    'uint8': sitk.sitkUInt8,
    'int16': sitk.sitkInt16,
    'uint16': sitk.sitkUInt16,
    'int32': sitk.sitkInt32,
    'uint32': sitk.sitkUInt32,
    'int64': sitk.sitkInt64,
    'uint64': sitk.sitkUInt64,
    'float32': sitk.sitkFloat32,
    'float64': sitk.sitkFloat64,
}

_dtype_itk_label_depth_table = {
    'int8': sitk.sitkLabelUInt8,
    'int16': sitk.sitkLabelUInt16,
    'int32': sitk.sitkLabelUInt32,
    'int64': sitk.sitkLabelUInt64,
    'uint8': sitk.sitkLabelUInt8,
    'uint16': sitk.sitkLabelUInt16,
    'uint32': sitk.sitkLabelUInt32,
    'uint64': sitk.sitkLabelUInt64,
}

_itk_depth_dtype_table = {
    sitk.sitkInt8: np.int8,
    sitk.sitkUInt8: np.uint8,
    sitk.sitkInt16: np.int16,
    sitk.sitkUInt16: np.uint16,
    sitk.sitkInt32: np.int32,
    sitk.sitkUInt32: np.uint32,
    sitk.sitkInt64: np.int64,
    sitk.sitkUInt64: np.uint64,
    sitk.sitkFloat32: np.float32,
    sitk.sitkFloat64: np.float64,
    sitk.sitkLabelUInt8: np.uint8,
    sitk.sitkLabelUInt16: np.uint16,
    sitk.sitkLabelUInt32: np.uint32,
    sitk.sitkLabelUInt64: np.uint64,
}


def read(filename: str)->Tuple[np.ndarray, tuple]:
    """Read vtk and itk image

    Args:
        filename (str): A file name will be loaded.

    Returns:
        Tuple[np.ndarray, tuple]: Loaded image and image spacing.
    """

    itk_img = sitk.ReadImage(filename)
    img = np.array(sitk.GetArrayFromImage(itk_img),
                   _itk_depth_dtype_table[itk_img.GetPixelIDValue()])
    # img = np.transpose(img, (1, 2, 0))
    return img, itk_img.GetSpacing()


def write(filename: str, image: np.ndarray, spacing: tuple=None):
    """Write image by itk format

    Args:
        filename (str): A file name will be written.
        image (np.ndarray): An image will be written.
        spacing (tuple, optional): Defaults to None. A spacing of the image.
    """

    itk_img = None
    itk_img = sitk.GetImageFromArray(image)

    if spacing is not None:
        itk_img.SetSpacing(spacing)

    sitk.WriteImage(itk_img, filename, True)
