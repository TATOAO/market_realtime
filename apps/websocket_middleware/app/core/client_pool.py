
class ClientBase():
    def __init__(self, host: str, subsription_limits: int):
        self.subsription_limits = subsription_limits
        self.host = 'http://127.0.0.1:11111'
