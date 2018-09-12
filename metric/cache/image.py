from metric.cache.invoke_cache_list import InvokeCacheList
import pycuda.gpuarray as gpuarray


def to_gpu(image):
    return gpuarray.to_gpu(image.astype(np.float32))


class Image:
    def __init__(self, image):
        self.image = image
        self.cache = {}

    def get_array(self):
        return self.image

    def process(self, function, *args, **kwargs):
        id_proc = id(function)
        arg_pair = (args, kwargs)
        if id_proc in self.cache and arg_pair in self.cache:
            return self.cache[id_proc][arg_pair]

        processed = function(self.image, *args, **kwargs)
        self.cache[id_proc] = InvokeCacheList()
        self.cache[id_proc][arg_pair] = processed

        return Image(processed)

    def to_pycuda(self):
        return self.process(to_gpu, self.image)
