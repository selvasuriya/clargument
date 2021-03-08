import re
import functools

"""
an arg
    an arg is any string

an escaped arg
    an arg starting with '-' character

    Unescaping
        unescaping is the process of removing the escape from an arg
        i.e, remove the first '-' character to unescape an escaped arg

a doubly escaped arg
    this arg is also an escaped arg
    an unescaped arg starting with '-' character, i.e an arg escaped twice
    
    Unescaping
        unescaping an unescaped doubly escaped arg will result in the removal of the double escaping

a singly escaped arg
    any escaped arg which is't a doubly escaped arg

direct arg
    an arg with no escape is a direct arg

dataarg
    any data extracted from the arg that is meaningfully an input from the user

short input name
    a data arg consisting of a single character from the english alphabet
    this data arg only originates from singly escaped args

    Data Validation
        which is present in the list of short input names

long input name
    a data arg consisting of more than a single character
    this data arg only originates from doubly escaped args

    Data Validation
        which is present in the list of long input names

grouped short input names
    a data arg consisting of more than a single character from the english alphabet
    this data arg only originates from singly escaped args

    Data Validation
        all such characters being present in the list of short input names

value input
    this data arg only originates from direct args
"""

# individual args processing

# arg functions

def parseEscapedArg(arg):
    return unescapeArg(arg) if arg is not None and arg.startswith("-") else None

def unescapeArg(arg):
    return arg.replace("-", "", 1)

def parseDoublyEscapedArg(arg):
    return parseEscapedArg(parseEscapedArg(arg))

def parseSinglyEscapedArg(arg):
    return parseEscapedArg(arg) if parseDoublyEscapedArg(arg) is None else None

def parseDirectArg(arg):
    return arg if parseEscapedArg(arg) is None else None

def parseShortInputNameArg(arg):
    return parseSinglyEscapedArg(arg) if parseSinglyEscapedArg(arg) is not None and len(parseSinglyEscapedArg(arg)) == 1 and parseSinglyEscapedArg(arg).isalpha() else None

def parseLongInputNameArg(arg):
    return parseDoublyEscapedArg(arg) if parseDoublyEscapedArg(arg) is not None and len(parseDoublyEscapedArg(arg)) > 1 and re.match("^[a-zA-Z0-9_]*$", parseDoublyEscapedArg(arg)) is not None else None

def parseGroupedShortInputNamesArg(arg):
    return parseSinglyEscapedArg(arg) if parseSinglyEscapedArg(arg) is not None and len(parseSinglyEscapedArg(arg)) > 1 and parseSinglyEscapedArg(arg).isalpha() else None

# DataArgExtractor

class DataArgExtractor:

    def __init__(self, validating_data):
        self.validating_data = validating_data

    def extractArgumentNamesFromEscapedArg(self, arg):
        """
        An arg head is the name of the argument.
        Argument names are the first element of any named argument.
        Named arguments come in two flavours short name and long name.
        All argument must have a short name long names are optional.
        Positional arguments do not explicitly mention their argument name,
        but can be infered from the position of these arguments.
        Short argument names can grouped together within a single clargument,
        out of such grouped arguments only the last one can optionally have values.
        Valueless short arguments are refered to as flags which have boolean values,
        indicated by their presence(True) or absense(False).
    
        This function only returns the short names of the named arguments,
        all others are ignored by returning an empty list.
        """

        dataarg = self.parseLongInputNameArg(arg)
        if dataarg is not None:
            return [self.validating_data["long_input_names"][dataarg]]

        dataarg = self.parseShortInputNameArg(arg)
        if dataarg is not None:
            return [dataarg]

        return self.parseGroupedShortInputNamesArg(arg)

    def parseShortInputNameArg(self, arg):
        return parseShortInputNameArg(arg) if parseShortInputNameArg(arg) is not None and parseShortInputNameArg(arg) in self.validating_data["short_input_names"] else None

    def parseLongInputNameArg(self, arg):
        return parseLongInputNameArg(arg) if parseLongInputNameArg(arg) is not None and parseLongInputNameArg(arg) in self.validating_data["long_input_names"] else None

    def parseGroupedShortInputNamesArg(self, arg):
        if parseGroupedShortInputNamesArg(arg) is not None:
            short_input_names = list(parseGroupedShortInputNamesArg(arg))
            if len(short_input_names) > 0:
                front_one = short_input_names[-1]
                short_input_names = [v for v in short_input_names if v is not front_one]
                short_input_names = self.filterValidShortInputNames(short_input_names)
                if front_one in self.validating_data["short_input_names"]:
                    short_input_names.append(front_one) 
            return short_input_names
        return []

    def parseValueArg(self, arg):
        return parseDirectArg(arg)

    def filterValidShortInputNames(self, short_input_names):
        return list(set(short_input_names) & set(self.validating_data["flags"]))

    def getBodyHavingArgumentName(self, arg):
        darg = self.extractArgumentNamesFromEscapedArg(arg)
        return darg[-1] if darg and darg[-1] in self.validating_data["named_valued_arguments"] else None

# test operation

if __name__ == "__main__":

    import sys

    dex = DataArgExtractor({
        "short_input_names": ["s", "p"],
        "long_input_names": ["spec", "peck"],
        "flags": ["p"],
        "named_valued_arguments": []
    })

    print()
    for arg in sys.argv[1:]:
        print("short", dex.parseShortInputNameArg(arg))
        print("long", dex.parseLongInputNameArg(arg))
        print("group", dex.parseGroupedShortInputNamesArg(arg))
        print("value", dex.parseValueArg(arg))
        print()
