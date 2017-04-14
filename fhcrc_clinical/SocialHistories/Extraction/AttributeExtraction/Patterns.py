import re


def matches_TIMEEXPR(word):
    time_expressions = {"day", "days", "wks", "week", "weeks", "mths", "mnths", "months", "month", "yr", "yrs", "years", "year", "decade", "decades"}
    return word in time_expressions

def matches_NUM(word):
    if re.match("one|two|three|four|five|six|seven|eight|nine|ten", word) is not None \
            or re.match("^[0-9]{1,3}$", word) is not None \
            or re.match("^[0-9]*\.[0-9]+", word) is not None \
            or re.match("^[0-9]{1,3}-[0-9]{1,3}$", word) is not None:
        return True
    return False


def matches_YEARNUM(word):
    if re.match("[0-9]{4}(')?(s)?$", word) is not None or \
            re.match("[0-9]{2}s$", word):
        return True
    return False


def matches_NUMWORDSHAPE(word):
        # 1 or 2 numbers in a row directly attached to sequence of letters is an AMOUNT
        if re.match("(.)*[0-9]{1,2}(/[0-9])*[a-zA-Z]*", word) is not None:
            return True


print ("1995 matches NUM -> "+ str(matches_NUM("1995")))
print ("Years smokeing: 25 -> "+ str(matches_NUM("25")))