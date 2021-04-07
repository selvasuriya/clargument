from paraivari.parser import parse
import sys


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
                "func": lambda a: f"hai the mail is posted{a['k'].value}"
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
    }
}
args = sys.argv[1:]

parse(args, config_data)

