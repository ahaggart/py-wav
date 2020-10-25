from typing import List
from sources.Source import Source
from sources.aggregations.AdditiveSource import AdditiveSource

class SequentialSource(AdditiveSource):
    def __init__(self, children: List[Source]=None):
        AdditiveSource.__init__(self, None)
        if children is not None:
            acc = 0
            for child in children:
                self.with_source(acc, child)
                acc += child.get_duration()