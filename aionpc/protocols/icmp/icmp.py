from .constants import PROTOCOL_NAME
from .protocol import Protocol
from .printer import EchoRequestPrinter
from ...protocol import BaseProtocol


class ICMP(BaseProtocol, name=PROTOCOL_NAME):
    def __init__(self, config):
        self.printer = EchoRequestPrinter(config.get('host'))
        self.protocol = Protocol(config.get('host'))
        self._config = None
