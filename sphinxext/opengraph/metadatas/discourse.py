from typing import List, Annotated

from ..metadata import Metadata, parameter

class DiscourseMetadata(Metadata):
    REQUIRES = ["opengraph"]
    ignore_canonical: parameter(bool, "whether Discourse ignore the canonical url and use the `page_url` for parsing opengraph data.", tags=("og:ignore_canonical"))

    @staticmethod
    def render_one(prop: str, content: str) -> str:
        return f'<meta property="{prop}" content="{content}" />'

    def render(self) -> List[str]:
        ret = []
        if self.ignore_canonical and "og:ignore_canonical" not in self.custom_tags: ret += [self.render_one("og:ignore_canonical", str(self.ignore_canonical))]
        return ret
        