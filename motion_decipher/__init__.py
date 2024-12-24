import cv2 as cv
from math import sin, cos, pi
import motion_decipher.logger as logger
from motion_decipher.math import normalize_3d
from motion_decipher.keypad import Keypad, META_QUEST_3_KEYPAD
from motion_decipher.pose_estimation import Triangle, pose_estimation

def run_motion_decipher(
    video_path: str,
    target_sequence: str,
    presses: list[tuple[int, int]],
    view_angle: float,
    angle_ambiguous: list[float],
    dist_ambiguous: list[tuple[float, float]],
    target_keypad: Keypad = META_QUEST_3_KEYPAD
) -> list[str]:
    logger.log_info(f"Starting Case {target_sequence}.")

    if len(presses) == 0:
        logger.log_warning("No Press Events Provided...")
        return []
    
    press_idx: int = 0
    frame_idx: int = 0
    triangles: list[Triangle] = []
    video_capture = cv.VideoCapture(video_path)

    while video_capture.isOpened():
        has_data, frame = video_capture.read()
        if not has_data:
            break

        if frame_idx >= presses[press_idx][0]:
            if frame_idx <= presses[press_idx][1]:
                frame_triangles = pose_estimation([
                    cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                ])

                if len(frame_triangles) > 0:
                    triangles.append(frame_triangles[0])
                    press_idx += 1

                    if press_idx >= len(presses):
                        break
            else:
                press_idx += 1

                if press_idx >= len(presses):
                    break

        frame_idx += 1

    video_capture.release()

    logger.log_info("Finished Extracting Video Information.")

    points_3d: list[tuple[float, float, float]] = normalize_3d([
        (t.get_x(), t.get_y(), t.get_area())
        for t in triangles
    ])

    view_radians: float = view_angle * pi / 180.0
    points_2d: list[tuple[float, float]] = [
        (
            (1.0 - x) * cos(view_radians) + (1.0 - z) * sin(view_radians),
            1.0 - y
        ) for x, y, z in points_3d
    ]

    logger.log_info("Finished Keyboard Reconstruction.")

    min_list: list[str] | None = None

    for dist in dist_ambiguous:
        for angle in angle_ambiguous:
            cur_list = target_keypad.infer_candidates(
                points_2d,
                angle,
                dist
            )

            if target_sequence not in cur_list:
                continue

            if min_list is None or len(cur_list) < len(min_list):
                min_list = cur_list

    if min_list is None:
        logger.log_error(f"Failure Case {target_sequence}...")
        return []

    logger.log_success(f"Success Case {target_sequence}!")
    return min_list

