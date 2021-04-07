from paraivari.payanam.koththisarukku.clarguments import parse as argparse

"""
config_data:
   it is a dictionary with all the commands that the application accepts as keys and config_data for their arguments (see clarguments.py) as value
   command:
      this is the first subcommand for the command line application
args:
   the list of strings that should be parsed as command line arguments
"""

#!!! note: any improvements and feature addition for sub command parsing shall be invoked from here


def parse(args, config_data):
    if len(args) > 0:
        command = args[0]
    if len(args) > 0 and command in config_data:
        if len(args) > 1:
            args = args[1:]
        else:
            args.pop()
        return argparse(args, config_data[command])
    elif "thedirectcommand" in config_data:
        return argparse(args, config_data["thedirectcommand"])
    return None


if __name__ == "__main__":

    import sys

    config_data = {
        "command": {
            "short_input_names": ["d"],
            "long_input_names": {"spec":"s", "peck":"p", "cat":"c"},
            "positional_arguments": ["c", "d", "k", "l"],
            "argument_value_properties": {
                "s": [0], "p": [0],
                "c": [2], "d": [1, True],
                "k": [3, True], "l": [3]
            }
        }
    }
    args = sys.argv[1:]

    a = parse(args, config_data)
    print(a)
