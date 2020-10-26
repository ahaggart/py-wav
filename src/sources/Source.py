class Source:
    def get_buffer(self, fs):
        raise NotImplementedError

    def get_duration(self, fs) -> int:
        raise NotImplementedError
