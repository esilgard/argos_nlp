# Contains tunable system parameters
import os

# Data directories
cur_dir_path = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(cur_dir_path, "..", "DataDir")
MODEL_DIR = os.path.join(DATA_DIR, "SVMModels")
ATTRIB_EXTRACTION_DIR_HOME = os.path.join(DATA_DIR, "CRFModels")
