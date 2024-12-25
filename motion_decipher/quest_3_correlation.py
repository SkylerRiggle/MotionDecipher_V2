from typing import Generator
from motion_decipher.math import compute_angle_deg, compute_distance


__NUM_COLUMNS: int = 3
__NUM_ROWS: int = 4

__COLUMN_WIDTH: float = 1.0
__ROW_HEIGHT: float = 0.6

__DIS_GROUPS: list[tuple[float, float]] = [
    (0.0, 0.0), #G1
    (0.6, 0.6), #G2
    (1.0, 1.2), #G3
    (1.56, 1.57), #G4
    (1.8, 2.34), #G5
]

__DIR_GROUPS: list[float] = [
    0.0, #EAST
    45.0, #NORTHEAST
    90.0, #NORTH
    135.0, #NORTHWEST
    180.0, #WEST
    225.0, #SOUTHWEST
    270.0, #SOUTH
    315.0, #SOUTHEAST
]

__KEY_POSITIONS: list[tuple[float, float]] = [
    (1.0, 0.0), #0
    (0.0, 1.8), #1
    (1.0, 1.8), #2
    (2.0, 1.8), #3
    (0.0, 1.2), #4
    (1.0, 1.2), #5
    (2.0, 1.2), #6
    (0.0, 0.6), #7
    (1.0, 0.6), #8
    (2.0, 0.6), #9
]

__DIS_TABLE: dict[str, dict[int, set[str]]] | None = None
__DIR_TABLE: dict[str, dict[int, set[str]]] | None = None

def __scale_points__(input_points: list[tuple[float, float]]) -> Generator[list[tuple[float, float]], None, None]:
    global __NUM_COLUMNS, __COLUMN_WIDTH, __NUM_ROWS, __ROW_HEIGHT

    for column_count in range(1, __NUM_COLUMNS + 1):
        x_scale = column_count * __COLUMN_WIDTH

        for row_count in range(1, __NUM_ROWS + 1):
            y_scale = row_count * __ROW_HEIGHT

            yield [(x * x_scale, y * y_scale) for x, y in input_points]

def __get_directions__(angle: float, delta_t: float = 22.5) -> list[int]:
    global __DIR_GROUPS

    min_distance: float = float("inf")
    min_idx: int = -1

    for g_idx in range(len(__DIR_GROUPS)):
        true_angle = __DIR_GROUPS[g_idx]

        lower = (true_angle - delta_t + 360.0) % 360.0
        upper = (true_angle + delta_t) % 360.0

        if lower <= angle <= upper:
            return [g_idx]

        if lower > true_angle:
            if angle >= lower or angle <= upper:
                return [g_idx]

        g_min_distance = abs(angle - true_angle)
        if g_min_distance < min_distance:
            min_idx = g_idx
            min_distance = g_min_distance

    if angle > __DIR_GROUPS[min_idx]:
        return [min_idx, (min_idx + 1) % len(__DIR_GROUPS)]
    
    return [(min_idx - 1 + len(__DIR_GROUPS)) % len(__DIR_GROUPS), min_idx]

def __get_distances__(distance: float) -> list[int]:
    global __DIS_GROUPS

    min_distance: float = float("inf")
    min_idx: int = -1

    for g_idx in range(len(__DIS_GROUPS)):
        min_g, max_g = __DIS_GROUPS[g_idx]

        if min_g <= distance <= max_g:
            return [g_idx]
        
        g_min_distance = min(abs(min_g - distance), abs(max_g - distance))
        if g_min_distance < min_distance:
            min_idx = g_idx
            min_distance = g_min_distance

    if distance < __DIS_GROUPS[min_idx][0] and min_idx != 0:
        return [min_idx - 1, min_idx]
    
    if distance > __DIS_GROUPS[min_idx][1] and min_idx != len(__DIS_GROUPS) - 1:
        return [min_idx, min_idx + 1]
    
    return [min_idx]

def __feature_extraction__(input_points: list[tuple[float, float]], delta_t: float) -> list[tuple[list[int], list[int]]]:
    features: list[tuple[list[int], list[int]]] = []
    last_point = input_points[0]

    for cur_point in input_points[1:]:
        angle = compute_angle_deg(last_point, cur_point)
        distance = compute_distance(last_point, cur_point)

        features.append((__get_directions__(angle, delta_t), __get_distances__(distance)))

        last_point = cur_point

    return features

def __build_dir_table__():
    global __DIR_TABLE, __KEY_POSITIONS, __DIR_GROUPS

    __DIR_TABLE = {}
    for from_idx in range(len(__KEY_POSITIONS)):
        from_key = str(from_idx)
        from_pos = __KEY_POSITIONS[from_idx]

        __DIR_TABLE[from_key] = {}

        for g_idx in range(len(__DIR_GROUPS)):
            __DIR_TABLE[from_key][g_idx] = { from_key }

        for to_idx in range(len(__KEY_POSITIONS)):
            if to_idx == from_idx:
                continue

            to_key = str(to_idx)
            to_pos = __KEY_POSITIONS[to_idx]

            for dir_feature in __get_directions__(compute_angle_deg(from_pos, to_pos), 22.5):
                __DIR_TABLE[from_key][dir_feature].add(to_key)

def __build_dis_table__():
    global __DIS_TABLE, __KEY_POSITIONS, __DIS_GROUPS

    __DIS_TABLE = {}
    for from_idx in range(len(__KEY_POSITIONS)):
        from_key = str(from_idx)
        from_pos = __KEY_POSITIONS[from_idx]

        __DIS_TABLE[from_key] = {}

        for g_idx in range(len(__DIS_GROUPS)):
            __DIS_TABLE[from_key][g_idx] = set()

        for to_idx in range(len(__KEY_POSITIONS)):
            to_key = str(to_idx)
            to_pos = __KEY_POSITIONS[to_idx]

            for dis_feature in __get_distances__(compute_distance(from_pos, to_pos)):
                __DIS_TABLE[from_key][dis_feature].add(to_key)

def quest_3_correlation(input_points: list[tuple[float, float]], delta_t: float = 14.5) -> list[str]:
    global __DIR_TABLE, __DIS_TABLE, __DIS_GROUPS

    match len(input_points):
        case 0:
            return []
        case 1:
            return [str(val) for val in range(10)]
        
    if __DIR_TABLE is None:
        __build_dir_table__()

    if __DIS_TABLE is None:
        __build_dis_table__()

    candidates: set[str] = set()
        
    for scaled_points in __scale_points__(input_points):
        cur_sequences: list[str] = [str(val) for val in range(10)]
        for dir_features, dis_features in __feature_extraction__(scaled_points, delta_t):
            new_sequences: list[str] = []

            for sequence in cur_sequences:
                last_key = sequence[-1]

                for dir_feature in dir_features:
                    dir_keys: set[str] = __DIR_TABLE[last_key][dir_feature]

                    for dis_feature in dis_features:
                        dis_keys: set[str] = __DIS_TABLE[last_key][dis_feature]

                        for key in dir_keys.intersection(dis_keys):
                            new_sequences.append(f"{sequence}{key}")

            cur_sequences = new_sequences

        for sequence in cur_sequences:
            candidates.add(sequence)    
    
    return list(candidates)