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

class LocalFlags:

    def __init__(self, l):
        self.location = l
        self.flags = {}

    def addFlag(self, n, count=1):
        if n not in self.flags:
            self.flags[n] = count
        else:
            self.flags[n]+=count

    def merge(self, localflags):
        for flag in localflags.flags:
            self.addFlag(flag, localflags.flags[flag])

    def toArgument(self):
        return {flag: Argument(flag, True, self.flags[flag]) for flag in self.flags}

    def __str__(self):
        return f"{self.flags}"

class ValuedArgument:

    def __init__(self, n, l):
        self.location = l
        self.name = n
        self.value = None

    def insertValue(self, v):
        if self.isOpen():
            self.value = v
            return True
        return False

    def isOpen(self):
        return self.value is None

    def merge(self, valued_arg):
        if self.name == valued_arg.name:
            self.value.extend(valued_arg.value)

    def toArgument(self):
        return Argument(self.name, self.value, 1)

    def __str__(self):
        return f"name {self.name} value {self.value}"

class ArgumentSink:

    def __init__(self, arguments, validating_data):
        self.locations = {}
        self.validating_data = validating_data
        self.arguments = arguments

    def sinkFlag(self, k, flag):
        if flag:
            if k not in self.locations:
                self.locations[k] = LocalFlags(k)
            if isinstance(self.locations[k], LocalFlags):
                self.locations[k].addFlag(flag)
                return True
        return False

    def sinkValuedArgument(self, k, n, v):
        if k not in self.locations and n:
            self.locations[k] = ValuedArgument(n, k)
            return self.locations[k].insertValue(v)
        return False

    def merge(self):
        localflags_list = [self.locations[k] for k in self.locations if isinstance(self.locations[k], LocalFlags)]
        localflags_merged = LocalFlags(0)
        for localflags in localflags_list:
            localflags_merged.merge(localflags)
        localflags_merged = localflags_merged.toArgument()
        localflags_merged.update({n: Argument(n, False, 1) for n in self.validating_data["flags"] if n not in localflags_merged})

        repeating_valued_arguments = [v for k, v in sorted(self.locations.items()) if isinstance(v, ValuedArgument) and v.name in self.validating_data["repeating_valued_arguments"]]
        fixedlength_valued_arguments = [v for k, v in sorted(self.locations.items()) if isinstance(v, ValuedArgument) and v.name in self.validating_data["fixedlength_valued_arguments"]]
        valued_arguments_merged = {}
        for arg in repeating_valued_arguments:
            if arg.name not in valued_arguments_merged:
                valued_arguments_merged[arg.name] = arg
            else:
                valued_arguments_merged[arg.name].merge(arg)
        for arg in fixedlength_valued_arguments:
            if arg.name not in valued_arguments_merged:
                valued_arguments_merged[arg.name] = arg
        for n in list(valued_arguments_merged):
            valued_arguments_merged[n] = valued_arguments_merged[n].toArgument()

        arguments = valued_arguments_merged
        arguments.update(localflags_merged)
        self.arguments.addArgs(arguments)

    def __str__(self):
        o = ""
        for k, locarg in self.locations.items():
            o = f"{o}\nlocation {k} args {locarg.__str__()}"
        return o

class Argument:

    def __init__(self, n, v, c):
        self.name = n
        self.value = v
        self.count = c

    def __str__(self):
        return f"name {self.name} value {self.value} count {self.count}"

class Arguments:

    def __init__(self, validating_data):
        self.args = {}
        self.validating_data = validating_data

    def addArgs(self, args):
        self.args.update(args)

    def triggerAction(self):
        ovl = self.findOverloadMatch()
        if ovl:
            self.setDefaults(self.generateDefaults(ovl))
            if "func" in ovl and ovl["func"]:
                return ovl["func"](self.args)
            return "You have not set a function to your overload. You can follow the docs if you need any help :D"
        return self.defaultFunc()

    def filterOverloadCombo(self, args):
        return [n for n in args if n not in self.validating_data["boolean_params"] and n not in self.validating_data["global_defaults"]]

    def passOnlyValidSwitches(self, args):
        return [n for n in args if (n in self.validating_data["switches"] and self.args[n].value) or n not in self.validating_data["switches"]]

    def findOverloadMatch(self):
        ovl_combo = self.passOnlyValidSwitches(self.filterOverloadCombo(self.args))
        for ovl in self.validating_data["overloading"]:
            dest = self.filterOverloadCombo(ovl["local"])
            if all(n in ovl_combo for n in dest) and all(n in dest for n in ovl_combo):
                return ovl
        return None 

    def generateDefaults(self, ovl):
        defaults = self.validating_data["global_defaults"]
        if "local_defaults" in ovl:
            defaults.update({n:ovl["local_defaults"][n] for n in defaults if n in ovl["local_defaults"]})
        return defaults

    def setDefaults(self, defaults):
        self.args.update({n:Argument(n, defaults[n], 1) for n in defaults if n not in self.args})

    def defaultFunc(self):
        return "You have not set any overloading. To set one follow the docs."

    def __str__(self):
        o = ""
        for n in self.args:
            o = f"{o}\n{self.args[n].__str__()}"
        return o
