__all__ = [
    "editor", "geometry", "physics", "scene",
    "texture", "vector", "quaternion"]

from . import editor
from . import geometry
# NOTE: might break material out into it's own module
# -- will see once we're interacting w/ bite
from . import physics
from . import scene  # file formats
from . import texture  # texture projection for editor
from . import vector
from . import quaternion

# TODO: only include viewer if dependencies are present
# from . import viewer

# TODO: expose classes
# -- physics: AABB etc.
# -- geometry: Vertex, Polygon, Mesh, Model, Material
# -- vector: Vec3, Vec2 (rename!)
# -- quaternion: Quaternion
# -- scene: pixar.Usd, wavefront.Obj, khronos.Gltf
