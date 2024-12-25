from os import mkdir, listdir
from os.path import join, isdir
from multiprocessing import Pool
from motion_decipher import run_motion_decipher, logger


"""
Change the variable TEST_CASE_FOLDER to the relative path
of the directory containing the 'videos' and 'keypresses'
folders you'd like to run.

Change the variable TEST_CASE_FILE to the name of the video
file you'd like to run, or None to run all videos in the
directory.

Change the variable OUTPUT_FOLDER to the relative path
you'd like to save the list of candidates for each PIN.

Change the variable VIEWING_ANGLE to alter the test(s) horizontal angle.

Change the variable MAX_PROCESSES to the value of 1 for a standard synchronous
single-process run, or larger if you'd like to run numerous tests at a time.
"""
TEST_CASE_FOLDER: str = "./tests"
TEST_CASE_FILE: str | None = None
OUTPUT_FOLDER: str = "./output"
VIEWING_ANGLE: float = 90.0
MAX_PROCESSES: int = 10

def handle_proc(
    videos_path: str,
    keypresses_path: str,
    video_filename: str
):
    if not video_filename.endswith(".mp4"):
            return

    target_sequence = video_filename.replace(".mp4", "").strip()
    video_keypresses_path: str = join(keypresses_path, target_sequence)

    presses: list[tuple[int, int]] = []
    for idx in range(1, len(target_sequence) + 1):
        min_idx = 999_999_999
        max_idx = -999_999_999

        cur_press_path: str = join(video_keypresses_path, str(idx))
        for press_img in listdir(cur_press_path):
            if not press_img.endswith(".jpg"):
                continue

            img_idx = int(press_img.replace(".jpg", "").strip())
            min_idx = min(min_idx, img_idx)
            max_idx = max(max_idx, img_idx)

        if min_idx > max_idx:
            continue

        presses.append((min_idx, max_idx))

    candidates = run_motion_decipher(
        join(videos_path, video_filename),
        target_sequence,
        presses,
        VIEWING_ANGLE
    )

    out_file = open(join(OUTPUT_FOLDER, target_sequence + ".txt"), "w")
    for candidate in candidates:
        out_file.write(candidate + "\n")
    out_file.close()

def main():
    videos_path: str = join(TEST_CASE_FOLDER, "videos")
    keypresses_path: str = join(TEST_CASE_FOLDER, "keypresses")

    if TEST_CASE_FILE is not None:
        handle_proc(videos_path, keypresses_path, TEST_CASE_FILE)
        return

    video_filenames = listdir(videos_path)
    video_filenames.sort()

    if MAX_PROCESSES <= 1:
        for video_filename in video_filenames:
            handle_proc(videos_path, keypresses_path, video_filename)

        return
    
    arguments = [(
        str(videos_path),
        str(keypresses_path),
        video_filename,
    ) for video_filename in video_filenames]

    process_pool = Pool(processes=min(MAX_PROCESSES, len(arguments)))
    process_pool.starmap(handle_proc, arguments)


if __name__ == "__main__":
    try:
        if not isdir(OUTPUT_FOLDER):
            mkdir(OUTPUT_FOLDER)
        main()
    except Exception as e:
        logger.log_error(f"{e}")