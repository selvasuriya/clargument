from clcommands import parse as parseCmd
import sys

"""
boolean:
   have two meanings, a parameter which has a default of False and thus cannot participate in overloading
   a switch solely intended for overloading, i.e it will not be received as a parameter
string_list:(fixed length and repeating)
   it can have a default value if so it can not participate in overloading
   when it have no default value it may be set to None(when user did not input to the argument) and it can participate in overloading
Defaults:
   defaults come in two flavours global and local
   global defaults will always have the same dafault value and does not depend on the overloading selection
   default values of local defaults depend on the oveloading selection
   when a parameter has both local and global defaults the local will override the global default
   a local default having parameter should also have a global default if not its local default will be ignored
Overloading:
   the overloading of a command is dependent only on the switches(not the boolean parameters), and the string_lists (fixed length and repeating) which don't have a default value


flag declaration:
   declaring flags in argument_value_properties is optional, flags are declared in the boolean_params and switches

!!!todo
   fetching data if any from failed Argument formations by the user. (these are now completely ignored)
"""

def parse(args, config_data):
    print(parseCmd(args, config_data).triggerAction())

if __name__ == "__main__":

    def createNote(args):
        return f"create note name {args['c'].value[0]} body {args['b'].value[0]}"

    def listNote(args):
        return f"list note {args['l'].value}"

    def deleteNote(args):
        return "delete note"

    config_data = {
        "command": {
            "short_input_names": ["d"],
            "long_input_names": {"spec":"s", "peck":"p", "cat":"c"},
            "positional_arguments": ["c", "d", "k", "l"],
            "argument_value_properties": {
                "c": [2], "d": [1, True],
                "k": [3, True], "l": [3]
            },
            "global_defaults": {"k":["defaultk1", "defaultk2", "defaultk3"], "c":["defaultc1", "defaultc2"]},
            "boolean_params": ["s"],
            "switches": ["p"],
            "overloading": [
                            {
                    "local": ["p"],
                    "local_defaults": {"k": ["lock1", "lock2", "lock3"]},
                    "func": lambda a: "hai the mail is just posted"
                },
                            {
                    "local": ["d", "p"],
                    "local_defaults": {"c": ["locc1", "locc2"]},
                    "func": lambda a: f"hai the mail is destined to {a['d'].value[0]}"
                },
                            {
                    "local": ["d"],
                    "func": lambda a: "hai the mail is posted"
                },
                            {
                    "local": ["l"],
                    "func": lambda a: "hai the mail is posted"
                },
                            {
                    "local": ["l", "p"],
                    "func": lambda a: "hai the mail is posted"
                },
                            {
                    "local": ["d", "l"],
                    "func": lambda a: "hai the mail is posted"
                },
                            {
                    "local": ["l", "d", "p"],
                    "func": lambda a: "hai the mail is posted by ss with love"
                }
            ]
        },
        "note": {
            "long_input_names": {"create": "c", "delete": "d", "list": "l"},
            "argument_value_properties": {
                "b": [1], "l": [1, True], "c": [1], "d": [1, True]
            },
            "overloading": [
                {
                    "local": ["c", "b"],
                    "func": createNote
                },
                {
                    "local": ["l"],
                    "func": listNote
                },
                {
                    "local": ["d"],
                    "func": deleteNote
                }
            ]
        }
    }
    args = sys.argv[1:]

    parse(args, config_data)
