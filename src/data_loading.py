"""Scripts to load raw data from shared folder."""

import os

# ----------------------- Data  Paths -----------------------#
SRC_DIR = "/home/shared/data_raw/SRC/"
BLUEPRINTS_DIR_NAME = "polycam_blueprints"
SLAT_PLY_DIR_NAME = "splat_plys"

BLUE_PRINT_PATH = os.path.join(SRC_DIR, BLUEPRINTS_DIR_NAME)
SLAT_PLY_PATH = os.path.join(SRC_DIR, SLAT_PLY_DIR_NAME)
# ----------------------------------------------------------#
