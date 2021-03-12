from Field import Field
from ArgumentExtractionLib import ArgumentSink
from ArgumentExtractionLib import parseEscapedArg
from ArgumentExtractionLib import parseShortInputNameArg
from ArgumentExtractionLib import parseLongInputNameArg
from ArgumentExtractionLib import parseGroupedShortInputNamesArg
from ArgumentExtractionLib import parseDirectArg


class FieldConsumer:

    def __init__(self, validating_data):
        self.validating_data = validating_data 

    def consumeBody(self, field, argument_name):
        if self.validating_data["argument_value_properties"][argument_name][1]:
            consumed = field.consumeElastic(self.validating_data["argument_value_properties"][argument_name][0])
            if consumed.rng.getSpan() is not 0:
                return consumed
            else:
                return field.consumeHard(self.validating_data["argument_value_properties"][argument_name][0])
        else:
            return field.consumeHard(self.validating_data["argument_value_properties"][argument_name][0])

# DataArgExtractor

class DataArgExtractor:

    def __init__(self, args, arg_sink, consumer, validating_data):
        args.insert(0, "--")
        self.args = args
        self.arg_sink = arg_sink
        self.consumer = consumer
        self.validating_data = validating_data
        self.fields = []

    def getArgsLen(self):
        return len(self.args)

    def extractValuedArgument(self, k, n, consumed):
        if consumed.isValid():
            args = self.args[consumed.rng.getStart():consumed.rng.getEnd()]
            if all(parseDirectArg(b) is not None for b in args):
                return self.arg_sink.sinkValuedArgument(k, n, args)
        return False

    def catchEscapedArgs(self):

        def extractArgumentNamesFromEscapedArg(i, field):
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

            def sinkEscaped(i, n, field):
                if n in self.validating_data["flags"]:
                    return self.arg_sink.sinkFlag(i, n)
                elif n in self.validating_data["valued_arguments"]:
                    return self.extractValuedArgument(i+1, n, self.consumer.consumeBody(field, n))
                return False
    
            def sinkShortInputNameArg(arg):
                """checks if the short option is present in the validating_data['short_input_names']"""
                if parseShortInputNameArg(arg) in self.validating_data["short_input_names"]:
                    return sinkEscaped(i, parseShortInputNameArg(arg), field)
                return False

            def sinkLongInputNameArg(arg):
                """checks if the long option is present in the validating_data['long_input_names']"""
                if parseLongInputNameArg(arg) in self.validating_data["long_input_names"] and self.validating_data["long_input_names"][parseLongInputNameArg(arg)] in self.validating_data["short_input_names"]:
                    return sinkEscaped(i, self.validating_data["long_input_names"][parseLongInputNameArg(arg)], field)
                return False

            def sinkGroupedShortInputNamesArg(arg):
                """checks if the grouped short options are all flags(which must be present in the validating_data['flags']) optionally ended with a valued/flag short option(which must be present in the validating_data['short_input_names'])."""
    
                # separating the inner options and the option on the right side edge(because the later one may be associated with one or more values inputted successively on the command line)
                flags = list(parseGroupedShortInputNamesArg(arg))
                front_one = flags.pop()

                flag_sink = False
                for f in flags:
                    if f in self.validating_data["flags"]:
                        flag_sink = self.arg_sink.sinkFlag(i, f) or flag_sink
                front_one_sink = (sinkEscaped(i, front_one, field) if front_one in self.validating_data["short_input_names"] else False)
                return front_one_sink or flag_sink

            arg = self.args[i]
            if parseShortInputNameArg(arg) is not None:
                return sinkShortInputNameArg(arg)
            elif parseLongInputNameArg(arg) is not None:
                return sinkLongInputNameArg(arg)
            elif parseGroupedShortInputNamesArg(arg) is not None:
                return sinkGroupedShortInputNamesArg(arg)
            return False

        escaped_locations = [i for i, arg in zip(range(self.getArgsLen()), self.args) if parseEscapedArg(arg) is not None]

        moved_escaped_locations = escaped_locations[1:]
        moved_escaped_locations.append(self.getArgsLen())
        escape_past_locations = [i+1 for i in escaped_locations]
        self.fields = [Field(i, j) for i, j in zip(escape_past_locations, moved_escaped_locations)]

        for i, field in zip(escaped_locations, self.fields):
            extractArgumentNamesFromEscapedArg(i, field)

    def glideOnPositionalArgs(self):

        # initialisations
        tmp_pos_args = self.validating_data["positional_arguments"][:]
        tmp_fields = self.fields[:]
        tmp_pos_args.reverse()
        tmp_fields.reverse()

        # fetching argument_name and field
        if tmp_pos_args:
            argument_name = tmp_pos_args.pop()
        else:
            argument_name = None
        if tmp_fields:
            field = tmp_fields.pop()
        else:
            field = None

        while(argument_name and field):
            k = field.getUnconsumedStart()

            if self.extractValuedArgument(k, argument_name, self.consumer.consumeBody(field, argument_name)):
                # updating the argument_name
                # exits when tmp_pos_args is depleted
                # triggers when values are successfully extracted for the argument_name
                if tmp_pos_args:
                    argument_name = tmp_pos_args.pop()
                else:
                    argument_name = None
    
            # updating the field
            # exits when tmp_fields is depleted
            if field.show() == 0:
                # triggers when a field is completely consumed
                if tmp_fields:
                    field = tmp_fields.pop()
                else:
                    field = None

    def koththicharukku(self):
        self.catchEscapedArgs()
        self.glideOnPositionalArgs()
