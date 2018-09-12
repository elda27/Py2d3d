import cv2
import numpy as np
from metric.metric import Metric


class ContourDistance(Metric):
    def __init__(self, contour_extraction='canny', extraction_args=dict()):
        self.contour_extraction = contour_extraction
        self.extraction_args = extraction_args

    def calculate(self, image, model_image):
        return self.calculate_cpu(image, model_image)

    def calculate_cpu(self, image, model_image):
        image = self.provide(image)
        contour_image = image.process(
            self.contour_extraction, image, **self.extraction_args
        )

        model_silhouette = model_image > 0
        gx, gy = np.gradient(model_silhouette)
        model_contour = gx > 0 | gy > 0

        cxs, cys = np.nonzero(contour_image)
        mcxs, mcys = np.nonzero(model_contour)

        cxs = np.repeat(np.expand_dims(cxs, 1), (1, len(mcxs), 1))
        cys = np.repeat(np.expand_dims(cys, 1), (1, len(mcys), 1))

        mcxs = np.repeat(np.expand_dims(mcxs, 0), (len(cxs), 1, 1))
        mcys = np.repeat(np.expand_dims(mcys, 0), (len(cys), 1, 1))

        return np.sum(np.min((cxs - mcxs) ** 2 + (cys - mcys) ** 2, axis=0))

    def calculate_gpu(self, image, model_image):
        raise NotImplementedError()

    @property
    def contour_extraction(self):
        return self.contour_extraction_

    @contour_extraction.setter
    def contour_extraction(self, value):
        if isinstance(value, str):
            self.contour_extraction_name = value
            if value == 'canny':
                self.contour_extraction_ = cv2.Canny
            else:
                raise ValueError('Unknown contour extraciton type: ' + value)
        else:
            raise TypeError('Bad type:' + type(value))

    def serialize_config(self):
        return {
            'extraction_args': self.extraction_args,
            'contour_extraction': self.contour_extraction_name,
        }

    def load_config(self, config):
        for key, value in config.items():
            setattr(self, key, value)
