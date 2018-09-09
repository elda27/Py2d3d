

registered_metrics = {}


def register_metric(name):
    def _register_metric(klass):
        registered_metrics[name] = klass
        return klass
    return _register_metric


def make_metric(name, *args, **kwargs):
    return registered_metrics[name](*args, **kwargs)
