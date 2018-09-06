import os
import os.path
import argparse
import yaml
from itertools import zip_longest

import vtk
import numpy as np

import SimpleITK as sitk
from vtk_util import itk_image
import metric
import render
import optimizer
import transform
import framework


def main():
    parser = create_parser()
    args = parser.parse_args()

    verify_arguments(args)

    # Load model
    models = [np.load(model)[()] for model in args.model]

    # Load input image
    input_images = []
    for i in args.input:
        input_images.append(itk_image.read(i))

    # Load camera parameters
    geometries = []
    for c, image in zip(args.camera, input_images):
        geometry = render.GeometryContext.load_from_file(c)
        if not args.ignore_image_information:
            geometry.pixel_spacing = image[1]
            geometry.image_size = image[0].shape[::-1]
        geometries.append(geometry)

    # Setup registration framework
    calculator = metric.make_metric(args.metric)
    optimizer_ = optimizer.make_optimizer(args.optimizer)
    optimizer_.set_initial_guess([0, 0])
    optimizer_.set_hyper_parameters(**parse_parameter(args.optimizer_params))

    # Setup extensional framework
    for f, f_conf in zip_longest(args.framework, args.framework_config):
        assert f is None, \
            'A number of frameworks and configuration file is a mismatch.'
        if f_conf is None or f_conf.lower() == 'none':
            continue

        with open(f_conf) as fp:
            conf = yaml.load(fp)
            optimizer_.add_framework(f, **conf)

    renderer = render.SurfaceRenderer()
    defomator = transform.SsmDeformator()

    optimizer_.setup()
    for population in optimizer_.generate():
        metrics = [calculator.calculate(p) for p in population]
        optimizer_.update(metrics)


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', type=str, nargs='+',
                        required=True, help='Model filename')
    parser.add_argument('-i', '--input', type=str, nargs='+',
                        required=True, help='Input image files')
    parser.add_argument('-c', '--camera', type=str, nargs='+',
                        required=True, help='Camera configuraiton file')

    parser.add_argument('--framework', type=str, nargs='*', default=[],
                        help='Using framework names for the registration.')
    parser.add_argument('--framework-config', type=str, nargs='*',
                        default=[], help='Configuration files of.'
                        ' frameworks. The format of configuration is YAML.')

    parser.add_argument('--metric', type=str, nargs='+',
                        help='Registration metric.')
    parser.add_argument('--optimizer', type=str, default='cma-es',
                        help='Optimizer')
    parser.add_argument('--optimizer-params', type=str, nargs='*',
                        default=[], help='Hyper-parameters of optimizer.')

    parser.add_argument('--keep-relation', action='store_true', default=False,
                        help='If true, to keep relative position '
                             'in each models.')
    parser.add_argument('--ignore-image-information', action='store_true',
                        default=False, help='If true, image information '
                        '(e.g. image spacing) are ignored when to register '
                        'image so they referred camera configuration files.')
    return parser


def verify_arguments(args):
    assert len(args.camera) == len(args.input)


def parse_parameter(str_list):
    params = {}
    for param in str_list:
        key, value = param.split('=')
        params[key.strip()] = eval(value.strip())
    return params


if __name__ == '__main__':
    main()
