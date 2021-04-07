class Range:
    """

    initialises with an int value for the start property,
    an int value for the end property

    both properties can be accessed with getters

    start and end properties are meant to model start and end index of a range
    of list elements

    """

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def getStart(self):
        return self.start

    def getEnd(self):
        return self.end

    def getSpan(self):
        return self.end - self.start

    def split(self, at):
        if at > self.getStart() and at < self.getEnd():
            tmp = self.end
            self.end = at
            return tmp

    def __str__(self):
        return f"start {self.getStart()} end {self.getEnd()}"

# todo throwing exception when getEnd() accessed before closing


class RightHeadedRange(Range):
    """

    initialises with an int value for the start property,
    None for the end property

    both properties can be accessed with getters
    close() method sets the end property with an int value greater than
    the start property only when the object is not closed
    it can be checked if the end property is set with isClosed() method

    start and end properties are meant to model start and end index of
    a range of list elements

    """

    def __init__(self, start):
        super(RightHeadedRange, self).__init__(start, None)

    def isClosed(self):
        return self.getEnd() is not None

    def close(self, end):
        if not self.isClosed() and end >= self.getStart():
            self.end = end

    def split(self, at):
        if self.isClosed():
            return super(RightHeadedRange, self).split(at)

# rng = RightHeadedRange(4)
# print(rng, rng.isClosed())
# rng.close(14)
# print(rng, rng.isClosed())
# rng2 = RightHeadedRange(6)
# print(rng, rng.isClosed(), rng2, rng2.isClosed())
# rng2.close(rng.split(6))
# print(rng, rng.isClosed(), rng2, rng2.isClosed())

# todo exception throwing when isValid() accessed before consumption


class ConsumedField:
    """

    initialises with a rng (RightHeadedRange) property and an isvalid
    bool property set to True

    method consume closes the rng and sets the isvalid property only when
    the object previously has not consumed
    method hasConsumed returns if the object has consumed
    method isValid gets the value of isvalid

    """

    def __init__(self, start):
        self.rng = RightHeadedRange(start)
        self.isvalid = True

    def consume(self, end, isvalid=True):
        if not self.hasConsumed():
            self.rng.close(end)
            self.isvalid = isvalid

    def hasConsumed(self):
        return self.rng.isClosed()

    def isValid(self):
        return self.isvalid

    def __str__(self):
        return f"validity {self.isValid()} {self.rng}"


class Field:
    """

    initialises with a rng (Range) property and unconsumed_start (int)
    property set to start of the rng initially

    the range represents a range of elements from a list
    the unconsumed_start is the start of the elements which are not
    yet consumed

    the getLimit() method gets the end of rng
    the getUnconsumedStart() method gets the unconsumed_start property
    the show() method returns the range that is yet to be consumed
    the consume() method increments the unconsumed_start by length amount if
    the length is greater than or equal to zero and lesser than or equal to
    the unconsumed range. It returns True if the consumption succeeds
    or else False

    """

    def __init__(self, start, end):
        self.rng = Range(start, end)
        self.unconsumed_start = self.rng.getStart()

    def split(self, at):
        fld = Field(at, self.rng.split(at))
        if self.getUnconsumedStart() > self.getLimit():
            noverflow = self.show()
            self.unconsumed_start += noverflow
            fld.consume(-noverflow)
        return fld

    def getLimit(self):
        return self.rng.getEnd()

    def getUnconsumedStart(self):
        return self.unconsumed_start

    def show(self):
        return self.getLimit()-self.getUnconsumedStart()

    def consume(self, length):
        if length >= 0 and length <= self.show():
            self.unconsumed_start += length
            return True
        else:
            return False

    def acquireAll(self):
        """
        consumes all the unconsumed area
        """
        return self.consume(self.show())

    def acquireAtmost(self, length):
        """
        consumes the range length if possible,
        otherwise consumes all that is available
        """
        if not self.acquire(length):
            return self.acquireAll()
        return True

    def acquire(self, length):
        """
        consumes the range length if possible,
        otherwise no consumption occurs which is indicated by
        a False return value
        """
        return self.consume(length)

    def acquireExcept(self, length):
        """
        consumes everything except a range of length from the available
        unconsumed range if possible,
        otherwise no consumption occurs which is indicated by
        a False return value
        """
        return self.consume(self.show()-length)

    def acquireStretchy(self, length):
        """
        consumes the greatest multiple of the value length which
        can be consumed from the available unconsumed range,
        zero consumption is allowed
        """
        return self.acquireExcept(self.show() % length)

    def consumeElastic(self, unit_length):
        """
        does a acquireStretchy(),
        and returns a ConsumedField object for the range that was
        consumed in the operation whose validity is determined
        by the success of the consumption.
        """
        consumed_field = ConsumedField(self.getUnconsumedStart())
        isvalid = self.acquireStretchy(unit_length)
        consumed_field.consume(self.getUnconsumedStart(), isvalid)

        # Destroys the seen but not acquirable. This is lost
        # (because it is not recorded into the ConsumedField object
        # which is returned).
        self.acquireAll()

        return consumed_field

    def consumeHard(self, length):
        """
        does a acquire(),
        and returns a ConsumedField object for the range that was consumed
        in the operation.
        If the consumption fails all the available unconsumed range
        is consumed and the ConsumedField object returned will have
        isvalid set to False.
        """
        consumed_field = ConsumedField(self.getUnconsumedStart())
        isvalid = self.acquire(length)
        if not isvalid:
            # Destroys the seen but not acquirable.
            # This is lost(because of being invalid).
            self.acquireAll()
        consumed_field.consume(self.getUnconsumedStart(), isvalid)

        return consumed_field

    def __str__(self):
        return f"{self.rng} unconsumed_start {self.getUnconsumedStart()}"


class Piece:
    """

    initialises with the properties type(string), subtype(string),
    consumed_field (ConsumedField)

    type is the type of the argument extract,
    sub_type is the type of the piece within the argument extract

    """

    def __init__(self, consumed_field, typ, sub_type):
        self.consumed_field = consumed_field
        self.type = typ
        self.sub_type = sub_type

    def __str__(self):
        return f"{self.type} {self.sub_type} {self.consumed_field}"

# fld = Field(1,4)
# print(fld)
# print(fld.split(2))
# print(fld)
