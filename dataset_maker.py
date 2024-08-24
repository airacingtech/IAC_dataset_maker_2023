import os 
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

if env_ranges is None:
    raise ValueError("RANGES environment variable is not set in the .env file")

# Convert the environment variable to a numpy array
ranges = ast.literal_eval(env_ranges)
ranges = np.array(ranges)

print("The ranges to keep are: ")
print(ranges)

# ------------- Create Destination Directory if it does not exist ------------ #
if not os.path.isdir(DEST_DIR):
    print(f"DEST_DIR ({DEST_DIR}) did not exist so creating it.")
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
