import fhcrc_clinical.SocialHistories.Preprocessing.generate_notes
import fhcrc_clinical.SocialHistories.Preprocessing.filter_for_keywords
import fhcrc_clinical.SocialHistories.Preprocessing.split_into_f
import fhcrc_clinical.SocialHistories.SystemUtilities.Configuration as c

# Generate individual notes based on the results from the sql query
from fhcrc_clinical.SocialHistories import Preprocessing

print("Calling the note generation module...")
Preprocessing.generate_notes.main()

# split into dev, train, and test
print("Filtering data into dev train and test folders ...")
Preprocessing.split_into_f.main(c.NOTE_OUTPUT_DIR)
# Filter full list of documents for keywords (smoking, tobacco), and produce
#  a list of which ones need annotations
print("Calling the keyword filter module")
Preprocessing.filter_for_keywords.main()

print "Done."

