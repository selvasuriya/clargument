# clargument
Command line argument parser.

**Usage**

   A command line interpreter that interprets long and short options(flags), short options can be grouped, options can also take user inputted data, an option can take a single data, multiple data or repeating data of any order, positional arguments are also supported.
   The "--" command line argument can be inputted to separate different options whenever needed, one typical use case is to tell the end of a repeating data when the data is followed immediately by a positional argument.

**About**

   The code is implemented with functional and object oriented approach.

* Identification of the ranges that would yield unabiguously the user inputted name value pairs(when processed linearly), from the user inputted command line arguments is handled with a functional approach by the module *DataArgExtractor.py*.
* Fetching the name value pairs from the identified ranges is supported by the module *Fields.py* which is implemented with object oriented approach.
* The main driving code which is in the *clarguments.py* is mostly procedural but simple.
* The code is documented wherever necessary to my knowledge.
