from SourceState import SourceState
from mapper.Mappable import Mappable
from mapper.mapper import tree_print


class Stateful(Mappable):
    def __init__(self):
        Mappable.__init__(self)
        self.create_mapping()
        self.state = SourceState()

    def get_state(self):
        return self.state

    def set_state(self, state: SourceState):
        self.state = state.with_depth(state.depth + 1)

        type_name = self.mapping['type']

        tree_print(f"Type: {type_name}", self.state.depth)
        tree_print(f"| dilation: {self.state.dilation_factor}", self.state.depth)
        tree_print(f"| offset: {self.state.offset}", self.state.depth)
