"""adapted from ass.physics"""
from __future__ import annotations
from collections.abc import Iterable
import math
from typing import List, Union

from . import vector


class AABB:
    """Axis-Aligned Bounding Box"""
    # NOTE: no internal validity checks (mins <= maxs; extents >= 0)
    mins: vector.vec2 = property(lambda s: s._mins)
    maxs: vector.vec2 = property(lambda s: s._maxs)
    origin: vector.vec2 = property(lambda s: s._origin)
    extents: vector.vec2 = property(lambda s: s._extents)  # should be positive
    # NOTE: you should add an epsilon to extents before testing for collision

    def __init__(self):
        self._origin = vector.vec2(0, 0)
        self._extents = vector.vec2(math.inf, math.inf)
        self._mins = vector.vec2(math.inf, math.inf)
        self._maxs = vector.vec2(-math.inf, -math.inf)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {tuple(self.mins)} -> {tuple(self.maxs)}>"

    def __add__(self, other: Union[vector.vec2, Bounds]) -> AABB:
        """expand to enclose"""
        out = self.__class__()
        if isinstance(other, Iterable) and len(other) == 2:
            other = vector.vec2(*other)
        if isinstance(other, vector.vec2):  # expand bounds to contain point
            out.mins = vector.vec2(*[min(s, o) for s, o in zip(self.mins, other)])
            out.maxs = vector.vec2(*[max(s, o) for s, o in zip(self.maxs, other)])
        elif isinstance(other, AABB):  # expand bounds around other AABB
            out.mins = vector.vec2(*[min(s, o) for s, o in zip(self.mins, other.mins)])
            out.maxs = vector.vec2(*[max(s, o) for s, o in zip(self.maxs, other.maxs)])
        else:
            raise TypeError(
                f"{self.__class__.__name__} cannot contain '{type(other).__name__}'")
        return out

    def __contains__(self, other: Union[vector.vec2, AABB]) -> bool:
        # type coersion
        if isinstance(other, Iterable) and len(other) == 2:
            other = vector.vec2(*other)
        # tests
        if isinstance(other, vector.vec2):
            return all([m <= a <= M for m, a, M in zip(self.mins, other, self.maxs)])
        elif isinstance(other, AABB):
            mins_inside = all([s <= o for s, o in zip(self.mins, other.mins)])
            maxs_inside = all([s >= o for s, o in zip(self.maxs, other.maxs)])
            return mins_inside and maxs_inside
        else:
            raise TypeError(f"{self.__class__.__name__} cannot contain '{type(other).__name__}'")

    def __eq__(self, other: AABB) -> bool:
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self.mins, self.maxs))

    def intersects(self, other: AABB) -> bool:
        # TODO: test
        return all([
            sm <= oM and sM >= om  # overlaps on axis
            for sm, oM, sM, om in zip(self.mins, other.maxs, self.maxs, other.mins)])

    def as_circle(self) -> Circle:
        return Circle(self.origin, self.extents.magnitude())

    @property
    def corners(self) -> List[vector.vec2]:
        return [
            self.origin + vector.vec2(+self.extents.x, +self.extents.y),
            self.origin + vector.vec2(+self.extents.x, -self.extents.y),
            self.origin + vector.vec2(-self.extents.x, +self.extents.y),
            self.origin + vector.vec2(-self.extents.x, -self.extents.y)]

    # INITIALISERS

    @classmethod
    def from_mins_maxs(cls, mins: vector.vec2, maxs: vector.vec2) -> AABB:
        out = cls()
        assert len(mins) == 2
        assert len(maxs) == 2
        out._mins = vector.vec2(*mins)
        out._maxs = vector.vec2(*maxs)
        out._origin = (out.mins + out.maxs) / 2
        out._extents = out.maxs - out.origin
        return out

    @classmethod
    def from_origin_extents(cls, origin: vector.vec2, extents: vector.vec2) -> AABB:
        out = cls()
        assert len(origin) == 2
        assert len(extents) == 2
        out.origin = vector.vec2(*origin)
        out.extents = vector.vec2(*extents)
        return out

    @classmethod
    def from_points(cls, points: List[vector.vec2]) -> AABB:
        return sum({vector.vec2(*p) for p in points}, start=cls())

    # SETTERS

    @mins.setter
    def mins(self, new_mins: vector.vec2):
        """expand bounds"""
        self._mins = new_mins
        self._origin = (self.mins + self.maxs) / 2
        self._extents = self.mins + self.origin

    @maxs.setter
    def maxs(self, new_maxs: vector.vec2):
        """expand bounds"""
        self._maxs = new_maxs
        self._origin = (self.mins + self.maxs) / 2
        self._extents = self.maxs - self.origin

    @origin.setter
    def origin(self, new_origin: vector.vec2):
        """move the center, keep dimensions"""
        self._origin = new_origin
        self._mins = self.origin - self.extents
        self._maxs = self.origin + self.extents

    @extents.setter
    def extents(self, new_extents: vector.vec2):
        """keep the center, change dimensions"""
        self._extents = new_extents
        self._mins = self.origin - self.extents
        self._maxs = self.origin + self.extents


class Circle:
    center: vector.vec2
    radius: float

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
        # NOTE: could maybe do something funky where Circle()+... sets center
        # -- can't really see a purpose to that tho
        # -- and it's not very transparent
        # -- unlike AABB.from_points

    def __add__(self, other: Union[vector.vec2, Bounds]) -> Circle:
        if isinstance(other, Iterable) and len(other) == 2:
            other = vector.vec2(*other)
        if isinstance(other, vector.vec2):
            radius2 = (other - self.center).sqrmagnitude()
        elif isinstance(other, AABB):
            return sum(other.corners, start=self)
        elif isinstance(other, Circle):
            distance = (self.center - other.center).sqrmagnitude()
            radius2 = distance + other.radius ** 2
        else:
            raise TypeError(...)
        new_radius = math.sqrt(radius2)
        return Circle(self.center, max(new_radius, self.radius))

    def __contains__(self, other: Union[vector.vec2, AABB]):
        if isinstance(other, Iterable) and len(other) == 2:
            other = vector.vec2(*other)
        if isinstance(other, vector.vec2):
            return (other - self.center).sqrmagnitude() <= self.radius ** 2
        elif isinstance(other, AABB):
            return all(corner in self for corner in other.corners)
        elif isinstance(other, Circle):
            offset = (other.center - self.center).sqrmagnitude()
            return offset + other.radius ** 2 <= self.radius ** 2

    def intersects(self, other: Bounds):
        if isinstance(other, AABB):
            if not self.as_AABB().intersects(other):
                return False
            if any(corner in self for corner in other.corners):
                return True
            raise NotImplementedError("need to test for edge intersection")
        elif isinstance(other, Circle):
            distance = (self.center - other.center).sqrmagnitude()
            sqrradii = self.radius ** 2 + other.radius ** 2
            return distance <= sqrradii
        else:
            raise TypeError(...)

    def as_AABB(self) -> AABB:
        """square bounds of circle for lazy checks"""
        extents = vector.vec2(self.radius, self.radius)
        return AABB.from_origin_extents(self.center, extents)

    @classmethod
    def from_points(cls, points: List[vector.vec2]) -> Circle:
        center = sum(points) / len(points)
        radius_squared = max(
            (center - point).sqrmagniture()
            for point in points)
        return cls(center, math.sqrt(radius_squared))


# TODO: OBB (Oriented Bounding Box)


Bounds = Union[AABB, Circle]
