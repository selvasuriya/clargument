**Implemented:**

* Arguments:
   All name value pairs extracted are arguments

* Options:
   All arguments inputted with explicitly spelling their name either as a short option (for example -s) or as a long option (for example --save) having zero or more values are options

* Flags:
   All options with zero values, they are boolean valued arguments

* Valued Options:
   All options with one or more values

* Repeating Values:
   The values of an argument can be repeating in steps of any length

* Positional Arguments:
   These arguments are associated with an argument name based on the position of the values inputted with respect to the other positional arguments, these may have one or more values

* Grouped Options:
   Options may be grouped, flags are allowed at any position in a grouped option argument, but valued option is only allowed at the end of the grouped option argument which can be followed by values

* "--":
   can be used anywhere between two arguments, used especially after a repeating value if the repeating value was followed by a positional argument, for removing the ambiguity in identifying the arguments separately if any.

* Multiple Versions of Options:
   options occurring repeatedly won't be ignored. Flags will be counted. Valued options can occur repeatedly with their multiple values being split between different occurances in order.

* Default Values:

* optional and required arguments:

* grouping the arguments:

* overloading commands based on the type(by argument name) and number of arguments:


**To be implemented:**

* Values of the command:
   the command has arguments, it may also directly have values. This shall be implemented as the always first positional argument in any command

* Delimited Values:
   for example f,f,f

* Valued Options and their value in one argument:
   for example -sValue -psValue -s=Value --save=Value

* Specific set of Values:
   for example -s accepting only "fast" and "slow" as arguments

* Sub commands area:
   this is a static area of commands and quite limited in accepting value inputs, i.e arguments cannot change positions

* Min and Max number of Values:


**Later:**

* validations:

