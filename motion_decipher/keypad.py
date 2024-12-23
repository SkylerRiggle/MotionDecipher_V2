from math import atan2, pi
from typing import Callable


class Direction:
    NORTH: int = 0
    NORTH_EAST: int = 1
    EAST: int = 2
    SOUTH_EAST: int = 3
    SOUTH: int = 4
    SOUTH_WEST: int = 5
    WEST: int = 6
    NORTH_WEST: int = 7

    UNIT_CIRCLE: list[int] = [
        EAST,
        NORTH_EAST,
        NORTH,
        NORTH_WEST,
        WEST,
        SOUTH_WEST,
        SOUTH,
        SOUTH_EAST
    ]

    @staticmethod
    def dir_to_str(direction: int) -> str:
        match direction:
            case Direction.NORTH:
                return 'N'
            case Direction.NORTH_EAST:
                return 'NE'
            case Direction.EAST:
                return 'E'
            case Direction.SOUTH_EAST:
                return 'SE'
            case Direction.SOUTH:
                return 'S'
            case Direction.SOUTH_WEST:
                return 'SW'
            case Direction.WEST:
                return 'W'
            case Direction.NORTH_WEST:
                return 'NW'
        return "?"

    @staticmethod
    def points_to_direction(
        point_a: tuple[float, float],
        point_b: tuple[float, float],
        ambiguous_region: float = 15.0
    ) -> list[int]:
        dx = point_b[0] - point_a[0]
        dy = point_b[1] - point_a[1]

        if dx == 0.0:
            if dy > 0.0:
                degree = 90
            else:
                degree = 270
        elif dy == 0.0:
            if dx > 0.0:
                degree = 0
            else:
                degree = 180
        else:
            degree = atan2(dy, dx) * 180.0 / pi
            while degree < 0.0:
                degree += 360.0
            degree %= 360.0

        unambiguous_region = max(
            min(360.0, 360.0 - 8 * ambiguous_region), 0.0
        ) / 8.0
        cur_angle = unambiguous_region * 0.5

        if degree < cur_angle:
            return [Direction.EAST]

        for idx in range(8):
            cur_angle += ambiguous_region

            if degree <= cur_angle:
                return [
                    Direction.UNIT_CIRCLE[idx],
                    Direction.UNIT_CIRCLE[(idx + 1) % 8]
                ]

            cur_angle += unambiguous_region

            if degree < cur_angle:
                return [Direction.UNIT_CIRCLE[(idx + 1) % 8]]

        return [Direction.EAST]

class Key:
    __id: int
    __x: float
    __y: float

    __press_callback__: Callable[[str, int | None], str]

    def __init__(
        self,
        key_id: int,
        x: float,
        y: float,
        press_callback: Callable[[str, int | None], str],
    ):
        self.__id = key_id
        self.__x = x
        self.__y = y
        self.__press_callback = press_callback

    def get_id(self) -> int:
        return self.__id

    def get_center(self) -> tuple[float, float]:
        return self.__x, self.__y

    def press(
        self,
        current_str: str,
        last_key_id: int | None = None
    ) -> tuple[str, int]:
        return self.__press_callback(current_str, last_key_id), self.__id

