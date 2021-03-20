from Signal import Signal


class SignalProvider:
    def get_signal(self, uuid: str) -> Signal:
        raise NotImplementedError
