import cv2 as cv
import mediapipe as mp


class Triangle:
    __point_a_x: float
    __point_a_y: float

    __point_b_x: float
    __point_b_y: float

    __point_c_x: float
    __point_c_y: float

    def __init__(
        self,
        a_x: float,
        a_y: float,

        b_x: float,
        b_y: float,

        c_x: float,
        c_y: float,
    ):
        __PRECISION_SCALING: float = 1_000
        
        self.__point_a_x = a_x * __PRECISION_SCALING
        self.__point_a_y = a_y * __PRECISION_SCALING
        self.__point_b_x = b_x * __PRECISION_SCALING
        self.__point_b_y = b_y * __PRECISION_SCALING
        self.__point_c_x = c_x * __PRECISION_SCALING
        self.__point_c_y = c_y * __PRECISION_SCALING

    def get_area(self) -> float:
        return abs(0.5 * (
            self.__point_a_x * (self.__point_b_y - self.__point_c_y) +
            self.__point_b_x * (self.__point_c_y - self.__point_a_y) +
            self.__point_c_x * (self.__point_a_y - self.__point_b_y)
        ))

    def get_x(self) -> float:
        return self.__point_a_x

    def get_y(self) -> float:
        return self.__point_a_y

def pose_estimation(
    frames: list[cv.Mat],
    point_a: int = 0,
    point_b: int = 5,
    point_c: int = 17,
) -> list[Triangle]:
    if len(frames) == 0:
        return []

    hand_poses: list[Triangle] = []

    with mp.solutions.hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.3,
        min_tracking_confidence=0.3
    ) as hand_model:
        for frame in frames:
            results = hand_model.process(frame)

            if not results.multi_hand_landmarks:
                continue

            hand_marks = results.multi_hand_landmarks[0]
            hand_poses.append(Triangle(
                hand_marks.landmark[point_a].x,
                hand_marks.landmark[point_a].y,
                
                hand_marks.landmark[point_b].x,
                hand_marks.landmark[point_b].y,

                hand_marks.landmark[point_c].x,
                hand_marks.landmark[point_c].y,
            ))

    return hand_poses