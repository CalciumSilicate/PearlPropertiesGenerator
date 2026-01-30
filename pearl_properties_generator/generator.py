import math
from dataclasses import dataclass
from typing import List
from enum import Enum


class SortBy(Enum):
    DISTANCE = "distance"
    TICK = "tick"
    TOTAL_TNT = "total_tnt"
    LIGHT_GRAY = "light_gray"
    DARK_GRAY = "dark_gray"


@dataclass
class Vec3d:
    x: float
    y: float
    z: float

    def __add__(self, other: "Vec3d") -> "Vec3d":
        return Vec3d(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vec3d") -> "Vec3d":
        return Vec3d(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> "Vec3d":
        return Vec3d(self.x * scalar, self.y * scalar, self.z * scalar)

    def length(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def distance(self, other: "Vec3d") -> float:
        return (self - other).length()

    def angle(self) -> float:
        return math.atan2(self.z, self.x)

    def __repr__(self) -> str:
        return f"({self.x:.4f}, {self.y:.4f}, {self.z:.4f})"


class Constant:
    BIG_ARRAY_TNT = 260
    MAX_BIG_ARRAY_COUNT = 7
    MAX_TNT = BIG_ARRAY_TNT * MAX_BIG_ARRAY_COUNT
    MAX_10_COUNT = BIG_ARRAY_TNT // 10
    MAX_1_COUNT = 10

    DELTA_POSITION = [
        Vec3d(0, 49.345698, 0),
        Vec3d(0, 49.357766, 0),
    ]

    MOTION = [
        Vec3d(0, 0.174457, 0),
        Vec3d(0, 0.206522, 0),
    ]

    THRUST = [
        Vec3d(0.602541821, -0.0022355, 0.602541821),
        Vec3d(0.602714894, 0.00660668, 0.602714894),
    ]

    SIGN_L = [
        [[+1, 1, +1], [-1, 1, -1], [+1, 1, -1], [+1, 1, -1]],
        [[-1, 1, +1], [+1, 1, -1], [+1, 1, +1], [+1, 1, +1]],
        [[-1, 1, -1], [+1, 1, +1], [-1, 1, +1], [-1, 1, +1]],
        [[+1, 1, -1], [-1, 1, +1], [-1, 1, -1], [-1, 1, -1]],
    ]

    SIGN_R = [
        [[-1, 1, +1], [-1, 1, +1], [+1, 1, +1], [-1, 1, -1]],
        [[-1, 1, -1], [-1, 1, -1], [-1, 1, +1], [+1, 1, -1]],
        [[+1, 1, -1], [+1, 1, -1], [-1, 1, -1], [+1, 1, +1]],
        [[+1, 1, +1], [+1, 1, +1], [+1, 1, -1], [-1, 1, +1]],
    ]


class Pearl:
    def __init__(self, position: Vec3d, momentum: Vec3d):
        self.position = Vec3d(position.x, position.y, position.z)
        self.momentum = Vec3d(momentum.x, momentum.y, momentum.z)

    def get_position(self) -> Vec3d:
        return self.position

    def get_y(self) -> float:
        return self.position.y

    def accelerate(self, thrust: Vec3d):
        self.momentum = self.momentum + thrust

    def tick(self, cnt: int = 1):
        for _ in range(cnt):
            self.position = self.position + self.momentum
            self.momentum = self.momentum * 0.99
            self.momentum.y -= 0.03

    def copy(self) -> "Pearl":
        return Pearl(
            Vec3d(self.position.x, self.position.y, self.position.z),
            Vec3d(self.momentum.x, self.momentum.y, self.momentum.z),
        )


class Setting:
    rotation: int = 0

    def __init__(
        self,
        amount_l: int = 0,
        amount_r: int = 0,
        direction: int = 0,
        pitch: int = 0,
    ):
        self.amount_l = amount_l
        self.amount_r = amount_r
        self.direction = direction
        self.pitch = pitch

    @classmethod
    def from_bits(cls, text: str) -> "Setting":
        bits = [c == '1' for c in text if c in '01']
        if len(bits) != 27:
            raise ValueError(f"Illegal setting bits: expected 27, got {len(bits)}")
        
        amount_l = 0
        amount_r = 0
        direction = 0
        pitch = 0
        
        p = iter(bits)
        amount_l += Constant.BIG_ARRAY_TNT * 1 * next(p)
        amount_l += Constant.BIG_ARRAY_TNT * 2 * next(p)
        amount_l += Constant.BIG_ARRAY_TNT * 4 * next(p)
        amount_r += Constant.BIG_ARRAY_TNT * 4 * next(p)
        amount_r += Constant.BIG_ARRAY_TNT * 2 * next(p)
        amount_r += Constant.BIG_ARRAY_TNT * 1 * next(p)
        amount_l += 1 * 1 * next(p)
        amount_l += 1 * 2 * next(p)
        amount_l += 1 * 4 * next(p)
        amount_l += 1 * 8 * next(p)
        amount_r += 1 * 8 * next(p)
        amount_r += 1 * 4 * next(p)
        amount_r += 1 * 2 * next(p)
        amount_r += 1 * 1 * next(p)
        pitch = next(p)
        amount_l += 10 * 1 * next(p)
        amount_l += 10 * 2 * next(p)
        amount_l += 10 * 4 * next(p)
        amount_l += 10 * 8 * next(p)
        amount_l += 10 * 16 * next(p)
        direction += 2 * next(p)
        direction += 1 * next(p)
        amount_r += 10 * 16 * next(p)
        amount_r += 10 * 8 * next(p)
        amount_r += 10 * 4 * next(p)
        amount_r += 10 * 2 * next(p)
        amount_r += 10 * 1 * next(p)
        
        return cls(amount_l, amount_r, direction, pitch)

    def get_thrust(self) -> Vec3d:
        thrust_l = Constant.THRUST[self.pitch] * self.amount_l
        thrust_r = Constant.THRUST[self.pitch] * self.amount_r

        rot = Setting.rotation
        d = self.direction

        thrust_l = Vec3d(
            thrust_l.x * Constant.SIGN_L[rot][d][0],
            thrust_l.y * Constant.SIGN_L[rot][d][1],
            thrust_l.z * Constant.SIGN_L[rot][d][2],
        )
        thrust_r = Vec3d(
            thrust_r.x * Constant.SIGN_R[rot][d][0],
            thrust_r.y * Constant.SIGN_R[rot][d][1],
            thrust_r.z * Constant.SIGN_R[rot][d][2],
        )

        return thrust_l + thrust_r

    def to_bits(self) -> str:
        def qpow(a: int, b: int) -> int:
            ans = 1
            while b > 0:
                if b & 1:
                    ans *= a
                a *= a
                b >>= 1
            return ans

        def split(num: int, step: int, k: int, max_count: int) -> tuple:
            step *= qpow(2, k - 1)
            ret = ""
            for i in range(k, 0, -1):
                t = qpow(2, i - 1)
                flag = step <= num and t <= max_count
                ret += "1" if flag else "0"
                if flag:
                    num -= step
                    max_count -= t
                step //= 2
            return ret, num

        a, b, d, p = self.amount_l, self.amount_r, self.direction, self.pitch

        a1, a = split(a, Constant.BIG_ARRAY_TNT, 3, Constant.MAX_BIG_ARRAY_COUNT - 1)
        a1 = a1[::-1]
        a2, a = split(a, 10, 5, Constant.MAX_10_COUNT - 1)
        a2 = a2[::-1]
        a3, a = split(a, 1, 4, Constant.MAX_1_COUNT)
        a3 = a3[::-1]

        b1, b = split(b, Constant.BIG_ARRAY_TNT, 3, Constant.MAX_BIG_ARRAY_COUNT - 1)
        b2, b = split(b, 10, 5, Constant.MAX_10_COUNT - 1)
        b3, b = split(b, 1, 4, Constant.MAX_1_COUNT)

        ds, _ = split(d, 1, 2, 3)
        ps, _ = split(p, 1, 1, 1)

        return f"[{a1} {b1}] [{a3} {b3}] [{ps} {a2} {ds} {b2}]"


@dataclass
class SettingResult:
    distance: float
    position: Vec3d
    tick: int
    light_gray: int
    dark_gray: int
    total_tnt: int
    bits: str
    direction: int
    pitch: int


@dataclass
class TracePoint:
    tick: int
    chunk: str
    position: Vec3d
    momentum: Vec3d


def get_chunk_string(pos: Vec3d) -> str:
    x = int(math.floor(pos.x / 16))
    z = int(math.floor(pos.z / 16))
    return f"[{x}, {z}]"


class TraceSimulator:
    def __init__(
        self,
        pearl_x: float,
        pearl_z: float,
        player_y: float,
        rotation: int,
        ground_y: float,
        max_tick: int,
    ):
        self.pearl_x = pearl_x
        self.pearl_z = pearl_z
        self.player_y = player_y
        self.rotation = rotation
        self.ground_y = ground_y
        self.max_tick = max_tick
        
        Setting.rotation = rotation

    def simulate(self, bits: str) -> List[TracePoint]:
        try:
            setting = Setting.from_bits(bits)
        except ValueError:
            return []
        
        pos = Vec3d(self.pearl_x, self.player_y, self.pearl_z) + Constant.DELTA_POSITION[setting.pitch]
        pearl = Pearl(pos, Vec3d(
            Constant.MOTION[setting.pitch].x,
            Constant.MOTION[setting.pitch].y,
            Constant.MOTION[setting.pitch].z
        ))
        pearl.accelerate(setting.get_thrust())
        
        results = []
        for tick in range(self.max_tick):
            if pearl.get_y() < self.ground_y:
                break
            results.append(TracePoint(
                tick=tick,
                chunk=get_chunk_string(pearl.get_position()),
                position=Vec3d(pearl.position.x, pearl.position.y, pearl.position.z),
                momentum=Vec3d(pearl.momentum.x, pearl.momentum.y, pearl.momentum.z),
            ))
            pearl.tick()
        
        return results


class PearlPropertiesGenerator:
    def __init__(
        self,
        pearl_x: float,
        pearl_z: float,
        player_y: float,
        rotation: int,
        max_tnt: int,
        ground_y: float,
        max_tick: int,
        dest_x: float,
        dest_z: float,
        max_results: int = 100,
    ):
        self.pearl_x = pearl_x
        self.pearl_z = pearl_z
        self.player_y = player_y
        self.rotation = rotation
        self.max_tnt = max_tnt
        self.ground_y = ground_y
        self.max_tick = max_tick
        self.dest_x = dest_x
        self.dest_z = dest_z
        self.max_results = max_results

        Setting.rotation = rotation

    def _get_pearl(self, pitch: int) -> Pearl:
        pos = Vec3d(self.pearl_x, self.player_y, self.pearl_z) + Constant.DELTA_POSITION[pitch]
        return Pearl(pos, Vec3d(Constant.MOTION[pitch].x, Constant.MOTION[pitch].y, Constant.MOTION[pitch].z))

    def _intersect(self, a1: float, a2: float, b1: float, b2: float) -> bool:
        return max(a1, b1) < min(a2, b2)

    def _in_range(self, direction: int, angle: float, delta: float) -> bool:
        s1 = Setting(0, 1, direction, 0)
        s2 = Setting(1, 0, direction, 0)
        a1 = s1.get_thrust().angle()
        a2 = s2.get_thrust().angle()

        if a2 < a1:
            a1, a2 = a2, a1

        pi = math.pi
        if abs(a2 - a1) > pi:
            a1 += 2 * pi
            a1, a2 = a2, a1

        b1 = angle - delta
        b2 = angle + delta

        return (
            self._intersect(a1, a2, b1, b2)
            or self._intersect(a1 + 2 * pi, a2 + 2 * pi, b1, b2)
            or self._intersect(a1, a2, b1 + 2 * pi, b2 + 2 * pi)
        )

    def generate(self, sort_by: SortBy = SortBy.DISTANCE) -> List[SettingResult]:
        pi = math.pi

        pearl0 = self._get_pearl(0)
        vec = Vec3d(self.dest_x, pearl0.get_y(), self.dest_z) - pearl0.get_position()
        angle = vec.angle()
        delta = 10.0 / self.max_tnt
        a1 = angle - delta
        a2 = angle + delta

        results = []

        for d in range(4):
            if not self._in_range(d, angle, delta):
                continue

            for i in range(self.max_tnt + 1):
                flag_success = False
                flag_break = False

                j = 0
                while not flag_break and j <= self.max_tnt:
                    for p in range(2):
                        if flag_break:
                            break

                        s = Setting(i, j, d, p)
                        thrust_angle = s.get_thrust().angle()

                        in_angle_range = (
                            (a1 < thrust_angle < a2)
                            or (a1 < thrust_angle + 2 * pi < a2)
                            or (a1 < thrust_angle - 2 * pi < a2)
                        )

                        if not in_angle_range:
                            if flag_success:
                                flag_break = True
                            continue

                        flag_success = True

                        pearl0_for_pitch = self._get_pearl(p)
                        pearl = pearl0_for_pitch.copy()
                        pearl.accelerate(s.get_thrust())

                        mn = 1e10
                        best_pos = pearl.get_position()
                        best_tick = -1

                        for tick in range(self.max_tick):
                            pearl.tick()
                            if pearl.get_y() < self.ground_y:
                                break

                            dis = pearl.get_position().distance(
                                Vec3d(self.dest_x, pearl.get_y(), self.dest_z)
                            )

                            if dis < mn:
                                mn = dis
                                best_pos = Vec3d(
                                    pearl.get_position().x,
                                    pearl.get_position().y,
                                    pearl.get_position().z,
                                )
                                best_tick = tick + 1
                            else:
                                break

                        if mn != 1e10:
                            results.append(
                                SettingResult(
                                    distance=mn,
                                    position=best_pos,
                                    tick=best_tick,
                                    light_gray=s.amount_l,
                                    dark_gray=s.amount_r,
                                    total_tnt=s.amount_l + s.amount_r,
                                    bits=s.to_bits(),
                                    direction=s.direction,
                                    pitch=s.pitch,
                                )
                            )
                    j += 1

        if sort_by == SortBy.DISTANCE:
            results.sort(key=lambda x: x.distance)
        elif sort_by == SortBy.TICK:
            results.sort(key=lambda x: x.tick)
        elif sort_by == SortBy.TOTAL_TNT:
            results.sort(key=lambda x: x.total_tnt)
        elif sort_by == SortBy.LIGHT_GRAY:
            results.sort(key=lambda x: x.light_gray)
        elif sort_by == SortBy.DARK_GRAY:
            results.sort(key=lambda x: x.dark_gray)

        return results[: self.max_results]
