import os
import os.path
import argparse

import vtk
import numpy as np

import SimpleITK as sitk


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', type=str, nargs='+',
                        required=True, help='Model filename')
    parser.add_argument('--framework', type=str, nargs='+',
                        help='Registration framework.')
    parser.add_argument('-i', '--input', type=str, nargs='+'
                        required=True, help='Input image files')
    parser.add_argument('-c', '--camera', type=str, nargs='+',
                        required=True, help='Camera configuraiton.')
    args = parser.parse_args()

    # Load model
    model = np.load(args.model)[()]

    # Load camera parameters
    geometries = []
    for c in args.camera:
        geometries = render.GeometryContext.load_from_file(c)

    input_images = []
    for i in args.input:
        itk_image = sitk.ReadImage(i)
        sitk.itk_to
        spacing = itk_image.GetSpacing()


if __name__ == '__main__':
    main()
