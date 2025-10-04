# R2Northstar/mods/Northstar.CustomServers/mod/maps/navmesh/mp_coliseum_small.nm
"""for r2recast .nm files (Titanfall 2 NPC Navigation Meshes)"""
from __future__ import annotations
import io
from typing import Dict, List, Tuple

from .. import geometry
from .. import vector
from . import base

import breki
from breki import binary
from breki import core
from breki.files.parsed import parse_first


class Params(core.MappedArray):
    _format = "5f5i"
    _mapping = {
        "origin": [*"xyz"],
        "tile_size": ["width", "height"],
        "max_tiles": None,
        "max_polygons": None,
        # "i hate this"
        "disjoint_polygon_group_count": None,
        "reachability_table": ["size", "count"]}
    _classes = {
        "origin": vector.vec3}


class FileHeader(core.Struct):
    magic: bytes  # b"TESM" (M SET)
    version: int  # 5
    num_tiles: int
    params: Params

    _format = "4s2I" + Params._format
    __slots__ = ["magic", "version", "num_tiles", "params"]
    _arrays = {"params": Params._mapping}
    _classes = {"params": Params}


TilePos = Tuple[int, int, int]  # ivec3
# ^ (x, y, layer)


class TileHeader(core.Struct):  # dtMeshHeader
    """Detour/Include/DetourNavMesh.h:274"""
    magic: bytes  # b"VAND" (D NAV)
    version: int  # 13
    position: TilePos
    user_id: int
    num_polygons: int
    per_poly_size: int  # bonus data
    num_vertices: int
    num_links: int
    detail: List[int]
    num_bounds_nodes: int
    num_connections: int  # number of off-mesh connections
    first_connection: int  # index of first polygon w/ off-mesh connection
    agent: List[int]  # walkable agent restrictions
    bounds: Tuple[vector.vec3, vector.vec3, float]

    _format = "4s4iI10i10f"
    __slots__ = [
        "magic", "version", "position", "user_id",
        "num_polygons", "per_poly_size", "num_vertices", "num_links",
        "detail", "num_bounds_nodes",
        "num_connections", "first_connection",
        "agent", "bounds"]
    _arrays = {
        "position": ["x", "y", "layer"],
        "detail": ["num_meshes", "num_vertices", "num_triangles"],
        "agent": ["height", "radius", "climb_height"],
        "bounds": {
            "mins": [*"xyz"],
            "maxs": [*"xyz"],
            "quantization_factor": None}}
    _classes = {
        "bounds.mins": vector.vec3,
        "bounds.maxs": vector.vec3}


class Polygon(core.Struct):  # dtPoly
    """r2recast/Detour/Include/DetourNavMesh.h:158"""
    first_link: int
    indices: List[int]  # 6x vertex indices
    neighbours:  List[int]  # 6x neighbour edge indices
    flags: int
    num_vertices: int
    area_type: int  # 6:2 bitfield
    disjoint_set_id: int
    unknown: int
    center: vector.vec3

    _format = "I13H2B2H3f"
    __slots__ = [
        "first_link", "indices", "neighbours", "flags",
        "num_vertices", "area_type", "disjoint_set_id",
        "unknown", "center"]
    _arrays = {
        "indices": 6, "neighbours": 6,
        "center": [*"xyz"]}
    _classes = {
        "center": vector.vec3}


class Link(core.Struct):  # dtLink
    """r2recast/Detour/Include/DetourNavMesh.h:211"""
    neighbour: int  # 32-bit! not 64!
    next_link: int
    edge: int  # index of polygon edge owning this link
    boundary: List[int]  # side & sub-edge area; boundary links only
    flags: int

    _format = "2I4BI"
    __slots__ = ["neighbour", "next_link", "edge", "boundary", "flags"]
    _arrays = {"boundary": ["side", "min", "max"]}
    # TODO: flags enum


class DetailMesh(core.Struct):  # dtPolyDetail
    """r2recast/Detour/Include/DetourNavMesh.h:200"""
    _format = "2I2B"
    # __slots__ = [
    #     "first_vertex", "first_triangle",
    #     "num_vertices", "num_triangles"]
    __slots__ = [
        "first_triangle", "first_vertex",
        "num_triangles", "num_vertices"]


