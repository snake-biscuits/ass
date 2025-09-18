from __future__ import annotations
from typing import Dict, List, Union

from .. import geometry

import breki
from breki.files.parsed import parse_first


ModelList = Union[
    List[geometry.Model],
    Dict[str, geometry.Model]]


def indent(count: int = 1) -> str:
    return " " * 4 * count  # 4 spaces, no tabs


# NOTE: wavefront.Obj uses groups instead of models
# -- Gltf & Usd have nodes / node trees (indexed relationships)
# -- might need to rethink how we represent model names
# -- copying data for every instance seems like a bad idea
class SceneDescription(breki.ParsedFile):
    """base class for file formats containing multiple models etc."""
    # NOTE: formats can be lossy, reloading a saved file could result in data loss
    # -- but some formats will also contain data which we totally ignore
    models: Dict[str, geometry.Model]

    def __init__(self, filepath: str, archive=None, code_page=None):
        super().__init__(filepath, archive, code_page)
        self.models = dict()

    @parse_first
    def __repr__(self) -> str:
        descriptor = f'"{self.filename}" {len(self.models)} models'
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @classmethod
    def from_models(cls, filepath: str, models: ModelList) -> SceneDescription:
        out = cls(filepath)
        if isinstance(models, (list, tuple, set)):
            models = {
                f"model_{i:03d}": model
                for i, model in enumerate(models)}
        assert isinstance(models, dict), "'models' must be a ModelList!"
        out.models = models
        out.is_parsed = True
        return out
