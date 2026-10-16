import math

from ass.physics import AABB, Plane
from ass.vector import vec3

import pytest


planes = {"floor": (vec3(z=1), 0)}


class TestInit:
    @pytest.mark.parametrize("normal,distance", planes.values(), ids=planes.keys())
    def test_init(self, normal: vec3, distance: float):
        plane = Plane(normal, distance)
        assert plane.normal == normal
        assert plane.distance == distance

    def test_invalid(self):
        with pytest.raises(AssertionError):
            Plane(vec3(z=2), 0)


# def test_negation(plane, inverse):
#     assert -Plane(*plane) == Plane(*inverse)


class TestCollision:
    def test_point(self):
        plane = Plane(vec3(z=1), 0)
        assert plane.test(vec3(z=1)) == 1  # above
        assert plane.test(vec3(z=-1)) == -1  # below


cube = AABB.from_origin_extents(origin=vec3(0, 0, 0), extents=vec3(1, 1, 1))

axials = {
    "X+": (cube, Plane(vec3(x=+1), 1)),
    "Y+": (cube, Plane(vec3(y=+1), 1)),
    "Z+": (cube, Plane(vec3(z=+1), 1)),
    "X-": (cube, Plane(vec3(x=-1), 1)),
    "Y-": (cube, Plane(vec3(y=-1), 1)),
    "Z-": (cube, Plane(vec3(z=-1), 1))}

half_sqrt_2 = math.sqrt(2) / 2
# third_sqrt_3 = math.sqrt(3) / 3  # for corner bevel

bevel_axes = {
    "NW": (-1, +1), "NE": (+1, +1),
    "SW": (-1, -1), "SE": (+1, -1)}

bevel_normals = {
    cardinal: vec3(x, y, 0) * half_sqrt_2
    for cardinal, (x, y) in bevel_axes.items()}

bevels = {
    cardinal: (cube, Plane(normal, math.sqrt(2)))
    for cardinal, normal in bevel_normals.items()}


class TestAABBInteraction:
    @pytest.mark.parametrize("aabb,plane", axials.values(), ids=axials.keys())
    def test_is_axial(self, aabb, plane):
        assert plane.is_axial_of(aabb)

    @pytest.mark.parametrize("aabb,plane", bevels.values(), ids=bevels.keys())
    def test_is_not_axial(self, aabb, plane):
        assert not plane.is_axial_of(aabb)
        # definitely not intersecting
        plane2 = Plane(plane.normal, plane.distance * 2)
        assert not plane2.is_axial_of(aabb)

    @pytest.mark.parametrize("aabb,plane", bevels.values(), ids=bevels.keys())
    def test_is_bevel(self, aabb, plane):
        assert plane.is_bevel_of(aabb)

    @pytest.mark.parametrize("aabb,plane", axials.values(), ids=axials.keys())
    def test_is_not_bevel(self, aabb, plane):
        assert not plane.is_bevel_of(aabb)
        # definitely not intersecting
        plane2 = Plane(plane.normal, plane.distance * 2)
        assert not plane2.is_bevel_of(aabb)

    # def test_intersections(self):
    #     ...

    # def test_slices(self):
    #     ...
