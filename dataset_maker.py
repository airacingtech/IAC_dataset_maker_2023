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

env_ranges = os.getenv("RANGES")
FRAME_RATE = os.getenv("FRAME_RATE")

MAKE_VID_DEFAULT = os.getenv("MAKE_VID_DEFAULT")

if env_ranges is None:
    raise ValueError("RANGES environment variable is not set in the .env file")

# Convert the environment variable to a numpy array
ranges = ast.literal_eval(env_ranges)
ranges = np.array(ranges) * np.double(FRAME_RATE)

print("The ranges to keep are: ")
print(ranges)

# ------------- Create Destination Directory if it does not exist ------------ #
if not os.path.isdir(DEST_DIR):
    print(f"DEST_DIR ({DEST_DIR}) did not exist so creating it.")
    os.makedirs(DEST_DIR)
else:
    print(f"Deleting DEST_DIR ({DEST_DIR}) recreating it.")
    shutil.rmtree(DEST_DIR)
    os.makedirs(DEST_DIR)

print("Scanning Source Directory: " + SOURCE_DIR + "\n")
print("This operation may take a while if source directory has too many files...\n\n")
source_file_list = os.listdir(SOURCE_DIR)
source_file_list = sorted(source_file_list, key=str.lower)
print("Scan Done")

count = 0
total_to_be_copied = 0
iter_array = None
for i in range(0, len(ranges)):
    if iter_array is None:
        iter_array = np.arange(ranges[i][0], ranges[i][1], dtype=np.uint)
    else:
        iter_array = np.append(iter_array, np.arange(ranges[i][0], ranges[i][1], dtype=np.uint))
    total_to_be_copied += ranges[i][1] - ranges[i][0]

print("Now copying data from:\n" + SOURCE_DIR + "\nto:\n" + str(DEST_DIR) + "\n")

print(f"Max files to be copied are {total_to_be_copied} out of a total of {len(source_file_list)}")

for tqdm_iter in tqdm(iter_array):
    source_file = source_file_list[tqdm_iter]
    file_words = source_file.split('_')

    # if not os.path.exists(os.path.join(SOURCE_DIR, source_file)):
    shutil.copy(SOURCE_DIR + '/' + source_file, DEST_DIR)
    count += 1

print(count)
f = open(DEST_DIR + "/num_data.txt", "w+")
f.write(f"{count}")
f.close()

# Turn newly filtered extracted images into video
if MAKE_VID_DEFAULT:
    video_name = DEST_DIR.split("/")[-3] + '_' + DEST_DIR.split("/")[-2]
    subprocess.run(
        ["ffmpeg", "-framerate", FRAME_RATE, "-pattern_type", "glob",
        "-i", "*.jpg", "-c:v", "libx264", "-profile:v", "high", "-crf", "20", "-pix_fmt", "yuv420p",
        f"{video_name}.mp4"],
        cwd=DEST_DIR,
        capture_output=False,
        text=True,
    )