class DetailTriangle(core.Struct):
    """Detour/Source/DetourNavMesh.cpp:644"""
    indices: List[int]
    # if index < poly.num_vertices: polygon.vertices[index]
    # else: polygon.detail_vertices[index - polygon.num_vertices]
    edge_flags: int  # 2:2:2 bitfield (top 2 bits unused)

    _format = "4B"
    __slots__ = ["indices", "edge_flags"]
    _arrays = {"indices": 3}
    # TODO: flags enum / bitfield
    # TODO: enum: DT_DETAIL_EDGE_BOUNDARY etc.


class BoundsNode(core.Struct):  # dtBVNode
    """r2recast/Detour/Include/DetourNavMesh.h:225"""
    mins: List[int]
    maxs: List[int]
    index: int  # -ve for "escape sequence"

    _format = "6Hi"
    __slots__ = ["mins", "maxs", "index"]
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}


class Connection(core.Struct):  # dtOffMeshConnection
    """r2recast/Detour/Include/DetourNavMesh.h:234"""
    position: Tuple[vector.vec3, vector.vec3]
    radius: float
    polygon: int
    flags: int  # TODO: LinkFlags
    side: int  # endpoint side
    user_id: int
    reference_position: vector.vec3
    yaw_angle: float

    _format = "7fH2BI4f"
    __slots__ = [
        "position", "radius", "polygon", "flags", "side", "user_id",
        "reference_position", "yaw_angle"]
    _arrays = {"position": {"a": [*"xyz"], "b": [*"xyz"]}}
    _classes = {
        "position.a": vector.vec3,
        "position.b": vector.vec3,
        "reference_position": vector.vec3}


class Tile:  # dtMeshTile
    """r2recast/Detour/Source/DetourNavMesh.cpp:986"""
    header: TileHeader
    vertices: List[vector.vec3]
    polygons: List[Polygon]
    per_poly: List[bytes]  # per_poly_size
    links: List[Link]
    detail_meshes: List[DetailMesh]
    detail_vertices: List[vector.vec3]
    detail_triangles: List[DetailTriangle]
    bounds_tree: List[BoundsNode]
    connections: List[Connection]

    def as_model(self) -> geometry.Model:
        normal = vector.vec3(z=+1)
        base_vertices = [
            geometry.Vertex(pos, normal)
            for pos in self.vertices]
        detail_vertices = [
            geometry.Vertex(pos, normal)
            for pos in self.detail_vertices]
        polygons = list()
        if len(self.polygons) != len(self.detail_meshes):
            raise AssertionError(  # 99% confident
                f"{len(self.polygons)=}, {len(self.detail_meshes)=}")
        for poly, dm in zip(self.polygons, self.detail_meshes):
            # print(f"{poly=}")
            # print(f"{dm=}")
            # local detail vertices slice
            start = dm.first_vertex
            end = start + dm.num_vertices
            local_vertices = detail_vertices[start:end]
            # triangles
            start = dm.first_triangle
            end = start + dm.num_triangles
            for triangle in self.detail_triangles[start:end]:
                face = list()
                for index in triangle.indices:
                    if index < poly.num_vertices:
                        face.append(base_vertices[index])
                    else:
                        print(", ".join([
                            f"{index=}",
                            f"{poly.num_vertices=}",
                            f"{len(local_vertices)=}",
                            f"{dm=}"]))
                        index -= poly.num_vertices
                        face.append(local_vertices[index])
                polygons.append(face)
        return geometry.Model([geometry.Mesh(polygons=polygons)])

    @classmethod
    def from_bytes(cls, raw_tile: bytes) -> Tile:
        return cls.from_stream(io.BytesIO(raw_tile))
        # TODO: verify we read all the bytes

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Tile:
        out = cls()
        # header
        out.header = TileHeader.from_stream(stream)
        assert out.header.magic == b"VAND", out.header.magic
        assert out.header.version == 13, out.header.version
        # data
        print("-==- TILE DATA -==-")
        print(f"{stream.tell()=} after header ({stream.tell() % 4})")
        out.vertices = [
            vector.vec3(*binary.read_struct(stream, "3f"))
            for i in range(out.header.num_vertices)]
        print(f"{stream.tell()=} after vertices ({stream.tell() % 4})")
        out.polygons = [
            Polygon.from_stream(stream)
            for i in range(out.header.num_polygons)]
        print(f"{stream.tell()=} after polygons ({stream.tell() % 4})")
        out.per_poly = [
            stream.read(out.header.per_poly_size * 4)
            for i in range(out.header.num_polygons)]
        print(f"{stream.tell()=} after per_poly ({stream.tell() % 4})")
        out.links = [
            Link.from_stream(stream)
            for i in range(out.header.num_links)]
        out.detail_meshes = [
            DetailMesh.from_stream(stream)
            for i in range(out.header.detail.num_meshes)]
        print(f"{stream.tell()=} after detail_meshes ({stream.tell() % 4})")
        stream.seek(4 - (stream.tell() % 4), 1)  # align to 4 byte boundary
        print(f"{stream.tell()=} after detail_meshes + realign")
        out.detail_vertices = [
            vector.vec3(*binary.read_struct(stream, "3f"))
            for i in range(out.header.detail.num_vertices)]
        print(f"{stream.tell()=} after detail_vertices ({stream.tell() % 4})")
        out.detail_triangles = [
            DetailTriangle.from_stream(stream)
            for i in range(out.header.detail.num_triangles)]
        print(f"{stream.tell()=} after triangles ({stream.tell() % 4})")
        out.bounds_tree = [
            BoundsNode.from_stream(stream)
            for i in range(out.header.num_bounds_nodes)]
        print(f"{stream.tell()=} after bounds_tree ({stream.tell() % 4})")
        out.connections = [
            Connection.from_stream(stream)
            for i in range(out.header.num_connections)]
        print(f"{stream.tell()=} after connections ({stream.tell() % 4})")
        # NOTE: should've crashed by now if we ran out of data
        # -- but did we read all the data?
        tail = stream.read()
        if len(tail) > 0:
            # multiple of 4 now
            # not per_poly
            print(f"! TAIL ! {out.header.position=}, {len(tail)=}")
            print(f"{len(tail) / 4}")
            print(f"{out.header=}")
        return out


