from typing import List, Annotated

from ..metadata import Metadata, parameter

class MetaMetadata(Metadata):
    description: parameter(str, tags=("description"))

    def render(self) -> List[str]:
        ret = []
        if self.description: ret += [f'<meta name="description" content="{self.description}">']
        return ret