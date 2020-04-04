import abc


class PacketMeta(type):
    pass


class PacketBase(metaclass=PacketMeta):

    __scheme__ = None

    @abc.abstractmethod
    def build(self, seq: int, proto: int, code: int):
        ...


class Packet(PacketBase):
    def build(self, seq: int, proto: int, code: int):
        raise NotImplementedError
