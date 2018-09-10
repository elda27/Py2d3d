import cv2
from metric.metric import Metric


class ContourDistance(Metric):
    def __init__(self, contour_extraction='canny', extraction_args=None):
        if contour_extraction == 'canny':
            cv2.Canny()

    def serialize_config(self):
        return {

        }

    def load_config(self, config):
        for key, value in config.items():
            setattr(self, key, value)
