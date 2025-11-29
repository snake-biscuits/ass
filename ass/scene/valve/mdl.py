# using .bt (010 Hex Binary Template) reversed by MasterLiberty & others
# Source SDK 2013 public/src/studio.h
# snake-biscuits/titanfall2_mdl_converter (private, incomplete)
# headassbtw/mdlshit (mostly complete, no structs)
from __future__ import annotations
import os
from typing import Dict, List

from ... import geometry
from ... import vector
from .. import base
from .vtx import Vtx
from .vvd import Vvd

import breki
from breki import binary
from breki import core


class Texturev53(core.Struct):
    __slots__ = ["relative_offset", "flags", "used", "unused"]
    _format = "11I"
    _arrays = {"unused": 8}


# NOTE: technically respawn.Mdl
# TODO: use breki.FriendlyFile to handle embedded files
class MdlHeaderv53(core.Struct):
    magic: bytes  # b"IDST"
    version: int  # 53 for Titanfall2
    checksum: int  # must match in linked files
    name_copy_offset: int
    name: bytes  # internal filename
    filesize: int  # .mdl size in bytes
    ...
    # v53 header2
    unknown_2: List[int]  # sizes / indices?
    vtx_offset: int  # offset of .vtx data; 0 if none
    vvd_offset: int  # offset of .vvd data; 0 if none
    vvc_offset: int  # offset of .vvc data; 0 if none
    phy_offset: int  # offset of .phy data; 0 if none
    vtx_length: int
    vvd_length: int
    vvc_length: int
    phy_length: int
    unknown_3: List[int]
    vtx_offset2: int  # again, idk why

    __slots__ = [
        "magic", "version", "checksum", "name_copy_offset", "name", "filesize",
        "eye_position", "illumination_position", "hull", "view",
        "flags",
        "num_bones", "bone_index",
        "num_bone_controllers", "bone_controller_index",
        "num_hitbox_sets", "hitbox_set_index",
        "num_local_anim", "local_anim_index",
        "num_local_seq", "local_seq_index",
        "activity_list_version", "events_indexed",
        "num_textures", "texture_index",
        "num_texture_dirs", "texture_dir_index",
        "num_skin_ref", "num_skin_families", "skin_index",
        "num_body_parts", "body_part_index",
        "num_local_attachments", "local_attachment_index",
        "num_local_nodes", "local_node_index", "local_node_name_index",
        "deprecated_num_flex_desc", "deprecated_flex_desc_index",
        "deprecated_num_flex_controllers", "deprecated_flex_controller_index",
        "deprecated_num_flex_rules", "deprecated_flex_rule_index",
        "num_ik_chains", "ik_chain_index",
        "deprecated_num_mouths", "deprecated_mouth_index",
        "num_local_pose_parameters", "local_pose_param_index",
        "surfaceprop_index",
        "keyvalue_index", "keyvalue_size",
        "num_local_ik_autoplay_locks", "local_ik_autoplay_lock_index",
        "mass", "contents",
        "num_include_models", "include_model_index",
        "virtualModel",
        "anim_block_name_index", "num_anim_blocks", "anim_block_index",
        "anim_block_model", "bone_table_by_name_index",
        "vertex_base", "index_base",
        "const_directional_light_dot", "root_lod", "num_allowed_root_lods",
        "unused", "fade_distance", "deprecated_num_flex_controller_ui",
        "deprecated_flex_controller_ui_index", "vert_anim_fixed_point_scale",
        "surfaceprop_lookup", "studiohdr2_index", "source_filename_offset",
        "unknown_2",
        "vtx_offset", "vvd_offset", "vvc_offset", "phy_offset",
        "vtx_length", "vvd_length", "vvc_length", "phy_length",
        # num_unknown_3, unknown_3_index, ?, ?, 240 null bytes
        "unknown_3", "vtx_offset2"]
    _format = "4s3I64sI18f44IfI10I4Bf2If19I"
    _arrays = {
        "eye_position": [*"xyz"],
        "illumination_position": [*"xyz"],
        "hull": {"min": [*"xyz"], "max": [*"xyz"]},
        "view": {"min": [*"xyz"], "max": [*"xyz"]},
        "unknown_2": 4, "unknown_3": 3}
    _classes = {
        "eye_position": vector.vec3,
        "illumination_position": vector.vec3,
        "hull.min": vector.vec3, "hull.max": vector.vec3,
        "view.min": vector.vec3, "view.max": vector.vec3}


