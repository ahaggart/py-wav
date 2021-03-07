from Signal import Signal


class SignalProvider:
    def get_signal(self) -> Signal:
        raise NotImplementedError
