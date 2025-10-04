# https://openusd.org/release/glossary.html
from __future__ import annotations
import collections
import re
from typing import Any, Dict, Generator, List

from .. import geometry
from .. import vector
from . import base

import breki
from breki.files.parsed import parse_first


reference_pattern = re.compile(r"@.*@(<.*>)?|<.*>")


# TODO: could we replicate material paths?
# -- how would blender interpret them?
def sanitise(material_name: str) -> str:
    material_name = material_name.replace("\\", "/")
    for bad_char in ".{}-":
        material_name = material_name.replace(bad_char, "_")
    return material_name.rpartition("/")[-1] if "/" in material_name else material_name


def usd_repr(value: Any) -> str:
    # NOTE: assumes lists of vectors will be converted beforehand
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        values = ", ".join(f'"{sanitise(v)}"' for v in value)
        return f"[{values}]"
    elif isinstance(value, str):
        if reference_pattern.fullmatch(value) is not None:
            return value
        else:
            return f'"{sanitise(value)}"'
    elif isinstance(value, (vector.vec2, vector.vec3)):
        return repr(tuple(value))
    else:
        return repr(value)


class Prim:
    """USD Data Node"""
    type_: str
    name: str
    metadata: Dict[str, Any]
    properties: List[Property]
    children: List[Prim]

    def __init__(self, type_, name, metadata={}, properties=[], children=[]):
        self.type_ = type_
        self.name = name
        self.metadata = metadata
        self.properties = properties
        self.children = children

    def __repr__(self) -> str:
        descriptor = f'{self.type_} "{self.name}"'
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def as_lines(self) -> Generator[str, None, None]:
        # NOTE: "def" is only one specifier
        # -- but we haven't needed "over" or "class" yet
        if len(self.metadata) > 0:
            yield f'def {self.type_} "{self.name}" ('
            for name, value in self.metadata.items():
                yield f"    {name} = {usd_repr(value)}"
            yield ")"
        else:
            yield f'def {self.type_} "{self.name}"'
        yield "{"
        for property_ in self.properties:
            for line in property_.as_lines():
                yield f"    {line}"
        if len(self.properties) > 0 and len(self.children) > 0:
            yield ""  # newline
        for i, child in enumerate(self.children):
            if i > 0:
                yield ""  # newline
            for line in child.as_lines():
                yield f"    {line}" if line != "" else ""
        yield "}"

    @classmethod
    def from_lines(cls, lines: List[str]) -> Prim:
        raise NotImplementedError()
        # get type_ & name from header
        # get metadata
        # get properties
        # get child prim(s)
        # return cls(type_, name, metadata, properties, children)


class Property:
    type_: str
    name: str
    value: Any
    metadata: Dict[str, Any]

    def __init__(self, type_, name, value, **metadata):
        self.type_ = type_
        self.name = name
        self.value = value
        self.metadata = metadata

    def __repr__(self) -> str:
        if len(self.metadata) == 0:
            return f'Property("{self.type_}", "{self.name}", {usd_repr(self.value)})'
        metadata = ", ".join(f"{name}={value!r}" for name, value in self.metadata.items())
        return f'Property("{self.type_}", "{self.name}", {usd_repr(self.value)}, {metadata})'

    def as_lines(self) -> Generator[str, None, None]:
        value = list(map(tuple, self.value)) if self.type_[-4:] in ("2f[]", "3f[]") else self.value
        if len(self.metadata) > 0:
            yield f"{self.type_} {self.name} = {usd_repr(value)} ("
            for name, value in self.metadata.items():
                yield f"    {name} = {usd_repr(value)}"
            yield ")"
        else:
            yield f"{self.type_} {self.name} = {usd_repr(value)}"

    @classmethod
    def from_lines(cls, lines: List[str]) -> Property:
        raise NotImplementedError()
        # get type_, name & value
        # get metadata (if any)
        # return cls(type_, name, value, metadata)


