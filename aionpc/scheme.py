from ctypes import Structure
from typing import Tuple


_special: Tuple[str, ...] = ('__module__', '__qualname__', '__annotations__')


class ProtocolSchemeMeta(type):
    def __new__(mcs, typename, bases, ns):
        if ns.get('_root', False):
            return super().__new__(mcs, typename, bases, ns)

        fields = [
            (key, value, ns[key])
            if key in ns
            else (key, value)
            for key, value in ns.get('__annotations__', {}).items()
        ]

        structure = type(typename, (Structure,), {'_fields_': fields})

        for key in ns:
            if key not in _special and key not in ns.get('__annotations__', {}):
                setattr(structure, key, ns[key])

        return structure


class ProtocolScheme(metaclass=ProtocolSchemeMeta):
    _root = True

    from_buffer = ...
    from_buffer_copy = ...
