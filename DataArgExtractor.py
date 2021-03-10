import re
import functools
from Field import Field

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

Capability:
    This locator is capable of locating short options (-s), long options (--search), grouped short options (-sp), argument value (45, myfirst.txt).

    The following are discarded a single character after the "--" string (--s), when the string "--" is used alone ("--"), when the string "-" is used alone ("-"), when the string "-" is followed by a string containing any character other than the english alphabet (-*, -j&j), when the string "--" is followed by a string containing any character other than the english alphabet, common numeral digits and the underscore character (--ha@m).

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

class ArgumentSink:

    def __init__(self, validating_data):
        self.args = {}
        self.validating_data = validating_data

    def getBodyHavingArgumentName(self, darg):
        """checks if the short options list darg ends with a valued short option(which must be present in the validating data 'valued_arguments')."""
        return darg[-1] if darg and darg[-1] in self.validating_data["valued_arguments"] else None

    def insertName(self, k, n):
        if k in self.args and n:
            if self.args[k][1] is None:
                self.args[k][1] = n
            return True
        return False

    def insertValue(self, k, v):
        if k in self.args and v:
            if self.args[k][2] is None:
                self.args[k][2] = v
            return True
        return False

    def addRaw(self, k, r):
        if r:
            if k not in self.args:
                self.args[k] = [r, None, None]
                self.insertName(k, self.getBodyHavingArgumentName(r))
            return True
        return False

    def getRaw(self, k):
        return self.args[k][0] if k in self.args else None

    def getName(self, k):
        return self.args[k][1] if k in self.args else None

    def getArg(self, k):
        return self.args[k][1:] if k in self.args else None

    def __str__(self):
        o = ""
        for k, arg in self.args.items():
            o = f"{o}\nindex {k} raw {arg[0]} name {arg[1]} body {arg[2]}"
        return o

# DataArgExtractor

class DataArgExtractor:

    def __init__(self, args, validating_data, arg_sink):
        args.insert(0, "--")
        self.args = args
        self.validating_data = validating_data
        self.arg_sink = arg_sink

    def getArgsLen(self):
        return len(self.args)

    def catchEscapedArgsAndProduceFields(self):
        escaped_locations = [i for i, arg in zip(range(len(self.args)), self.args) if parseEscapedArg(arg) is not None]
        moved_escaped_locations = escaped_locations[1:]
        moved_escaped_locations.append(self.getArgsLen())

        for i in escaped_locations:
            self.extractArgumentNamesFromEscapedArg(i) 
        escape_past_locations = [i+1 for i in escaped_locations]

        return ([Field(i, j) for i, j in zip(escape_past_locations, moved_escaped_locations)], escaped_locations)

    def extractValues(self, k, rng):
        args = self.args[rng.getStart():rng.getEnd()]
        if all(parseDirectArg(b) is not None for b in args):
            return self.arg_sink.insertValue(k, args)
        return False

    def extractArgumentNamesFromEscapedArg(self, i):
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

        def extractShortInputNameArg(i):
            """checks if the short option is present in the validating_data['short_input_names']"""
            arg = self.args[i]
            if parseShortInputNameArg(arg) is not None and parseShortInputNameArg(arg) in self.validating_data["short_input_names"]:
                return self.arg_sink.addRaw(i, [parseShortInputNameArg(arg)])
            return False

        def extractLongInputNameArg(i):
            """checks if the long option is present in the validating_data['long_input_names']"""
            arg = self.args[i]
            if parseLongInputNameArg(arg) is not None and parseLongInputNameArg(arg) in self.validating_data["long_input_names"] and self.validating_data["long_input_names"][parseLongInputNameArg(arg)] in self.validating_data["short_input_names"]:
                return self.arg_sink.addRaw(i, [self.validating_data["long_input_names"][parseLongInputNameArg(arg)]])
            return False

        def extractGroupedShortInputNamesArg(i):
            """checks if the grouped short options are all flags(which must be present in the validating_data['flags']) optionally ended with a valued/flag short option(which must be present in the validating_data['short_input_names'])."""
    
            arg = self.args[i]

            def filterFlags(short_input_names):
                """checks if the short options are flags i.e., present in the validating_data['flags']"""
                return list(set(short_input_names) & set(self.validating_data["flags"]))
    
            if parseGroupedShortInputNamesArg(arg) is not None:
                short_input_names = list(parseGroupedShortInputNamesArg(arg))
                front_one = short_input_names[-1]
                short_input_names = [v for v in short_input_names if v is not front_one]
                short_input_names = filterFlags(short_input_names)
                if front_one in self.validating_data["short_input_names"]:
                    short_input_names.append(front_one) 
                return self.arg_sink.addRaw(i, short_input_names) if short_input_names else False

            return False

        return (extractLongInputNameArg(i) or extractShortInputNameArg(i) or extractGroupedShortInputNamesArg(i))

# test operation

if __name__ == "__main__":

    import sys

    dex = DataArgExtractor(sys.argv[1:], {
        "short_input_names": ["s", "p", "c", "d"],
        "long_input_names": {"spec": "s", "peck":"p"},
        "flags": ["p", "s"]
    },
    ArgumentSink({
        "valued_arguments":["c", "d"]
    }))
    dex.catchEscapedArgsAndProduceFields()

    print(dex.arg_sink.args)
