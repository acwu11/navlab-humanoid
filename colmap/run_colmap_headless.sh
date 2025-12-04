#!/usr/bin/env bash
#
# Run COLMAP automatic reconstruction
# Usage:
#   ./run_colmap.sh /path/to/project 
#
# The project folder must contain a folder named "images" with all images.

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 /path/to/project" 
    exit 1
fi

DATASET_PATH="$1"
IMG_DIR="$DATASET_PATH/images"

if [ ! -d "$IMG_DIR" ]; then
    echo "Error: '$IMG_DIR' does not exist."
    exit 1
fi

echo ">>> Converting HEIF/HEIC files to PNG..."
if command -v heif-convert >/dev/null 2>&1; then
    CONVERT_HEIF="heif-convert"
elif command -v magick >/dev/null 2>&1; then
    CONVERT_HEIF="magick convert"
elif command -v ffmpeg >/dev/null 2>&1; then
    CONVERT_HEIF="ffmpeg -y -i"
else
    echo "ERROR: No converter found (install heif-convert, ImageMagick, or ffmpeg)."
    exit 1
fi
shopt -s nullglob
for f in "$IMG_DIR"/*.heif "$IMG_DIR"/*.HEIF "$IMG_DIR"/*.heic "$IMG_DIR"/*.HEIC; do
    out="${f%.*}.png"
    if [ -f "$out" ]; then
        echo "  Skipping $f → $out (already exists)"
        continue
    fi
    echo "  $f -> $out"
    $CONVERT_HEIF "$f" "$out"
done
shopt -u nullglob
echo ">>> Done converting images."


if [ ! -d "$DATASET_PATH/images" ]; then
    echo "Error: '$DATASET_PATH/images' does not exist."
    exit 1
fi

echo ">>> Running COLMAP (headless)..."
export QT_QPA_PLATFORM=offscreen

conda run -n airbus_autocalib colmap feature_extractor \
    --database_path $DATASET_PATH/database.db \
    --image_path $DATASET_PATH/images \
    --SiftExtraction.use_gpu 0

conda run -n airbus_autocalib colmap exhaustive_matcher \
    --database_path $DATASET_PATH/database.db \
    --SiftMatching.use_gpu 0

mkdir -p $DATASET_PATH/sparse

conda run -n airbus_autocalib colmap mapper \
    --database_path $DATASET_PATH/database.db \
    --image_path $DATASET_PATH/images \
    --output_path $DATASET_PATH/sparse


conda run -n airbus_autocalib colmap model_converter \
    --input_path $DATASET_PATH/sparse/0 \
    --output_path $DATASET_PATH/sparse/0 \
    --output_type TXT

mkdir -p $DATASET_PATH/dense

conda run -n airbus_autocalib colmap image_undistorter \
    --image_path $DATASET_PATH/images \
    --input_path $DATASET_PATH/sparse/0 \
    --output_path $DATASET_PATH/dense \
    --output_type COLMAP \
    --max_image_size 2000

conda run -n airbus_autocalib colmap patch_match_stereo \
    --workspace_path $DATASET_PATH/dense \
    --workspace_format COLMAP \
    --PatchMatchStereo.geom_consistency true

conda run -n airbus_autocalib colmap stereo_fusion \
    --workspace_path $DATASET_PATH/dense \
    --workspace_format COLMAP \
    --input_type geometric \
    --output_path $DATASET_PATH/dense/fused.ply

conda run -n airbus_autocalib colmap poisson_mesher \
    --input_path $DATASET_PATH/dense/fused.ply \
    --output_path $DATASET_PATH/dense/meshed-poisson.ply

conda run -n airbus_autocalib colmap delaunay_mesher \
    --input_path $DATASET_PATH/dense \
    --output_path $DATASET_PATH/dense/meshed-delaunay.ply
