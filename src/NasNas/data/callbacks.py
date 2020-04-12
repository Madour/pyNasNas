from functools import wraps


def callback(name):
    def decorator(method):
        @wraps(method)
        def wrapper(self, user_fn):
            self.callbacks.register(name, user_fn)
            return method(self, user_fn)
        return wrapper
    return decorator


class CallbackHandler:
    def __init__(self):
        self._callbacks = {}

    def register(self, name: str, function):
        self._callbacks[name] = function

    def call(self, name: str):
        if name in self._callbacks:
            self._callbacks[name]()


class HasCallbacks:
    def __init__(self, *args, **kwargs):
        # avoid blocking multiple inheritance by forwarding all arguments to super()
        super().__init__(*args, **kwargs)
        self._callbacks = CallbackHandler()

    @property
    def callbacks(self):
        return self._callbacks
