from typing import List, Annotated

from ..metadata import Metadata, parameter

class TwitterMetadata(Metadata):
    # from twitter's website
    MAX_DESCRIPTION_LENGTH = 200
    MAX_TITLE_LENGTH = 70
    MAX_IMAGE_ALT_LENGTH = 420

    title: parameter(str, tags=("twitter:title"))
    description: parameter(str, tags=("twitter:description"))
    image: parameter(str, tags=("twitter:image"))
    image_alt: parameter(str, ("twitter:image:alt"))

    card: parameter(str, "", "summary", tags=("twitter:card"))
    site: parameter(str, "", tags=("twitter:site"))
    site_id: parameter(str, "", tags=("twitter:site:id"))
    creator: parameter(str, "", tags=("twitter:creator"))
    creator_id: parameter(str, "", tags=("twitter:creator:id"))

    def fill(self) -> None:
        if self.description and len(self.description) > self.MAX_DESCRIPTION_LENGTH:
            self.description = self.description[:self.MAX_DESCRIPTION_LENGTH - 3] + "..."
        if self.title and len(self.title) > self.MAX_TITLE_LENGTH:
            self.title = self.title[:self.MAX_TITLE_LENGTH - 3] + "..."
        if self.image_alt and len(self.image_alt) > self.MAX_IMAGE_ALT_LENGTH:
            self.image_alt = self.image_alt[:self.MAX_IMAGE_ALT_LENGTH - 3] + "..."

    @staticmethod
    def render_one(name: str, content: str) -> str:
        return f'<meta name="{name}" content="{content}" />'

    def render(self) -> List[str]:
        ret = []
        if self.title: ret += [self.render_one("twitter:title", self.title)]
        if self.description: ret += [self.render_one("twitter:description", self.description)]
        if self.image: ret += [self.render_one("twitter:image", self.image)]
        if self.image_alt: ret += [self.render_one("twitter:image:alt", self.image_alt)]
        
        if self.card: ret += [self.render_one("twitter:card", self.card)]
        if self.site: ret += [self.render_one("twitter:site", self.site)]
        if self.site_id: ret += [self.render_one("twitter:site:id", self.site_id)]
        if self.creator: ret += [self.render_one("twitter:creator", self.creator)]
        if self.creator_id: ret += [self.render_one("twitter:creator:id", self.creator_id)]
        
        for tag, value in self.custom_tags.items():
            if not tag.startswith("twitter:"):
                continue
            ret += [self.render_one(tag, value)]
        
        return ret