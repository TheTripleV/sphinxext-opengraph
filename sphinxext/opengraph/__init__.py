from typing import Any, Dict
from .metadata import Metadata
from .metadatas.common import Common
from .metadatas.discord import DiscordMetadata
from .metadatas.discourse import DiscourseMetadata
from .metadatas.facebook import FacebookMetadata
from .metadatas.meta import MetaMetadata
from .metadatas.opengraph import OpengraphMetadata
from .metadatas.twitter import TwitterMetadata

from inspect import isclass
from copy import deepcopy

import os
from urllib.parse import urljoin, urlparse, urlunparse

from sphinx.application import Sphinx
import docutils.nodes as nodes

METADATAS = [DiscordMetadata, DiscourseMetadata, FacebookMetadata, MetaMetadata, OpengraphMetadata, TwitterMetadata]


class PrintTraceback:
    def __call__(self, func):
        def wrapper_func(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapper_func
    def __enter__(self): pass
    def __exit__(self, exc_type, exc_val, tb):
        if exc_type == None: return True
        import traceback
        print(f"\n{traceback.format_exc()}\n{exc_type.__name__}: {str(exc_val)}")

@PrintTraceback()
def get_clean_class_name(cls: "class"):
    return cls.__name__.replace("Metadata", "").lower()

@PrintTraceback()
def setup_rtd(app: Sphinx, config: Dict[str, Any]):
    ogp_config = config["ogp_config"]
    if os.getenv("READTHEDOCS") and "site_url" not in ogp_config:
        # readthedocs uses html_baseurl for sphinx > 1.8
        parse_result = urlparse(config["html_baseurl"])

        if config["html_baseurl"] is None:
            raise EnvironmentError("ReadTheDocs did not provide a valid canonical URL!")

        # Grab root url from canonical url
        ogp_config["site_url"] = urlunparse(
            (
                parse_result.scheme,
                parse_result.netloc,
                parse_result.path,
                "",
                "",
                "",
            )
        )

@PrintTraceback()
def setup_classes(app: Sphinx, config: Dict[str, Any]):
    config["ogp_config_classes"] = {get_clean_class_name(m):m for m in METADATAS}

    for metadata_cls in config["ogp_config"].get("metadatas", []):
        if isclass(metadata_cls):
            name = get_clean_class_name(metadata_cls)
            if name in config["ogp_config_classes"]:
                print("clash: A metadata class will be overwritten")
            config["ogp_config_classes"][name] = metadata_cls
    
@PrintTraceback()
def html_page_context(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: Dict[str, Any],
    doctree: nodes.document,
) -> None:
    if not doctree:
        return

    # Get page level overrides
    meta = context.get("meta") or {}
    ogp_meta_prefix = "ogp:"
    ogp_page_overrides = {k[len(ogp_meta_prefix):]:v for k,v in meta.items() if k.startswith(ogp_meta_prefix)}

    common_config = {k:v for k,v in ogp_page_overrides.items() if ":" not in k}
    
    ogp_config = deepcopy(app.config["ogp_config"])
    ogp_config.update(common_config)

    # Apply all user functions
    for key in ogp_config:
        if callable(ogp_config[key]):
            ogp_config[key] = ogp_config[key](app, pagename, templatename, context, doctree)

    common = Common(app, pagename, templatename, context, doctree, ogp_config)

    # Get Metadatas to Run
    desired_metadatas = ogp_config.get("metadatas", [])
    all_metadatas = app.config["ogp_config_classes"]
    metadatas: Dict[str, Metadata] = {}
    if desired_metadatas == "all" or "all" in desired_metadatas or not desired_metadatas:
        metadatas = all_metadatas
    elif isinstance(desired_metadatas, (tuple, list)):
            for metadata in metadatas:
                if isinstance(metadata, str) and metadata.lower() in all_metadatas:
                    m_name = metadata.lower()
                    metadatas[m_name] = all_metadatas[m_name]
                elif isclass(metadata):
                    m_name = get_clean_class_name(metadata)
                    metadatas[m_name] = all_metadatas[m_name]
    elif isinstance(desired_metadatas, str):
        for metadata in map(str.strip, metadatas.split(",")):
            m_name = metadata.lower()
            if m_name in all_metadatas:
                metadatas[m_name] = all_metadatas[m_name]

    metatags = []

    for m_name, m_cls in metadatas.items():
        for req in getattr(m_cls, "REQUIRES", []):
            if req.lower() not in metadatas:
                print(f"{m_name} depends on {req} but it has been excluded. Include {req} or uninclude {m_name}.")

    for m_name, m_cls in metadatas.items():

        ogp_config = deepcopy(app.config["ogp_config"])
        m_overrides = ogp_config.get(m_name, {})
        m_page_overrides = {k[len(m_name):]:v for k,v in ogp_page_overrides.items() if k.startswith(m_name)}
        m_page_tag_overrides = deepcopy(meta)

        ogp_config.update(m_overrides)
        ogp_config.update(m_page_overrides)

        # Apply all user functions
        for key in ogp_config:
            if callable(ogp_config[key]):
                ogp_config[key] = ogp_config[key](app, pagename, templatename, context, doctree)

        m = m_cls(common, ogp_config, m_page_tag_overrides, app=app, pagename=pagename, templatename=templatename, context=context, doctree=doctree)
        import code
        code.interact(local={**locals(), **globals()})

        metatags += m.render()


    context["metatags"] += "\n" + "\n".join(metatags) + "\n"


@PrintTraceback()
def setup(app: Sphinx) -> Dict[str, Any]:
    app.add_config_value("ogp_config", {"metadatas": ["all"]}, "html")

    app.connect("config-inited", setup_rtd)
    app.connect("config-inited", setup_classes)
    app.connect("html-page-context", html_page_context)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }