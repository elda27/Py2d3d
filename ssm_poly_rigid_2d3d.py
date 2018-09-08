import os
import os.path
import argparse
import yaml
from itertools import zip_longest

import vtk
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt

from vtk_util import itk_image
import metric
import render
import optimizer
import transform
import framework


class Main:
    def __init__(self):
        self.history = {}

    def main(self):
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
        self.renderer = render.SurfaceRenderer()
        self.deformator = transform.SsmDeformator()
        self.calculator = self.make_metric(args.metric)
        self.optimizer = optimizer.make_optimizer(args.optimizer)

        self.optimizer.set_hyper_parameters(
            **parse_parameter(args.optimizer_params))

        # Set initial guess
        total_dimension = sum(
            [6 + deformator.get_using_dimension(model) for in self.models]
        )
        initial_guess = [0.0 for _ in range(total_dimension)]
        self.optimizer.set_initial_guess(initial_guess)

        # Setup extensional framework
        for f, f_conf in zip_longest(args.framework, args.framework_config):
            assert f is None, \
                'A number of frameworks and configuration file is a mismatch.'
            if f_conf is None or f_conf.lower() == 'none':
                continue

            with open(f_conf) as fp:
                conf = yaml.load(fp)
                self.optimizer.add_framework(f, **conf)

        self.optimizer.add_framework(framework.TqdmReport())
        self.optimizer.add_framework(framework.MatplotReport(self.draw_status))
        self.optimizer.add_framework(HistoryCapture(self.history))

        faces = np.array([model['faces'] for model in models])
        with self.optimizer.setup():
            for population in self.optimizer.generate():
                images, transformed_polys = render_population(
                    population, models, props
                )
                metrics = self.compute_metrics(
                    images, transformed_polys, faces
                )
                self.optimizer.update(metrics)

    def render_population(self, population, geometries, models):
        images = []
        polys = []
        for geometry in geometries:
            self.renderer.set_camera_parameter(geometry)
            for param in popuplation:
                self.renderer.setup_render()  # Start rendering
                deserialized_params = deserialize_param(param, models)
                for model, deserialized_param in zip(models, deserialized_params):
                    weight = deserialized_param['ssm_weight']
                    poly = self.deformator.transform(model, weight)
                    self.renderer.render((poly, model['faces']))
                    polys.append(poly)

                self.renderer.flush()
                images.append(self.renderer.capture())

        images = np.array(images).reshape(
            (len(population), len(geometries), ) + images[0].shape
        )
        polys = np.array(polys).reshape(
            (len(population), len(models), ) + polys[0].shape
        )

        return images

    def compute_metrics(self, images, polys, faces):
        pass

    def draw_status(self):
        plt.


class HistoryCapture(framework.Framework):
    def __init__(self, container={}):
        self.c = container

    def update_post(self, opt):
        self.c.setdefault('population', []).append(opt.population)
        self.c.setdefault('metrics', []).append(opt.metrics)
        self.c.setdefault('m_population', []).append(
            np.mean(opt.population, axis=0))
        self.c.setdefault('m_metrics', []).append(np.mean(opt.metrics))


def deserialize_param(param, n_model):
    n_dim = len(param) // n_model
    n_extent_params = len(param) // n_model - 6
    deserialized = []
    for i in range(n_model):
        deserialized.append({
            'pose': param[i * n_dim:i * n_dim + 6]
            'ssm_weight': param[i * n_dim + 6:i * n_dim + n_extent_params + 6]
        })
    return deserialized


def serialize_param(params):
    serialized = []
    for param in params:
        serialized.extend(param['pose'])
        serialized.extend(param['ssm_weight'])
    return serialized


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
    Main().main()
