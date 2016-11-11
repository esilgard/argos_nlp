# Contains tunable system parameters
import os
from fhcrc_clinical.SocialHistories.SystemUtilities.Globals import *

# Environment/run type
ENV = RUNTIME_ENV.TEST

# Data directories
DATA_DIR = "/home/wlane/Documents/Substance_IE_Data/"
MODEL_DIR = os.path.join(DATA_DIR, "resources", "Models")
ATTRIB_EXTRACTION_DIR_HOME = DATA_DIR + "AttributeExtractionModels/"
