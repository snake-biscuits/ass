# using .bt (010 Hex Binary Template) reversed by MasterLiberty & others
# Source SDK 2013 public/src/studio.h
# snake-biscuits/titanfall2_mdl_converter (private, incomplete)
# headassbtw/mdlshit (mostly complete, no structs)
import enum
from typing import List

import breki
from breki import binary
from breki import core


class BodyPart(core.Struct):
    __slots__ = ["num_models", "model_index"]
    _format = "2I"


class Model(core.Struct):
    __slots__ = ["num_lods", "lod_index"]
    _format = "2I"


class Lod(core.Struct):
    __slots__ = ["num_meshes", "mesh_index", "switch_point"]
    _format = "2If"


class Mesh(core.Struct):
    __slots__ = ["num_strip_groups", "strip_group_index", "flags"]
    _format = "2IB"


class StripGroupFlags(enum.IntFlag):
    FLEXED = 0x01
    HARDWARE_SKINNED = 0x02
    DELTA_FLEXED = 0x04
    SUPPRESS_HARDWARE_MORPH = 0x08


class StripGroup(core.Struct):
    __slots__ = [
        "num_vertices", "vertex_index",
        "num_indices", "index_index",  # array of uint16_t
        "num_strips", "strip_index",
        "flags"]
    _format = "6IB"
    _classes = {"flags": StripGroupFlags}
    # NOTE: v49 (CS:GO) has 8 bytes of trailing padding
    # -- still version 7 in VtxHeader


class Strip(core.Struct):
    __slots__ = [
        "num_indices", "index_index",  # "index into group's pool"
        "num_vertices", "vertex_index",  # "index into group's pool"
        "num_bones", "flags",
        "num_bone_state_changes",  # 0x??000000
        "bone_state_change_index"]
    _format = "4IHB2I"  # bad struct alignment?


class Vertex(core.Struct):
    vvd_index: int  # mesh-relative index into vertices
    bone_id: List[int]  # indexes a global bone table
    __slots__ = [
        "bone_weight_index", "num_bones",
        "vvd_index", "bone_id"]
    _format = "4BH3B"
    _arrays = {"bone_weight_index": 3, "bone_id": 3}


class VtxHeader(core.Struct):
    __slots__ = [
        "version", "vertex_cache_size",
        "max_bones_per_strip",
        "max_bones_per_triangle",
        "max_bones_per_vertex",
        "checksum", "num_lods",
        "material_replacement_list_index",  # near EOF, b"\0" * 8
        "num_body_parts", "body_part_index"]
    _format = "2I2H6I"


class Vtx(breki.BinaryFile):
    header: VtxHeader

    def parse(self):
        if self.is_parsed:
            return
        self.is_parsed = True
        self.header = VtxHeader.from_stream(self.stream)
        assert self.header.version == 7

        self.stream.seek(self.header.body_part_index)
        body_parts = [
            (i, self.stream.tell(), BodyPart.from_stream(self.stream))
            for i in range(self.header.num_body_parts)]

        models = list()
        for i, offset, body_part in body_parts:
            self.stream.seek(offset + body_part.model_index)
            for j in range(body_part.num_models):
                offset = self.stream.tell()
                model = Model.from_stream(self.stream)
                models.append(((i, j), offset, model))

        lods = list()
        for index, offset, model in models:
            self.stream.seek(offset + model.lod_index)
            for i in range(model.num_lods):
                offset = self.stream.tell()
                lod = Lod.from_stream(self.stream)
                lods.append(((*index, i), offset, lod))

        # NOTE: 1 mesh per mdl.texture
        meshes = list()
        for index, offset, lod in lods:
            self.stream.seek(offset + lod.mesh_index)
            for i in range(lod.num_meshes):
                offset = self.stream.tell()
                mesh = Mesh.from_stream(self.stream)
                meshes.append(((*index, i), offset, mesh))

        strip_groups = list()
        for index, offset, mesh in meshes:
            self.stream.seek(offset + mesh.strip_group_index)
            for i in range(mesh.num_strip_groups):
                offset = self.stream.tell()
                strip_group = StripGroup.from_stream(self.stream)
                strip_groups.append(((*index, i), offset, strip_group))

        strips = list()
        vertices = dict()
        indices = dict()
        for index, offset, strip_group in strip_groups:
            self.stream.seek(offset + strip_group.strip_index)
            for i in range(strip_group.num_strips):
                strip = Strip.from_stream(self.stream)
                strips.append(((*index, i), self.stream.tell(), strip))
            self.stream.seek(offset + strip_group.vertex_index)
            vertices[index] = [
                Vertex.from_stream(self.stream)
                for i in range(strip_group.num_vertices)]
            self.stream.seek(offset + strip_group.index_index)
            indices[index] = binary.read_struct(
                self.stream, f"{strip_group.num_indices}H")

        self.body_parts = body_parts
        self.models = {index: model for index, offset, model in models}
        self.lods = {index: lod for index, offset, lod in lods}
        self.meshes = {index: mesh for index, offset, mesh in meshes}
        self.strip_groups = {index: sg for index, offset, sg in strip_groups}
        self.strips = {index: strip for index, offset, strip in strips}
        # NOTE: same indices as strip_group, List[type] values
        self.vertices = vertices
        self.indices = indices
