'''Event bus implementation'''

# https://stackoverflow.com/questions/1092531/event-system-in-python
class Bus(object):
    def __init__(self):
        self.__handlers = []

    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.__handlers.remove(handler)
        return self

    def fire(self, *args, **kwargs):
        for handler in self.__handlers:
            handler(*args, **kwargs)

    def clear_handlers(self, obj=None):
        for handler in self.__handlers:
            if not obj or handler.__self__ == obj:
                self -= handler

bus = Bus()