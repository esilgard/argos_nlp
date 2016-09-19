# Contains tunable system parameters
import os
from fhcrc_clinical.SocialHistories.SystemUtilities.Globals import *

# Environment/run type
ENV = RUNTIME_ENV.TEST

# Data directories
DATA_DIR = "/home/wlane/Documents/Substance_IE_Data/"
MODEL_DIR = os.path.join(DATA_DIR, "resources", "Models")

# Stanford tools
STANFORD_NER_PATH = DATA_DIR + "stanford-ner-2015-12-09/stanford-ner.jar"
STANFORD_NER_LIB_ALL = DATA_DIR + "stanford-ner-2015-12-09/lib/*:"
ATTRIB_EXTRACTION_DIR_HOME = DATA_DIR + "AttributeExtractionModels/"