# TODO: friend_patterns for textures & sub-models
class Usd(base.SceneDescription, breki.FriendlyHybridFile):
    """Pixar's Universal Scene Description format"""
    exts = {
        "*.usd": breki.DataType.EITHER,
        "*.usda": breki.DataType.TEXT,
        "*.usdc": breki.DataType.BINARY}
    # NOTE: use .from_archive to load `.usdz`
    models: Dict[str, geometry.Model]
    metadata: Dict[str, Any]
    prims: List[Prim]

    def __init__(self, filepath: str, archive=None, code_page=None):
        super().__init__(filepath, archive, code_page)
        self.metadata = dict(
            defaultPrim="root",
            metersPerUnit=0.0254,  # inches
            upAxis="Z")
        self.prims = list()

    as_bytes = breki.ParsedFile.as_bytes

    @parse_first
    def as_lines(self) -> List[str]:
        # generate prims if none exist & have models
        if len(self.prims) == 0 and len(self.models) > 0:
            self.regenerate_prims()
        out = list()
        # metadata
        out.extend([
            "#usda 1.0",
            "("])
        out.extend([
            f"    {name} = {usd_repr(value)}"
            for name, value in self.metadata.items()])
        out.append(")")
        # prims
        for i, prim in enumerate(self.prims):
            out.append("")  # newline
            out.extend(prim.as_lines())
        return out

    @classmethod
    def identify(cls, filepath: str, stream: base.ByteStream) -> base.DataType:
        type_ = super().identify(filepath, stream)
        if type_ == breki.DataType.EITHER:
            stream.seek(0)
            magic = stream.read(8)
            if magic == b"PXR-USDC":
                type_ = breki.DataType.BINARY
            elif magic[:4] == b"PK\x03\x04":
                raise RuntimeError(
                    "cannot open .usdz directly; use .from_archive() instead")
            else:  # most likely usda
                type_ = breki.DataType.TEXT
        return type_

    def parse_binary(self):
        if self.is_parsed:
            return
        self.is_parsed = True
        magic = self.stream.read(8)
        assert magic == b"PXR-USDC"
        unknown, lump_headers_offset = breki.read_struct(self.stream, "2Q")
        assert lump_headers_offset < self.size
        self.stream.seek(lump_headers_offset)
        num_lump_headers = breki.read_struct(self.stream, "Q")
        self.lump_headers = dict()
        for i in range(num_lump_headers):
            name, offset, length = breki.read_struct(self.stream, "16s2Q")
            name = name.rstrip(b"\x00").decode(*self.code_page)
            self.lump_headers[name] = (offset, length)
            print(f"{name:<16s} | {offset=}, {length=}")
        # lazy mount lumps
        for name, (offset, length) in self.lump_headers.items():
            self.stream.seek(offset)
            setattr(self, name, self.stream.read(length))
        # raise NotImplementedError()

    # TODO: material variants based on lightmap & cubemap indices (titanfall2)
    # -- could maybe do per-polygon attributes to encode this
    # TODO: catch duplicate material names ('Duplicate prim' will not load)
    def regenerate_prims(self):
        """build self.prims from self.models"""
        # translate models
        model_prims = list()
        for model_name, model in self.models.items():
            material_polygons = collections.defaultdict(list)
            # ^ {Material: [Polygon]}
            for mesh in model.meshes:
                material_polygons[mesh.material].extend(mesh.polygons)
            # core mesh properties
            face_lengths = [
                len(polygon.vertices)
                for polygons in material_polygons.values()
                for polygon in polygons]
            vertices = [
                vertex
                for polygons in material_polygons.values()
                for polygon in polygons
                for vertex in reversed(polygon.vertices)]
            # NOTE: crazy inefficient, but splitting models sucks
            uvs = [
                [
                    tuple(vertex.uv[i]) if i < len(vertex.uv) else (0, 0)
                    for vertex in vertices]
                for i in range(max(len(vertex.uv) for vertex in vertices))]
            # material binding spans
            start = 0
            material_bindings = list()
            for material, polygons in material_polygons.items():
                material_bindings.append(Prim(
                    "GeomSubset", sanitise(material.name),
                    metadata={
                        "prepend apiSchemas": ["MaterialBindingAPI"]},
                    properties=[
                        Property("uniform token", "elementType", "face"),
                        Property("uniform token", "familyName", "materialBind"),
                        Property("int[]", "indices", [*range(start, start + len(polygons))]),
                        Property("rel", "material:binding", f"</_materials/{sanitise(material.name)}>")]))
                start += len(polygons)
            # model prim
            model_prims.append(Prim(
                "Xform", model_name,
                properties=[
                    Property("float3", "xformOp:rotateXYZ", model.angles),
                    Property("float3", "xformOp:scale", model.scale),
                    Property("double3", "xformOp:translate", model.origin),
                    Property("uniform token[]", "xformOpOrder", [
                        "xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"])],
                children=[
                    Prim(
                        "Mesh", model_name,
                        metadata={
                            "prepend apiSchemas": ["MaterialBindingAPI"]},
                        properties=[
                            Property("int[]", "faceVertexCounts", face_lengths),
                            Property("int[]", "faceVertexIndices", [*range(sum(face_lengths))]),
                            Property("point3f[]", "points", [vertex.position for vertex in vertices]),
                            Property("normal3f[]", "normals", [vertex.normal for vertex in vertices]),
                            *[
                                Property("texCoord2f[]", f"primvars:uv{i}", uv_layer, interpolation="faceVarying")
                                for i, uv_layer in enumerate(uvs)],
                            Property("color3f[]", "primvars:displayColor", [
                                tuple(vertex.colour[:3]) for vertex in vertices],
                                interpolation="vertex"),
                            Property("float[]", "primvars:displayOpacity", [
                                1 - (vertex.colour[3] / 255)
                                for vertex in vertices],
                                interpolation="vertex")],
                        children=material_bindings)]))
        # material prims
        materials = {
                mesh.material
                for model in self.models.values()
                for mesh in model.meshes}
        # TODO: try replicating the material folder structure
        material_prims = [
            Prim("Material", sanitise(material.name))
            for material in sorted(materials, key=lambda m: m.name)]
        # TODO: construct a material users can plug textures into
        # -- will require parsing .vmt, .rpak & .vpk
        # root prim
        root = Prim("Xform", "root", children=[
            *model_prims,
            Prim("Scope", "_materials", children=[
                *material_prims])])
        self.prims = [root]
