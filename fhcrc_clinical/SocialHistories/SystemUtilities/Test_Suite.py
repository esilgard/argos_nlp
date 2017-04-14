from Extraction.AttributeExtraction.Processing_CRFSuite import standardize_tokens

# Test the standardize tokens function
print(standardize_tokens(["He","stopped","smoking","in","1995", ",", "nearly", "25", "years", "ago"]))
print(standardize_tokens(["she","smokes","1ppd","since","the", "80s"]))
print(standardize_tokens(["TOBACCO:","32-pack-yr",",","quit", "1/30"]))
print(standardize_tokens(["smoked","3-4","pack-years"]))
print(standardize_tokens(["smoked","80","pack-years"]))
print(standardize_tokens(["PLease","call","1-800-999-9999"]))
print(standardize_tokens(["she","smokes","1/2ppd", "since", "1980s"]))
print(standardize_tokens(["5yr","smoking","history"]))
print(standardize_tokens(["TOBACCO:","32-pack-yr",",","quit", "1/30/2019"]))
print(standardize_tokens(["TOBACCO:","32-pack-yr",",","quit", "1-30-99"]))
print(standardize_tokens(["TOBACCO:","32-pack-yr",",","quit", "1/30/13"]))
print(standardize_tokens(["TOBACCO:","32-pack-yr",",","quit", "1/30/1313"]))
print(standardize_tokens(["TOBACCO:","32yrs",",","quit", "1/30/1313"]))
print(standardize_tokens(["TOBACCO:","32weeks",",","quit", "1/30/1313"]))