class Mdl(base.SceneDescription, breki.FriendlyBinaryFile):
    code_page = breki.CodePage("latin_1", "strict")
    exts = ["*.mdl"]
    models: Dict[str, geometry.Model]
    # mdl metadata
    name: str
    textures: List[str]
    # related files shortcuts
    phy: breki.File
    vtx: Vtx
    vvc: breki.File
    vvd: Vvd

    def __init__(self, filepath: str, archive=None, code_page=None):
        super().__init__(filepath, archive, code_page)
        self.name = "untitled.mdl"
        self.textures = list()
        self.phy = None
        self.vtx = None
        self.vvc = None
        self.vvd = None

    def __repr__(self) -> str:
        descriptor = f'"{self.name}" {len(self.models)} models'
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    # TODO: automatically convert friends to BinaryFile subclasses
    # -- can extend .made_friends()

    @property
    def friend_patterns(self) -> Dict[str, breki.DataType]:
        base_name = os.path.splitext(self.filename)[0]
        return {
            f"{base_name}.{ext}": breki.DataType.BINARY
            for ext in ("phy", "vtx", "vvc", "vvd")}

    def parse(self):
        if self.is_parsed:
            return
        self.is_parsed = True
        magic, version = binary.read_struct(self.stream, "4sI")
        assert magic == b"IDST"
        assert version == 53
        self.stream.seek(0)
        self.header = MdlHeaderv53.from_stream(self.stream)
        # TODO: accept multiple versions, not just Titanfall2's format
        assert self.header.filesize == self.size
        self.name = self.code_page.decode(self.header.name.rstrip(b"\0"))

        # textures
        # NOTE: texture dirs might be structs
        # -- first int is an absolute offset into .mdl strings table
        self.stream.seek(self.header.texture_index)
        texture_structs = [
            (self.stream.tell(), Texturev53.from_stream(self.stream))
            for i in range(self.header.num_textures)]
        for offset, tex_struct in texture_structs:
            self.stream.seek(offset + tex_struct.relative_offset)
            self.textures.append(binary.read_str(self.stream, *self.code_page))

        # expose files contained inside .mdl
        self.extract_internal("vtx")
        self.extract_internal("vvd")
        self.extract_internal("vvc")
        self.extract_internal("phy")

        if self.vtx is None or self.vvd is None:
            raise RuntimeError("mdl has no mesh data")

        self.vtx.parse()
        assert self.header.checksum == self.vtx.header.checksum

        self.vvd.parse()
        assert self.header.checksum == self.vvd.header.checksum

        # TODO: defer parsing models until .models is touched
        # NOTE: this approach makes a lot of assumptions:
        # -- one BodyPart, Model, StripGroup & Strip per Mesh
        # -- indices are a valid triangle soup, rather than a series of strips
        # NOTE: some LoDs will not use all materials
        # -- assuming mesh index is material index
        base_name = os.path.splitext(self.filename)[0]
        for i in range(self.vvd.header.num_lods):
            # NOTE: for blender uv.y is invertex
            # -- y axis scale may be incorrect for non-square textures
            vertices = [
                geometry.Vertex(v.position, v.normal, v.uv)
                for v in self.vvd.lod[i]]
            meshes = list()
            offset = 0
            for j, texture in enumerate(self.textures):
                material = geometry.Material(texture.replace("\\", "/"))
                # BodyPart, Model, Lod, Mesh, StripGroup)
                index = (0, 0, i, j, 0)
                if index not in self.vtx.strip_groups:
                    continue
                strip_group = self.vtx.strip_groups[index]
                vtx_vertices = self.vtx.vertices[index]
                indices = self.vtx.indices[index]
                polygons = list()
                for k in range(0, strip_group.num_indices, 3):
                    a = vtx_vertices[indices[k + 0]].vvd_index + offset
                    b = vtx_vertices[indices[k + 1]].vvd_index + offset
                    c = vtx_vertices[indices[k + 2]].vvd_index + offset
                    polygons.append(geometry.Polygon([
                        vertices[a], vertices[b], vertices[c]]))
                meshes.append(geometry.Mesh(material, polygons))
                offset += self.vtx.strips[(*index, 0)].num_vertices
            self.models[f"{base_name}.lod{i}"] = geometry.Model(meshes)

    def extract_internal(self, ext: str):
        offset = getattr(self.header, f"{ext}_offset")
        length = getattr(self.header, f"{ext}_length")
        if (offset, length) == (0, 0):
            return None  # no data to extract
        assert offset + length <= self.size
        self.stream.seek(offset)
        raw_data = self.stream.read(length)
        base_name = os.path.splitext(self.filename)[0]
        filename = f"{base_name}.{ext}"
        full_path = os.path.join(self.folder, filename)
        file_classes = {"vtx": Vtx, "vvd": Vvd}
        file_class = file_classes.get(ext, breki.File)
        self.friends[filename] = file_class.from_bytes(
            full_path, raw_data, breki.DataType.BINARY, self.code_page)
        setattr(self, ext, self.friends[filename])
