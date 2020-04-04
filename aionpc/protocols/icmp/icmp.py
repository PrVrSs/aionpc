from .constants import PROTOCOL_NAME
from .protocol import Protocol
from .printer import EchoRequestPrinter
from ...protocol import BaseProtocol


class ICMP(BaseProtocol, name=PROTOCOL_NAME):
    def __init__(self, host):
        self.printer = EchoRequestPrinter(host=host)
        self.protocol = Protocol()
        self._config = None