class Keypad:
    __key_list: list[Key]
    __angle_map: dict[int, dict[int, list[int]]]
    __distance_map: list[list[tuple[float, float]]]

    def __init__(self, keys: list[Key]):
        self.__key_list = keys
        self.__build_angle_map__()
        self.__build_distance_map__()

    def __build_angle_map__(self):
        self.__angle_map = {}

        for idx in range(len(self.__key_list)):
            key_1 = self.__key_list[idx].get_center()

            self.__angle_map[idx] = {
                Direction.NORTH: [],
                Direction.NORTH_EAST: [],
                Direction.EAST: [],
                Direction.SOUTH_EAST: [],
                Direction.SOUTH: [],
                Direction.SOUTH_WEST: [],
                Direction.WEST: [],
                Direction.NORTH_WEST: [],
            }

            for jdx in range(len(self.__key_list)):
                if idx == jdx:
                    continue

                key_2 = self.__key_list[jdx].get_center()
                for direction in Direction.points_to_direction(
                    key_1,
                    key_2,
                    0.0
                ):
                    self.__angle_map[idx][direction].append(jdx)

    def __build_distance_map__(self):
        num_keys = len(self.__key_list)
        self.__distance_map = [[(0.0, 0.0)] * num_keys for _ in range(num_keys)]

        for idx in range(num_keys):
            key_1 = self.__key_list[idx].get_center()
            self.__distance_map[idx][idx] = (0.0, 0.0)

            for jdx in range(idx + 1, num_keys):
                key_2 = self.__key_list[jdx].get_center()

                distance = (
                    abs(key_1[0] - key_2[0]),
                    abs(key_1[1] - key_2[1])
                )

                self.__distance_map[idx][jdx] = distance
                self.__distance_map[jdx][idx] = distance

    def infer_candidates(
        self,
        input_points: list[tuple[float, float]],
        angle_ambiguous_region: float,
        distance_ambiguous_region: tuple[float, float]
    ) -> list[str]:
        if len(input_points) == 0:
            return []
        elif len(input_points) == 1:
            return [key.press("")[0] for key in self.__key_list]

        candidates: set[str] = set()

        max_point_1 = (0.0, 0.0)
        max_point_2 = (0.0, 0.0)
        max_dist: float = 0.0

        for idx_1 in range(len(input_points) - 1):
            point_1 = input_points[idx_1]
            for idx_2 in range(idx_1 + 1, len(input_points)):
                point_2 = input_points[idx_2]
                cur_dist = (
                        abs(point_1[0] - point_2[0]) +
                        abs(point_1[1] - point_2[1])
                )

                if cur_dist > max_dist:
                    max_dist = cur_dist
                    max_point_1 = point_1
                    max_point_2 = point_2

        for kdx_1 in range(len(self.__key_list)):
            key_1 = self.__key_list[kdx_1].get_center()
            for kdx_2 in range(len(self.__key_list)):
                key_2 = self.__key_list[kdx_2].get_center()

                s_x = (key_1[0] - key_2[0]) / (max_point_1[0] - max_point_2[0])
                s_y = (key_1[1] - key_2[1]) / (max_point_1[1] - max_point_2[1])

                if s_x < 0.0 or s_y < 0.0:
                    continue

                last_point = input_points[0]
                cur_sequences = [(0.0, [idx]) for idx in range(len(self.__key_list))]
                for cur_point in input_points[1:]:
                    new_sequences = []

                    dx = s_x * abs(cur_point[0] - last_point[0])
                    dy = s_y * abs(cur_point[1] - last_point[1])
                    cur_directions = Direction.points_to_direction(
                        (last_point[0] * s_x, last_point[1] * s_y),
                        (cur_point[0] * s_x, cur_point[1] * s_y),
                        angle_ambiguous_region
                    )

                    for cur_err, sequence in cur_sequences:
                        last_key_idx = sequence[-1]

                        err_x = abs(dx - self.__distance_map[last_key_idx][last_key_idx][0])
                        err_y = abs(dy - self.__distance_map[last_key_idx][last_key_idx][1])

                        if (
                            err_x <= distance_ambiguous_region[0] and
                            err_y <= distance_ambiguous_region[1]
                        ):
                            new_sequences.append((
                                cur_err + err_x + err_y,
                                sequence + [last_key_idx]
                            ))

                        for direction in cur_directions:
                            for key_idx in self.__angle_map[last_key_idx][direction]:
                                err_x = abs(dx - self.__distance_map[last_key_idx][key_idx][0])
                                err_y = abs(dy - self.__distance_map[last_key_idx][key_idx][1])

                                if (
                                    err_x <= distance_ambiguous_region[0] and
                                    err_y <= distance_ambiguous_region[1]
                                ):
                                    new_sequences.append((
                                        cur_err + err_x + err_y,
                                        sequence + [key_idx]
                                    ))

                    cur_sequences = new_sequences
                    last_point = cur_point

                for cur_err, sequence in cur_sequences:
                    last_key_id = None
                    candidate: str = ""
                    for key_idx in sequence:
                        candidate, last_key_id = self.__key_list[key_idx].press(
                            candidate, last_key_id
                        )

                    candidates.add(candidate)

        return list(candidates)

META_QUEST_3_KEYPAD = Keypad([
    Key(0, 0.5, 0.0, lambda x, _ : x + '0'),

    Key(1, 0.0, 1.0, lambda x, _ : x + '1'),
    Key(2, 0.5, 1.0, lambda x, _ : x + '2'),
    Key(3, 1.0, 1.0, lambda x, _ : x + '3'),

    Key(4, 0.0, 2/3, lambda x, _ : x + '4'),
    Key(5, 0.5, 2/3, lambda x, _ : x + '5'),
    Key(6, 1.0, 2/3, lambda x, _ : x + '6'),

    Key(7, 0.0, 1/3, lambda x, _ : x + '7'),
    Key(8, 0.5, 1/3, lambda x, _ : x + '8'),
    Key(9, 1.0, 1/3, lambda x, _ : x + '9'),
])