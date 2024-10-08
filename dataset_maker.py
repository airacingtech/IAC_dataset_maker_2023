import os 
import subprocess
import shutil
import ast
import numpy as np
from tqdm import tqdm
from environs import Env


# Load Environment Variables
# Get current directory
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
env = Env()
env.read_env(os.path.join(CURRENT_DIR, "data_maker.env"))

SOURCE_DIR = env("SOURCE_DIR")

if SOURCE_DIR is None:
    raise ValueError("SOURCE_DIR environment variable is not set in the .env file")

DEST_DIR = os.path.join(SOURCE_DIR, "filtered")
INV_DEST_DIR = os.path.join(SOURCE_DIR, "inverse_filtered")

env_ranges = os.getenv("RANGES")
FRAME_RATE = np.double(os.getenv("FRAME_RATE"))

MAKE_VID_DEFAULT = os.getenv("MAKE_VID_DEFAULT")

if env_ranges is None:
    raise ValueError("RANGES environment variable is not set in the .env file")

# Convert the environment variable to a numpy array
ranges = ast.literal_eval(env_ranges)
ranges = np.array(ranges) * FRAME_RATE

print("The ranges to keep are: ")
print(ranges)

# ------------- Create Destination Directories if they do not exist ------------ #
def create_dir_if_not_exists(dir):
    if not os.path.isdir(dir):
        print(f"{dir} did not exist so creating it.")
        os.makedirs(dir)
    else:
        print(f"Deleting {dir} recreating it.")
        shutil.rmtree(dir)
        os.makedirs(dir)

create_dir_if_not_exists(DEST_DIR)
create_dir_if_not_exists(INV_DEST_DIR)
# ------------- Get the source directory files ------------ #

print("Scanning Source Directory: " + SOURCE_DIR + "\n")
print("This operation may take a while if source directory has too many files...\n\n")
# Get the list of files in the source directory excluding directories (/filtered and /inverse_filtered directories)
source_file_list = [x for x in os.listdir(SOURCE_DIR) if os.path.isfile(os.path.join(SOURCE_DIR, x))]
source_file_list = sorted(source_file_list, key=str.lower)
print("Scan Done")

# ------------- Create the inverted filter ------------ #
# Get the inverse of the ranges
def get_inverse_ranges(ranges, total_length):
    inverse_ranges = []
    current_start = 0

    # Iterate through the sorted ranges
    for start, end in ranges:
        if current_start <= start:
            inverse_ranges.append([current_start, start - 1])
        current_start = end + 1

    # Handle the case after the last range
    dist_from_end = total_length - current_start
    if dist_from_end > 0:
        # We don't want to add inverse frames that are less than a second of video time as
        # the normal range could be set to go to the end of the video (130/130) but the inverse
        # will have a couple of extra frames to work with after the last range (130/130 + 1/130)
        # which the user can't control. So we will only add the inverse range if it is less than
        # a second of video time.
        if dist_from_end < FRAME_RATE:
            inverse_ranges.append([current_start, total_length])

    return np.array(inverse_ranges)

inv_range = get_inverse_ranges(ranges, len(source_file_list))

print("The inverse range is")
print(inv_range)

# ------------- Copy the files to the destination directories ------------ #
def copy_ranges(ranges, source_file_list, source_dir, dest_dir):
    # Remove directories from source_file_list if any
    count = 0
    total_to_be_copied = 0
    iter_array = None
    for i in range(0, len(ranges)):
        if iter_array is None:
            iter_array = np.arange(ranges[i][0], ranges[i][1], dtype=np.uint)
        else:
            iter_array = np.append(iter_array, np.arange(ranges[i][0], ranges[i][1], dtype=np.uint))
        total_to_be_copied += ranges[i][1] - ranges[i][0]

    print("Now copying data from:\n" + source_dir + "\nto:\n" + str(dest_dir) + "\n")

    print(f"Max files to be copied are {total_to_be_copied} out of a total of {len(source_file_list)}")

    for tqdm_iter in tqdm(iter_array):
        source_file = source_file_list[tqdm_iter]
        file_words = source_file.split('_')
        shutil.copy(source_dir + '/' + source_file, dest_dir)
        count += 1

    return count

# Copy filtered files into /filtered directory
count_filtered = copy_ranges(ranges, source_file_list, SOURCE_DIR, DEST_DIR)

# Copy the inverted filtered files into /inverse_filtered directory
count_inv = copy_ranges(inv_range, source_file_list, SOURCE_DIR, INV_DEST_DIR)

# Save metadata to file
f = open(DEST_DIR + "/num_data.txt", "w+")
f.write(f"Total frames extracted in range: {count_filtered}")
f.write(f"Filtered frames {range}")
f.write(f"Inverse of filtered frames {inv_range}")
f.close()

# Turn newly filtered extracted images into video
if MAKE_VID_DEFAULT:
    # Normal Filter
    VIDEO_DEST_DIR = DEST_DIR + "/video"
    # Make video directory if it does not exist
    create_dir_if_not_exists(VIDEO_DEST_DIR)
    video_name = DEST_DIR.split("/")[-3] + '_' + DEST_DIR.split("/")[-2]
    subprocess.run(
        ["ffmpeg", "-framerate", str(FRAME_RATE), "-pattern_type", "glob",
        "-i", "*.jpg", "-c:v", "libx264", "-profile:v", "high", "-crf", "20", "-pix_fmt", "yuv420p",
        f"{video_name}.mp4"],
        cwd=DEST_DIR,
        capture_output=False,
        text=True,
    )
    # Move video to the video directory
    shutil.move(DEST_DIR + f"/{video_name}.mp4", VIDEO_DEST_DIR)

    # Inverted Filter
    INV_VIDEO_DEST_DIR = INV_DEST_DIR + "/video"
    # Make video directory if it does not exist
    create_dir_if_not_exists(INV_VIDEO_DEST_DIR)
    video_name = INV_DEST_DIR.split("/")[-3] + '_inverted_' + INV_DEST_DIR.split("/")[-2]
    subprocess.run(
        ["ffmpeg", "-framerate", str(FRAME_RATE), "-pattern_type", "glob",
        "-i", "*.jpg", "-c:v", "libx264", "-profile:v", "high", "-crf", "20", "-pix_fmt", "yuv420p",
        f"{video_name}.mp4"],
        cwd=INV_DEST_DIR,
        capture_output=False,
        text=True,
    )
    # Move video to the video directory
    shutil.move(INV_DEST_DIR + f"/{video_name}.mp4", VIDEO_DEST_DIR)
