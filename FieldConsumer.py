class FieldConsumer:

    def __init__(self, arg_sink, dex, validating_data):
        self.arg_sink = arg_sink
        self.dex = dex
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
    
    def breakAtEscapedArgs(self, escaped_locations, fields):
    
        for field, i in zip(fields, escaped_locations):
            argument_name = self.arg_sink.getName(i)
            if argument_name is not None:

                consumed = self.consumeBody(field, argument_name)
                if consumed.isValid():
                    self.dex.extractValues(i, consumed.rng)

    def breakAtPositionalArgs(self, fields):

        # initialisations
        tmp_pos_args = self.validating_data["positional_arguments"][:]
        tmp_fields = fields[:]
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
            consumed = self.consumeBody(field, argument_name)
            if consumed.isValid():
                self.arg_sink.addRaw(k, [argument_name])
                self.dex.extractValues(k, consumed.rng)

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
            
