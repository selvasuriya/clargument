from DataArgExtractor import DataArgExtractor
from DataArgExtractor import ArgumentSink
import sys

# configurations

validation_data = {
    "short_input_names": ["s", "p", "c", "d"],
    "long_input_names": {"spec": "s", "peck": "p"},
    "flags": ["s", "p"]
}

field_consumption_driving_data = {
    "valued_arguments": ["c", "d", "k", "l"],
    "positional_arguments": ["c", "d", "k", "l"],
    "argument_value_properties": {
        "s": [0, False], "p": [0, False],
        "c": [2, False], "d": [1, True],
        "k": [3, True], "l": [3, False]
    }
}

# globals

arg_sink = ArgumentSink(field_consumption_driving_data["valued_arguments"])
dex = DataArgExtractor(sys.argv[1:], validation_data, arg_sink)
fields = None

# subproc

def consumeBody(field, argument_name):
    if field_consumption_driving_data["argument_value_properties"][argument_name][1]:
        consumed = field.consumeElastic(field_consumption_driving_data["argument_value_properties"][argument_name][0])
        if consumed.rng.getSpan() is not 0:
            return consumed
        else:
            return field.consumeHard(field_consumption_driving_data["argument_value_properties"][argument_name][0])
    else:
        return field.consumeHard(field_consumption_driving_data["argument_value_properties"][argument_name][0])

# procedures

def breakAtEscapedArgs():
    fields, escaped_locations = dex.catchEscapedArgsAndProduceFields()
    for field, i in zip(fields, escaped_locations):
        argument_name = arg_sink.getName(i)
        if argument_name is not None:
            consumed = consumeBody(field, argument_name)
            if consumed.isValid():
                dex.extractValues(i, consumed.rng)
    return fields

def breakAtPositionalArgs():

    # initialisations
    tmp_pos_args = field_consumption_driving_data["positional_arguments"].copy()
    tmp_fields = fields.copy()
    tmp_pos_args.reverse()
    tmp_fields.reverse()

    # fetching argument_name and field
    argument_name = tmp_pos_args.pop()
    field = tmp_fields.pop()

    while(True):
        k = field.getUnconsumedStart()
        consumed = consumeBody(field, argument_name)
        if consumed.isValid():
            arg_sink.addRaw(k, [argument_name])
            dex.extractValues(k, consumed.rng)

            # updating the argument_name
            # exits when tmp_pos_args is depleted
            # triggers when values are successfully extracted for the argument_name
            if tmp_pos_args:
                argument_name = tmp_pos_args.pop()
            else:
                break

        # updating the field
        # exits when tmp_fields is depleted
        if field.show() == 0:
            # triggers when a field is completely consumed
            if tmp_fields:
                field = tmp_fields.pop()
            else:
                break
        
# main

fields = breakAtEscapedArgs()
breakAtPositionalArgs()
print(arg_sink)
