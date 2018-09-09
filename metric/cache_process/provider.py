from metric.cache_process.image import Image


class Provider:
    def __init__(self):
        self.caches = {}

    def clear(self):
        self.caches = {}

    def provide(self, image):
        img = Image(image)
        self.caches[id(image)] = img
        return img
