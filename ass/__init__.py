__all__ = [
    "geometry", "physics", "physics2d", "scene", "vector", "quaternion",
    "Material", "Mesh", "Model", "Polygon", "Vertex",
    "AABB", "Brush", "Plane",
    "AABB2D", "Circle",
    "Vec2", "Vec3",
    "Quaternion"]

# modules
from . import geometry
# NOTE: might break material out into it's own module
# -- will see once we're interacting w/ bite
from . import physics
from . import physics2d
from . import scene  # file formats
from . import vector
from . import quaternion

# classes
from .geometry import (
    Material,
    Mesh,
    Model,
    Polygon,
    Vertex)
from .physics import (
    AABB,
    Brush,
    Plane)
from .physics2d import AABB as AABB2D  # TODO: rename
from .physics2d import Circle
from .vector import vec2 as Vec2  # TODO: rename
from .vector import vec3 as Vec3  # TODO: rename
from .quaternion import Quaternion
