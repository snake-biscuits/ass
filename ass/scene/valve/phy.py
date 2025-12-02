# Source SDK 2013 public/src/phyfile.h
# https://developer.valvesoftware.com/wiki/PHY
from __future__ import annotations
from typing import List

from ... import vector

import breki
from breki import core


class PhyHeader(core.Struct):
    __slots__ = ["size", "unknown", "num_solids", "checksum"]
    _format = "4I"


class SurfaceHeader(core.Struct):
    """compactsurfaceheader_t"""
    size: int  # ???
    magic: bytes  # b"VPHY"
    __slots__ = [
        "size", "magic", "version", "model_type",
        "surface_size", "drag_axis_areas", "axis_map_size"]
    _format = "I4s2HI3fI"
    _arrays = {"drag_axis_areas": [*"xyz"]}
    _classes = {"drag_axis_areas": vector.vec3}
    # TODO: ModelType enum


class LegacyHeader(core.Struct):
    """legacysurfaceheader_t"""
    size: int  # ???
    magic: bytes  # b"IVPS" or b"\0\0\0\0"
    __slots__ = [
        "size", "center_of_mass", "rotation_inertia", "radius", "bitfield",
        "offset_ledgetree_root", "unknown_1", "magic", "unknown_2"]
    _format = "I7f3I4sI"
    _arrays = {
        "center_of_mass": [*"xyz"],
        "rotation_inertia": [*"xyz"]}
    _bitfields = {
        "bitfield": {"max_deviation": 8, "byte_size": 24}}
    _classes = {
        "center_of_mass": vector.vec3,
        "rotation_inertia": vector.vec3}
    data: bytes  # ???


class Solid:
    header: SurfaceHeader
    legacy: LegacyHeader
    # TODO: data
    ...

    @classmethod
    def from_stream(cls, stream) -> Solid:
        out = cls()
        out.header = SurfaceHeader.from_stream(stream)
        assert out.header.magic == b"VPHY"
        out.legacy = LegacyHeader.from_stream(stream)
        assert out.legacy.magic in (b"IVPS", b"\0\0\0\0")
        # TODO: data
        ...
        return out


class Phy(breki.BinaryFile):
    header: PhyHeader
    solids: List[Solid]
    # script: str

    def __init__(self, filepath: str, archive=None, code_page=None):
        super().__init__(filepath, archive, code_page)
        self.header = None
        self.solids = list()
        # self.script = ""

    def parse(self):
        if self.is_parsed:
            return
        self.is_parsed = True
        self.header = PhyHeader.from_stream(self.stream)
        assert self.header.size == 16

        self.solids = [
            Solid.from_stream(self.stream)
            for i in range(self.header.num_solids)]

        # self.script = self.code_page.decode(self.stream.read())
