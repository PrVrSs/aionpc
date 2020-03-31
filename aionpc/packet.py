import abc


class PacketMeta(type):
    pass


class PacketBase(metaclass=PacketMeta):

    __scheme__ = None

    @abc.abstractmethod
    def build(self, seq): ...


class Packet(PacketBase):
    def build(self, seq):
        raise NotImplementedError
