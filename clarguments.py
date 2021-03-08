import DataArgExtractor as Dex
from Field import Piece
from Field import Field
import sys

# argument name declaration

validation_data = {
    "short_input_names": ["s", "p", "c", "d"],
    "long_input_names": {"spec": "s", "peck": "p"},
    "flags": ["s", "p"],
    "named_valued_arguments": ["c", "d"]
}

# argument value declaration

valued_arguments: ["c", "d", "k", "l"]
positional_arguments = ["c", "d", "k", "l"]
argument_value_properties = {
    "s": [0, False], "p": [0, False],
    "c": [2, False], "d": [1, True],
    "k": [3, True], "l": [3, False]
}

# constants

escape = "escape"
positional = "positional"

# input

args = sys.argv[1:]
args.insert(0, "--")

# Resource

dex = Dex.DataArgExtractor(validation_data)

# functions

def splitArgsIntoFields():
    escaped_locations = [i for i, arg in zip(range(len(args)), args) if Dex.parseEscapedArg(arg) is not None]
    moved_escaped_locations = escaped_locations[1:]
    moved_escaped_locations.append(getArgsLen())
    return {Field(i, j):[] for i, j in zip(escaped_locations, moved_escaped_locations)}

def getArgsLen():
    return len(args)

def getDataArgs(rng):
    return args[rng.getStart():rng.getEnd()]

def consumeEscapedHead(field):
    return Piece(field.consumeHard(1), escape, "head")

def consumeBody(field, argument_name, typ):
    if argument_value_properties[argument_name][1]:
        return Piece(field.consumeElastic(argument_value_properties[argument_name][0]), typ, "body")
    else:
        return Piece(field.consumeHard(argument_value_properties[argument_name][0]), typ, "body")

def getEscapedBodyName(field):
    return dex.getBodyHavingArgumentName(getDataArgs(fields[field][0].consumed_field.rng)[0])

# data structure

fields = splitArgsIntoFields()

# subproc

def printFields(fields):
    for field in fields:
        print("field ", field.rng.getStart(), field.getUnconsumedStart(), field.rng.getEnd(), getDataArgs(field.rng))
        for piece in fields[field]:
            print(piece.type, " ", piece.sub_type, " ", piece.consumed_field.isValid(), " ", piece.consumed_field.rng.getStart(), piece.consumed_field.rng.getEnd(), getDataArgs(piece.consumed_field.rng))
        print("--------------")
    print()

# procedures

def breakAtEscapedArgs():
    for field in fields:
        fields[field].append(consumeEscapedHead(field)) 

    for field in fields:
        argument_name = getEscapedBodyName(field)
        if argument_name is not None:
            fields[field].append(consumeBody(field, argument_name, escape))

def breakAtPositionalArgs():

    # initialisations
    tmp_pos_args = positional_arguments
    tmp_fields = list(fields.keys())
    tmp_pos_args.reverse()
    tmp_fields.reverse()

    # fetching argument_name and field
    argument_name = tmp_pos_args.pop()
    field = tmp_fields.pop()

    while(True):
        piece = consumeBody(field, argument_name, positional)
        fields[field].append(piece)

        # updating the field and argument_name
        # exits when either tmp_fields or tmp_pos_args are depleted
        if field.show() == 0:
            # triggers when a field is completely consumed
            if tmp_fields:
                field = tmp_fields.pop()
            else:
                break
        if piece.consumed_field.isValid():
            # triggers when a piece is successfully extracted for the argument_name
            if tmp_pos_args:
                argument_name = tmp_pos_args.pop()
            else:
                break
        
# main

breakAtEscapedArgs()
breakAtPositionalArgs()
printFields(fields)
