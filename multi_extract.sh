#!/bin/sh

# Source ROS IRON
echo "Sourcing ROS2 IRON"
source /opt/ros/iron/setup.bash

# ---------------------------------------------------------------------------- #
#                               DEFAULT VARIABLES                              #
# ---------------------------------------------------------------------------- #
# Load data_maker.env file
source data_maker.env
echo "Loaded data_maker.env file to set default variables"

# ---------------------------------------------------------------------------- #
#                          PARSE ENVIRONMENT VARIABLES                         #
# ---------------------------------------------------------------------------- #

# --------------------------- ROSBAG DATA DIRECTORY -------------------------- #
if [ -z ${DATA_DIR+x} ]; then
    echo "----------------------------------------------------------------------------"
    echo "                         DATA_DIR not defined.                              "
    DATA_DIR=$DATA_DIR_DEFAULT
    echo "Defaulting DATA_DIR=$DATA_DIR"
    echo "----------------------------------------------------------------------------"
else
    echo "----------------------------------------------------------------------------"
    echo "DATA_DIR has been defined as $DATA_DIR"
    echo "----------------------------------------------------------------------------"
fi

# --------------------- EXTRACTION OUTPUT BASE DIRECTORY --------------------- #
if [ -z ${OUTPUT_BASE_DIR+x} ]; then
    echo "----------------------------------------------------------------------------"
    echo "                      OUTPUT_BASE_DIR not defined.                          "
    OUTPUT_BASE_DIR=$OUTPUT_BASE_DIR_DEFAULT
    echo "Defaulting OUTPUT_BASE_DIR=$OUTPUT_BASE_DIR"
    echo "----------------------------------------------------------------------------"
else
    echo "----------------------------------------------------------------------------"
    echo "OUTPUT_BASE_DIR has been defined as $OUTPUT_BASE_DIR"
    echo "----------------------------------------------------------------------------"
fi

# ---------------------------- VERBOSITY SETTINGS ---------------------------- #
if [ -z ${VERBOSE+x} ]; then
    echo "----------------------------------------------------------------------------"
    VERBOSE=$VERBOSE_DEFAULT
    echo "               VERBOSE not defined. Setting VERBOSE to $VERBOSE.                   "
    echo "----------------------------------------------------------------------------"
else
    echo "----------------------------------------------------------------------------"
    echo "                       VERBOSE has been defined as $VERBOSE                 "
    echo "----------------------------------------------------------------------------"
fi

# ------------------------ USE_COMPRESSED SETTINGS --------------------------- #
if [ -z ${USE_COMPRESSED+x} ]; then
    echo "----------------------------------------------------------------------------"
    USE_COMPRESSED=$USE_COMPRESSED_DEFAULT
    echo "               USE_COMPRESSED not defined. Setting USE_COMPRESSED to $USE_COMPRESSED.                   "
    echo "----------------------------------------------------------------------------"
else
    echo "----------------------------------------------------------------------------"
    echo "                       USE_COMPRESSED has been defined as $USE_COMPRESSED                 "
    echo "----------------------------------------------------------------------------"
fi

# --------------------------- UNDISTORTION SETTINGS -------------------------- #
if [ -z ${UNDISTORT:+x} ]; then
    echo "----------------------------------------------------------------------------"
    UNDISTORT=$UNDISTORT_DEFAULT
    echo "              UNDISTORT not defined. Setting UNDISTORT to $UNDISTORT.                "
    echo "----------------------------------------------------------------------------"
else
    echo "----------------------------------------------------------------------------"
    echo "                      UNDISTORT has been defined as $UNDISTORT              "
    echo "----------------------------------------------------------------------------"
fi
if [ $UNDISTORT -eq 1 ]; then
    if [ -z ${CALIB_DIR+x} ]; then
        echo "----------------------------------------------------------------------------"
        echo "                         CALIB_DIR not defined.                             "
        CALIB_DIR=$CALIB_DIR_DEFAULT
        echo "Defaulting CALIB_DIR=$CALIB_DIR"
        echo "----------------------------------------------------------------------------"
    else
        echo "----------------------------------------------------------------------------"
        echo "CALIB_DIR has been defined as $CALIB_DIR"
        echo "----------------------------------------------------------------------------"
    fi
fi

# ---------------------------- MAKE_VID SETTINGS ---------------------------- #
if [ -z ${MAKE_VID+x} ]; then
    echo "----------------------------------------------------------------------------"
    MAKE_VID=$MAKE_VID_DEFAULT
    echo "               MAKE_VID not defined. Setting MAKE_VID to $MAKE_VID_DEFAULT.                   "
    echo "----------------------------------------------------------------------------"
else
    echo "----------------------------------------------------------------------------"
    echo "                       MAKE_VID has been defined as $MAKE_VID                 "
    echo "----------------------------------------------------------------------------"
fi
# --------------------- ENVIRONMENT VARIABLE PARSING END --------------------- #

echo "\nPausing for 5 seconds. Press Ctrl+C to quit if the above settings are not correct.\n"
for i in 1 2 3 4 5 
do
  echo "$i seconds passed"
  sleep 1s
done


