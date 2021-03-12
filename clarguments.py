from DataArgExtractor import DataArgExtractor
from ArgumentExtractionLib import ArgumentSink
from ArgumentExtractionLib import Arguments
from DataArgExtractor import FieldConsumer
import sys

"""
Arguments:
   these are the name value pairs received from the user

Argument Name:
   usually this is a single letter from the english alphabet. The argument name is synonymous with the short argument name(if the argument is able to be inputted as a short option).

Argument Value:
   this can be catagorised as boolean(flag), list of strings of fixed length(string_list), list of strings that can grow in steps of some integral unit and grow to any length(repeating_string_list).

Argument Input Type:
   the arguments can be inputted at the command line in three different ways which are, long options, short options, positional arguments. A long option shall always be able to be inputted as a short option as well, positional arguments may also be able to be inputted as short, long options.


short_input_names:
   these arguments can be inputted as short named arguments
   make an entry to this list when an argument should be received both when input as an option and when input as a positional argument(note this is needed, only when it has no entry in long_input_names), others will be automatically infered from the positional_arguments list and argument_value_properties dict

long_input_names:
   these arguments can be inputted as long named arguments
   should always be associated with a short option name

positional_arguments:
   these arguments can be inputted as positional arguments
   the position of the input positional arguments will be as the argument names appear in the positional_arguments list

argument_value_properties:
   this contains the number of values an argument takes and if the value/values can repeat or not
   all argument names used in the above lists/dicts should have an entry here, if not it will be ignored

note:
   when any catagory of the above data does not contain any data it can be remove form including in the config dict, when no processing is intended empty dict can be provided(just for information)

sample:

config_data = {
    "short_input_names": ["d"],
    "long_input_names": {"spec":"s", "peck":"p", "cat":"c"},
    "positional_arguments": ["c", "d", "k", "l"],
    "argument_value_properties": {
        "s": [0], "p": [0],
        "c": [2], "d": [1, True],
        "k": [3, True], "l": [3]
    }
}

"""

# procedures

def expand_config_data(data):
    #!!! note: type and allowed range or catagory of data is not being checked, which may lead to undefined behaviour when wrong input is provided

    ## ----------------------
    if "switches" in data:
        switches = data["switches"]
    else:
        switches = []
    if "boolean_params" in data:
        boolean_params = data["boolean_params"]
    else:
        boolean_params = []
    if "global_defaults" in data:
        global_defaults = data["global_defaults"]
    else:
        global_defaults = {}
    if "overloading" in data:
        overloading = data["overloading"]
    else:
        overloading = []
    # generating flags
    flags = switches
    flags.extend(boolean_params)

    ## ----------------------
    if "argument_value_properties" in data:
        argument_value_properties = data["argument_value_properties"]
    else:
        argument_value_properties = {}
    # expanding the flag declarations
    argument_value_properties.update({k:[0, False] for k in flags})
    # expanding the fixed length variable declarations
    argument_value_properties.update({k:[argument_value_properties[k][0], False] for k in argument_value_properties if len(argument_value_properties[k]) is 1})

    ## ----------------------
    valued_arguments = [k for k in argument_value_properties if argument_value_properties[k][0] is not 0]
    if "long_input_names" in data:
        long_input_names = {k:data["long_input_names"][k] for k in data["long_input_names"] if data["long_input_names"][k] in argument_value_properties}
    else:
        long_input_names = {}

    ## ----------------------
    if "positional_arguments" in data:
        positional_arguments = [k for k in data["positional_arguments"] if k in valued_arguments]
    else:
        positional_arguments = []
    repeating_valued_arguments = [k for k in valued_arguments if argument_value_properties[k][1]]
    fixedlength_valued_arguments = [k for k in valued_arguments if not argument_value_properties[k][1]]

    ## ----------------------
    short_input_names = list(set(flags) | set([k for k in valued_arguments if k not in positional_arguments]) | set(long_input_names.values()))
    if "short_input_names" in data:
        short_input_names = list({k for k in data["short_input_names"] if k in argument_value_properties} | set(short_input_names))

    ## ----------------------
    return buildArgumentParsingData(short_input_names, long_input_names, flags, positional_arguments, argument_value_properties, valued_arguments, repeating_valued_arguments, fixedlength_valued_arguments, global_defaults, switches, overloading, boolean_params)

def buildArgumentParsingData(short_input_names, long_input_names, flags, positional_arguments, argument_value_properties, valued_arguments, repeating_valued_arguments, fixedlength_valued_arguments, global_defaults, switches, overloading, boolean_params):
    
    odata = {
        "named_argument_locating_data":{},
        "field_consumption_driving_data":{},
        "merge_data":{},
        "map_data":{}
    }

    odata["named_argument_locating_data"]["short_input_names"] = short_input_names
    odata["named_argument_locating_data"]["long_input_names"] = long_input_names
    odata["named_argument_locating_data"]["valued_arguments"]  = valued_arguments 
    odata["named_argument_locating_data"]["flags"] = flags
    odata["named_argument_locating_data"]["positional_arguments"] = positional_arguments

    odata["field_consumption_driving_data"]["argument_value_properties"] = argument_value_properties

    odata["merge_data"]["repeating_valued_arguments"]  = repeating_valued_arguments
    odata["merge_data"]["fixedlength_valued_arguments"] = fixedlength_valued_arguments
    odata["merge_data"]["flags"] = flags

    odata["map_data"]["global_defaults"] = global_defaults
    odata["map_data"]["switches"] = switches
    odata["map_data"]["overloading"] = overloading
    odata["map_data"]["boolean_params"] = boolean_params

    return odata
    

def parse(args, config_data):
    args = args
    validation_data = expand_config_data(config_data)
    arguments = Arguments(validation_data["map_data"])
    arg_sink = ArgumentSink(arguments, validation_data["merge_data"])
    consumer = FieldConsumer(validation_data["field_consumption_driving_data"])
    dex = DataArgExtractor(args, arg_sink, consumer, validation_data["named_argument_locating_data"])

    dex.koththicharukku()
    arg_sink.merge()
    return arg_sink.arguments


if __name__ == "__main__":

    config_data = {
        "short_input_names": ["d"],
        "long_input_names": {"spec":"s", "peck":"p", "cat":"c"},
        "positional_arguments": ["c", "d", "k", "l"],
        "argument_value_properties": {
            "s": [0], "p": [0],
            "c": [2], "d": [1, True],
            "k": [3, True], "l": [3]
        }
    }
    args = sys.argv[1:]

    a = parse(args, config_data)
    print(a)
