class ProtocolBehavior:
    def request(self, send, packet):
        pass

    def response(self, data):
        pass

    def complete_condition(self):
        pass

    def cancel(self):
        pass
