from functools import update_wrapper, partial


class pretty_printer:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, user_function):
        wrapper = partial(self._decorator, user_function)
        return update_wrapper(wrapper, user_function)

    async def _decorator(self, function, *args, **kwargs):
        async for response in function(*args, **kwargs):
            yield response


class pretty_printer2:
    def __init__(self, user_function):
        self._function = user_function

    def __get__(self, instance, owner):
        return partial(self, instance)

    def __call__(self, *args, **kwargs):
        return self._decorator(*args, **kwargs)

    async def _decorator(self, *args, **kwargs):
        async for response in self._function(*args, **kwargs):
            yield response
