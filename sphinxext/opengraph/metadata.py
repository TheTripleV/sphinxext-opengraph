from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Annotated, Any, Callable, Dict, Iterable, List, OrderedDict, Union
# from docutils.nodes import nodes
# from sphinx.application import Sphinx
from dataclasses import dataclass
from enum import Enum

class Required(Enum):
    REQUIRED = 1
    RECOMMENDED = 2
    OPTIONAL = 3
    NOT_RECOMMENDED = 4

    def __and__(self, other):
        if self.value < other.value:
            return self
        return other

class Availability(Enum):
    NONE = 1
    PAGE = 2
    GLOBAL = 3

    def __and__(self, other):
        if self.value < other.value:
            return self
        return other

def parameter(
    type: Any,
    description: str = "",
    default: Any = None,
    required: Required = Required.OPTIONAL,
    tags: tuple[str] = (),
    availability: Availability = Availability.GLOBAL,
):
    return Annotated[type, description, default, required, tags, availability]

class Metadata(ABC):
    def __init__(self, common: "Common", page_overrides: Dict[str, str], custom_tags: OrderedDict[str, str], **others):
        self.custom_tags = deepcopy(custom_tags)
        
        for name in self.__annotations__:
            # Inject from common
            if name in common.__annotations__:
                setattr(self, name, getattr(common, name))
            # Inject from variable overrides
            overrides = {**page_overrides, **others}
            if name in overrides:
                setattr(self, name, overrides[name])
            # Inject from tag overrides
            annotation = self.__annotations__[name]
            if isinstance(annotation, Annotated):
                tags = annotation.__args__[-1]
                if isinstance(tags, (tuple, list)):
                    for tag in tags:
                        if tag in self.custom_tags:
                            setattr(self, name, self.custom_tags[tag])
                            del self.custom_tags[tag]
            # Set else to none
            if not hasattr(self, name):
                setattr(self, name, None)

        self.fill()

    def get_default(self, name: str) -> Any:
        if name not in self.__annotations__:
            return None
        return self.__annotations__["description_length"].__args__[1]

    def fill(self) -> None:
        pass

    @abstractmethod
    def render(self) -> List[str]:
        pass