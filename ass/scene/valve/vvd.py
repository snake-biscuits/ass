# using .bt (010 Hex Binary Template) reversed by MasterLiberty & others
# Source SDK 2013 public/src/studio.h
# snake-biscuits/titanfall2_mdl_converter (private, incomplete)
# headassbtw/mdlshit (mostly complete, no structs)
from typing import List

from ... import vector

import breki
from breki import core


# max_lods = 8
# max_bones_per_vertex = 3
class VvdHeader(core.Struct):
    __slots__ = [
        "magic", "version", "checksum",
        "num_lods", "num_lod_vertices",
        "num_fixups", "fixup_index",
        "vertex_index", "tangent_index"]
    _format = "4s15I"
    _arrays = {"num_lod_vertices": 8}


class Fixup(core.Struct):
    lod: int  # "used to skip culled root lod"?
    source_vertex_id: int
    num_vertices: int
    __slots__ = ["lod", "source_vertex_id", "num_vertices"]
    _format = "3I"


class Vertex(core.Struct):
    __slots__ = ["weights", "position", "normal", "uv"]
    _format = "3f4B8f"
    _arrays = {
        "weights": {"weight": 3, "bone": 3, "num_bones": None},
        "position": [*"xyz"],
        "normal": [*"xyz"],
        "uv": [*"xy"]}
    _classes = {
        "position": vector.vec3,
        "normal": vector.vec3,
        "uv": vector.vec2}


class Vvd(breki.BinaryFile):
    header: VvdHeader
    lod: List[List[Vertex]]

    def parse(self):
        if self.is_parsed:
            return
        self.is_parsed = True
        self.header = VvdHeader.from_stream(self.stream)
        assert self.header.magic == b"IDSV"
        assert self.header.version == 4

        assert self.header.num_lods >= 1
        # LoD 0 should have the most vertices
        for i in range(self.header.num_lods):
            a = self.header.num_lod_vertices[i]
            b = self.header.num_lod_vertices[i + 1] if i < 8 else 0
            assert a >= b, f"LoD {i} isn't lower detail"

        self.stream.seek(self.header.vertex_index)
        self.vertices = [
            Vertex.from_stream(self.stream)
            for i in range(self.header.num_lod_vertices[0])]
