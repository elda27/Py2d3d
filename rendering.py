import os
import os.path
import argparse

import vtk
import numpy as np

import render


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', type=str,
                        required=True, help='Model filename')
    parser.add_argument('-s', '--shape', type=int, nargs=2, default=None,
                        help='Input image shape')
    parser.add_argument('-c', '--camera', type=str, default=None,
                        help='Camera configuraiton.')
    args = parser.parse_args()

    # Load statistical model
    model = np.load(args.model)[()]

    # Load camera parameters
    camera = None
    if args.camera is not None:
        geometry = render.GeometryContext.load_from_file(args.camera)
    else:
        geometry = render.GeometryContext()
        geometry.SOD = 1200
        geometry.SDD = 1100

    if args.shape is not None:
        geometry.image_size = args.shape

    renderer = render.SurfaceRenderer(False)
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderer.render_window)

    faces = model['faces']
    means = model['mean'].reshape(model['n_point'], model['n_dim'])

    model_center = np.mean(means, axis=0)
    means -= np.repeat(model_center[np.newaxis, :], means.shape[0], axis=0)

    interactor.Initialize()
    renderer.setup_render()

    renderer.render((means, faces))
    axes = vtk.vtkAxesActor()
    axes.SetTotalLength(100, 100, 100)
    renderer.renderer.AddActor(axes)

    renderer.renderer.ResetCamera()
    renderer.set_camera_parameter(geometry)
    renderer.flush()

    interactor.Start()


if __name__ == '__main__':
    main()
