from typing import List, Annotated

from ..metadata import Metadata, parameter

class DiscordMetadata(Metadata):
    REQUIRES = ["opengraph"]
    accent_color: parameter(str, "Color of the sidebar", tags=("theme-color"))

    def render(self) -> List[str]:
        ret = []
        if self.accent_color:
            ret += [f'<meta name="theme-color" content="{self.accent_color}">']

        return ret
