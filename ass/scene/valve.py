# using .bt (010 Hex Binary Template) reversed by MasterLiberty & others
# also used Source SDK public/src/studio.h for reference
from __future__ import annotations
from typing import Dict, List

from .. import geometry
from .. import vector
from . import base

import breki
from breki import binary
from breki import core
# from breki.files.parsed import parse_first


class Texturev53(core.Struct):
    # texture_dir index in unknown?
    # unused & used?
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
    vvd_offset: int  # offset of .vvd data; 0 if none
    name_offset: int  # 0 if none
    phy_offset: int  # offset of .phy data; 0 if none
    unknown_3: List[int]
    vtx_offset: int  # offset of .vtx data; 0 if none

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
        "unknown_2", "vvd_offset", "name_offset", "phy_offset",
        "unknown_3", "vtx_offset"]
    _format = "4s3I64sI18f44IfI10I4Bf2If19I"
    _arrays = {
        "eye_position": [*"xyz"],
        "illumination_position": [*"xyz"],
        "hull": {"min": [*"xyz"], "max": [*"xyz"]},
        "view": {"min": [*"xyz"], "max": [*"xyz"]},
        "unknown_2": 5, "unknown_3": 7}
    _classes = {
        "eye_position": vector.vec3,
        "illumination_position": vector.vec3,
        "hull.min": vector.vec3, "hull.max": vector.vec3,
        "view.min": vector.vec3, "view.max": vector.vec3}


class Mdl(base.SceneDescription, breki.BinaryFile):
    code_page = breki.CodePage("latin_1", "strict")
    exts = ["*.mdl"]
    models: Dict[str, geometry.Model]
    # metadata
    name: str
    textures: List[str]

    def __init__(self, filepath: str, archive=None, code_page=None):
        super().__init__(filepath, archive, code_page)
        self.name = "untitled.mdl"
        self.textures = list()

    def __repr__(self) -> str:
        descriptor = f'"{self.name}" {len(self.models)} models'
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

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
        # TODO: model data -> self.models
        ...
        # textures
        self.stream.seek(self.header.texture_index)
        texture_structs = [
            (self.stream.tell(), Texturev53.from_stream(self.stream))
            for i in range(self.header.num_textures)]
        for offset, tex_struct in texture_structs:
            self.stream.seek(offset + tex_struct.relative_offset)
            self.textures.append(binary.read_str(self.stream, *self.code_page))
        # NOTE: texture dirs might also be a struct
        # -- first int is an absolute offset into .mdl strings table
