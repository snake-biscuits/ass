__all__ = [
    "geometry", "physics", "scene", "vector", "quaternion"]

from . import geometry
# NOTE: might break material out into it's own module
# -- will see once we're interacting w/ bite
from . import physics
from . import scene  # file formats
from . import vector
from . import quaternion

# TODO: only include viewer if dependencies are present
# from . import viewer

# TODO: expose classes
# -- geometry: Material, Mesh, Model, Polygon, Vertex
# -- physics: AABB, Brush, Plane
# -- vector: Vec2, Vec3 (rename!)
# -- quaternion: Quaternion
