class AperiodicResultException(Exception):
    def __init__(self, uuid: str, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.uuid = uuid
