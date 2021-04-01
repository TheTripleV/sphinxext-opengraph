from typing import List, Annotated

from ..metadata import Metadata, parameter

class FacebookMetadata(Metadata):
    REQUIRES =  ["opengraph"]
    app_id: parameter(str, "app ID of a facebook page.", tags=("fb:app_id"))

    @staticmethod
    def render_one(prop: str, content: str) -> str:
        return f'<meta property="{prop}" content="{content}" />'

    def render(self) -> List[str]:
        ret = []
        if self.app_id: ret += [self.render_one("fb:app_id", self.app_id)]

        for tag, value in self.custom_tags.items():
            if not tag.startswith("fb:"):
                continue
            ret += [self.render_one(tag, value)]

        return ret
