import re
from typing import Dict, List, Annotated, OrderedDict, parameter

from sphinx.util import tags

from ..metadata import Availability, Metadata, Parameter, Required

class OpengraphMetadata(Metadata):
    site_name: str
    page_url: parameter(str, tags=("og:url"))
    title: parameter(str, tags=("og:title"))
    description: parameter(str, tags=("og:description"))
    image: parameter(str, tags=("og:image"))
    image_alt: parameter(str, tags=("og:image:alt"))

    image_alt: Annotated[str, "", None, Required.OPTIONAL, ("og:image:alt"), Availability.GLOBAL]

    type: parameter(str, "type of the page", "website", tags=("og:type"))

    @staticmethod
    def render_one(prop: str, content: str) -> str:
        return f'<meta property="{prop}" content="{content}" />'

    def render(self) -> List[str]:
        ret = []
        if self.type: ret += [self.render_one("og:type", self.type)]
        if self.site_name: ret += [self.render_one("og:site_name", self.site_name)]
        if self.page_url: ret += [self.render_one("og:url", self.page_url)]
        if self.title: ret += [self.render_one("og:title", self.title)]
        if self.description: ret += [self.render_one("og:description", self.description)]
        if self.image: ret += [self.render_one("og:image", self.image)]
        if self.image_alt: ret += [self.render_one("og:image:alt", self.image_alt)]

        for tag, value in self.custom_tags.items():
            if not tag.startswith("og:"):
                continue
            ret += [self.render_one(tag, value)]

        return ret
