
class Image:
    def __init__(self, image):
        self.image = image
        self.cache = {}

    def get_array(self):
        return self.image

    def process(self, function, *args, **kwargs):
        id_proc = id(function)
        if id_proc in self.cache:
            return self.cache[id_proc]

        processed = function(self.image, *args, **kwargs)
        self.cache[id_proc] = processed

        return processed