class NavMesh(base.SceneDescription, breki.BinaryFile):
    """clockwise winding, right handed, Y up"""
    exts = ["*.nm"]
    header: FileHeader
    tiles: Dict[TilePos, TileHeader]
    # ^ {(x, y, layer): Tile}
    tile_refs: Dict[int, TilePos]
    # ^ {tileref: (x, y, layer)}

    def __init__(self, filepath: str, archive=None, code_page=None):
        super().__init__(filepath, archive, code_page)
        self.tiles = dict()
        self.tile_refs = dict()

    @parse_first
    def __repr__(self) -> str:
        descriptor = " ".join([
            f'"{self.filename}"',
            f"{len(self.tiles)} tiles",
            # f"{len(self.models)} models",
            ])
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def tile_model(self, pos) -> geometry.Model:
        tile = self.tiles[pos]
        x, y, layer = tile.header.position
        tile_size = self.header.params.tile_size
        x = x * tile_size.width
        y = y * tile_size.height
        # z = tile.position.layer *? +? ???
        model = tile.as_model()
        model.origin = self.header.params.origin + vector.vec3(x, y)
        return model

    def parse(self):
        if self.is_parsed:
            return
        self.is_parsed = True
        self.header = FileHeader.from_stream(self.stream)
        assert self.header.magic == b"TESM", self.header.magic
        assert self.header.version == 5, self.header.version
        # tiles
        for i in range(self.header.num_tiles):
            tile_ref, data_size = binary.read_struct(self.stream, "2I")
            if 0 in (tile_ref, data_size):
                break
            raw_tile = self.stream.read(data_size)
            tile = Tile.from_bytes(raw_tile)
            tile_pos = tile.header.position
            assert tile_ref not in self.tile_refs
            assert tile_pos not in self.tiles
            self.tile_refs[tile_ref] = tile_pos
            self.tiles[tile_pos] = tile
        # that's the whole file!
        self.models = {
            f"{ref:08X}": self.tile_model(pos)
            for ref, pos in self.tile_refs.items()}