# ---------------------------------------------------------------------------- #
#                 Find all rosbags at datadir and extract data                 #
# ---------------------------------------------------------------------------- #
echo "\n\nSearching DATA_DIR for ROSBAGS now...\n"
root_dir=$(pwd)
sleep 2s
# find "$DATA_DIR" \( -iname "*.db3" -o -iname "*.mcap" \) -print0 | xargs -0 -I file dirname file | while read d; do
# find "$DATA_DIR" \( -iname "*.db3" -o -iname "*.mcap" \) -print0 | xargs -0 -I file dirname file | sort -u | while IFS= read -r d; do
#     echo "$d"
# done
find "$DATA_DIR" \( -iname "*.db3" -o -iname "*.mcap" \) -print0 | xargs -0 -I file dirname file | sort -u > /tmp/tempfile.txt


# find "$DATA_DIR" \( -iname "*.db3" -o -iname "*.mcap" \) -print0 | xargs -0 -I file dirname file | sort -u | while IFS= read -r d; do
while IFS= read -r line; do

    ROSBAG_NAME=$(basename "$line")
    # echo "ROSBAG_NAME $ROSBAG_NAME"

    # ---------------------------------------------------------------------------- #
    #                           NOTE: SPECIFY OUTPUT DIR                           #
    # ---------------------------------------------------------------------------- #
    OUTPUT_DIR="${OUTPUT_BASE_DIR}${ROSBAG_NAME}_${OUTPUT_NAME_SUFFIX}"
    
    # ------------------- NO CHANGES REQUIRED BEYOND THIS LINE ------------------- #

    # ------------------------------ Debug Verbosity ----------------------------- #
    echo "----------------------------------------------------------------------------"
    echo "Found ROSBAG:              $line"
    echo "Extracting images to:      $OUTPUT_DIR"
    echo "----------------------------------------------------------------------------"

    # -------------------------- Create output Directory ------------------------- #
    mkdir -p "$OUTPUT_DIR"

    # ------------------ Begin Extraction Based on User Setting ------------------ #
    cd "$root_dir"
    
    if [ $VERBOSE -eq 1 ]; then
        if [ $UNDISTORT -eq 1 ]; then
            if [ $USE_COMPRESSED -eq 1 ]; then
                echo "Running: python3 ros2bag_image_extractor.py $line $OUTPUT_DIR -vucp $CALIB_DIR"
                python3 ros2bag_image_extractor.py "$line" "$OUTPUT_DIR" -vucp "$CALIB_DIR"
            else 
                echo "Running: python3 ros2bag_image_extractor.py $line $OUTPUT_DIR -vup $CALIB_DIR"
                python3 ros2bag_image_extractor.py "$line" "$OUTPUT_DIR" -vup "$CALIB_DIR"
            fi
        else 
            if [ $USE_COMPRESSED -eq 1 ]; then
                echo "Running: python3 ros2bag_image_extractor.py $line $OUTPUT_DIR -vc"
                python3 ros2bag_image_extractor.py "$line" "$OUTPUT_DIR" -vc
            else
                echo "Running: python3 ros2bag_image_extractor.py $line $OUTPUT_DIR -v"
                python3 ros2bag_image_extractor.py "$line" "$OUTPUT_DIR" -v
            fi
        fi
    else
        if [ $UNDISTORT -eq 1 ]; then
            if [ $USE_COMPRESSED -eq 1 ]; then
                echo "Running: python3 ros2bag_image_extractor.py $line $OUTPUT_DIR -ucp $CALIB_DIR"
                python3 ros2bag_image_extractor.py "$line" "$OUTPUT_DIR" -ucp "$CALIB_DIR"
            else 
                echo "Running: python3 ros2bag_image_extractor.py $line $OUTPUT_DIR -up $CALIB_DIR"
                python3 ros2bag_image_extractor.py "$line" "$OUTPUT_DIR" -up "$CALIB_DIR"
            fi
        else
            if [ $USE_COMPRESSED -eq 1 ]; then
                echo "Running: python3 ros2bag_image_extractor.py $line $OUTPUT_DIR -c"
                python3 ros2bag_image_extractor.py "$line" "$OUTPUT_DIR" -c
            else
                echo "Running: python3 ros2bag_image_extractor.py $line $OUTPUT_DIR"
                python3 ros2bag_image_extractor.py "$line" "$OUTPUT_DIR"
            fi
        fi
    fi

    echo "Converting images to video... for $OUTPUT_DIR"
    cd $OUTPUT_DIR
    # --------------------- Convert Extracted Images to Video -------------------- #
    if [[ -d "$OUTPUT_DIR" ]] && [[ -n "$(ls -A "$OUTPUT_DIR")" ]]; then
        # Check if the output directory exists and is not empty
        if [[ $MAKE_VID -eq 1 ]]; then
            for camera_output_dir in "$OUTPUT_DIR"/*/; do
                base_name=$(basename "$camera_output_dir")
                echo "Creating mp4 for $camera_output_dir"
                mkdir -p "./output/$ROSBAG_NAME"
                # Redirecting ffmpeg's standard input to /dev/null to avoid interference with the loop reading
                ffmpeg -framerate 50 -pattern_type glob -i "$camera_output_dir/*.jpg" -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p "./output/$ROSBAG_NAME/$base_name.mp4" > /dev/null 2>&1 < /dev/null
            done
        fi
    fi
    sleep 1s
# done
echo "Done!"
done < /tmp/tempfile.txt

rm /tmp/tempfile.txt
# find $OUTPUT_BASE_DIR_DEFAULT -type d -empty -delete # Cleanup Empty Directories
