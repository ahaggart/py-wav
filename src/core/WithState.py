from SourceState import SourceState
from mapper.mapper import tree_print


class WithState:
    def __init__(self):
        self.state = SourceState()

    def get_state(self):
        return self.state

    def set_state(self, state: SourceState):
        self.state = state.with_depth(state.depth + 1)

        type_name = str(self.__class__.__name__)

        tree_print(f"Type: {type_name}", self.state.depth)
        tree_print(f"| dilation: {self.state.dilation_factor}", self.state.depth)
        tree_print(f"| offset: {self.state.offset}", self.state.depth)
