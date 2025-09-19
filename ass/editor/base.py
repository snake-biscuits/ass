from __future__ import annotations
from collections import defaultdict
import math
from typing import Any, Dict, List

from .. import geometry
from .. import physics
from .. import texture
from .. import vector

import breki
from breki.files.parsed import parse_first


# TODO: Curve (CoDRadiant)
# TODO: Displacement (Source)
# TODO: Patch (IdTech 3)
# TODO: TriColl (Titanfall) [for MRVN-Radiant]
# NOTE: some TriColls are Displacements
# -- misc_model (embeds a model as bsp triangles) [lightmap & physics]
# -- .gltf? iirc Respawn builds terrain in Autodesk Maya [citation needed]


class Brush:
    sides: List[BrushSide]

    def __init__(self, sides=None):
        self.sides = sides if sides is not None else list()

    def __repr__(self) -> str:
        return f"<Brush {len(self.sides)} sides @ 0x{id(self):012X}>"

    def as_model(self) -> geometry.Model:
        # take a maximum bounds and slice it down plane by plane
        # BrushSide -> Polygon
        # a rotated cube wouldn't have polygons for it's axial faces
        # since those get sliced into nothing
        # but we'll need some floating point rounding magic to detect nothingness
        raise NotImplementedError()
        # AABB quads
        # slice edges w/ each non-axial plane
        # only respect in-bounds intersections
        # slice edge by replacing A-B w/ A-S;S-B if A & B on opposite sides
        # find the lerp(t) via plane.test(A) * -plane.normal
        # keep the inside (back), discard the outside (front)

    # TODO: catch bevel planes
    # -- found in Titanfall Engine trigger brushes
    # -- don't contribute to geometry, but helpful for physics calculations

    def as_physics(self) -> physics.Brush:
        # need to confirm brush is closed & convex
        # having vertices would make determining bounds easier
        raise NotImplementedError()
        out = physics.Brush()
        bounds = dict()
        for side in self.sides:
            normal = side.plane.normal.normalised()
            axes = {
                math.isclose(getattr(normal, axis), sign): (axis, sign)
                for axis in "xyz" for sign in (+1, -1)}
            if True in axes:  # plane is axial (axis aligned)
                # NOTE: do we need to invert plane distance to get bounds?
                bounds[axes[True]] = side.plane.distance
                out.axial_planes.append(side.plane)
            else:
                out.other_planes.append(side.plane)
            mins = vector.vec3(bounds.get((axis, -1), +math.inf) for axis in "xyz")
            maxs = vector.vec3(bounds.get((axis, +1), -math.inf) for axis in "xyz")
            out.bounds = physics.AABB.from_mins_maxs(mins, maxs)
        return out


class BrushSide:
    plane: physics.Plane = physics.Plane((0, 0, 1), 0)
    shader: str = "__TB_empty"
    texture_vector: texture.TextureVector
    # TODO: include rotation in texture.TextureVector
    texture_rotation: float = 0

    def __init__(self, plane=None, shader=None, texture_vector=None, rotation=None):
        self.plane = self.plane if plane is None else plane
        self.shader = self.shader if shader is None else shader
        if texture_vector is None:
            self.texture_vector = texture.TextureVector.from_normal(self.plane.normal)
        else:
            self.texture_vector = texture_vector
        self.texture_rotation = self.texture_rotation if rotation is None else rotation

    def __repr__(self) -> str:
        # TODO: kwargs for texture axis & rotation (if shorter)
        return f"BrushSide({self.plane!r}, {self.shader!r}, ...)"


class Entity:
    classname: str  # exposed from _keys
    # NOT KEYVALUES
    brushes: List[Brush]
    _keys: List[str]  # key-value pairs to write
    # NOTE: keys will be stored w/ setattr

    def __init__(self, **kwargs):
        self.brushes = list()
        self._keys = list()
        for key, value in kwargs.items():
            self[key] = value

    def __delitem__(self, key: str):
        assert key in self._keys, f'cannot delete key "{key}"'
        self._keys.remove(key)
        delattr(self, key)

    def __getitem__(self, key: str) -> str:
        return getattr(self, key)

    def __repr__(self) -> str:
        lines = [
            "{",
            *[f'"{k}" "{self[k]}"' for k in self._keys],
            f"...skipped {len(self.brushes)} brushes...",
            "}"]
        return "\n".join(lines)

    def __setitem__(self, key: str, value: str):
        assert key not in ("_keys", "brushes"), f'cannot set key "{key}"'
        self._keys.append(key)
        setattr(self, key, value)

    def __str__(self):
        lines = [
            "{",
            *[f'"{k}" "{self[k]}"' for k in self._keys],
            *map(str, self.brushes),
            "}"]
        return "\n".join(lines)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class MapFile(breki.ParsedFile):
    comments: Dict[int, str]
    # ^ {line_no: "comment"}
    entities: List[Entity]
    worldspawn: Entity = property(lambda s: s.entities[0])

    def __init__(self, filepath: str, archive=None, code_page=None):
        super().__init__(filepath, archive, code_page)
        self.comments = dict()
        self.entities = list()

    @parse_first
    def __repr__(self) -> str:
        descriptor = f'"{self.filename}" {len(self.entities)} entities'
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @parse_first
    def search(self, **search: Dict[str, str]) -> List[Entity]:
        """Search for entities by key-values; e.g. .search(key=value) -> [{"key": value, ...}, ...]"""
        return [
            entity
            for entity in self.entities
            if all([
                entity.get(key, "") == value
                for key, value in search.items()])]

    @parse_first
    def entities_by_classname(self) -> Dict[str, List[Entity]]:
        out = defaultdict(str)
        for entity in self.entities:
            out[entity.classname].append(entity)
        return dict(out)

    @classmethod
    def from_entities(cls, filepath: str, entities: List[Entity]) -> MapFile:
        out = cls(filepath)
        out.entities = entities
        out.is_parsed = True
        return out
