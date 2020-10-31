import inspect
import uuid
from typing import Dict


class Mappable:
    def __init__(self):
        self.mapping = {}

    def create_mapping(self):
        # do some magic to extract the constructor params
        caller_frame = inspect.stack()[1]
        arginfo = inspect.getargvalues(caller_frame[0])

        self.mapping = {arg: arginfo.locals[arg] for arg in arginfo.args if arg != 'self'}
        if arginfo.keywords is not None:
            self.mapping.update(arginfo.locals[arginfo.keywords])

        if "uuid" not in self.mapping:
            self.mapping["uuid"] = str(uuid.uuid4())

    def get_params(self) -> Dict:
        return self.mapping.copy()
