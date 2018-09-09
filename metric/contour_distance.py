import cv2
from metric.metric import Metric


class ContourDistance(Metric):
    def __init__(self, extraction_method='canny'):

    def serialize_config(self):
        return {

        }

    def load_config(self, config):
        for key, value in config.items():
            setattr(self, key, value)
