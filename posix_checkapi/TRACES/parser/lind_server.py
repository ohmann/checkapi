"""
The Lind OS Server.  This module services system calls coming from glibc
<Author>
  Chris Matthews (cmatthew@cs.uvic.ca)
<Start Date>
  Dececmber 2010
"""

#begin include struct.repy
"""
Author: Justin Cappos


Start date: May 26th, 2011

Purpose: support packing and unpacking data in an identical way to Python's
struct module.   We can't tell the endianness so we will need to be given
it.

See http://docs.python.org/library/struct.html for more details!

"""


def _convert_number_to_big_endian_string(numbertoconvert,numberofbytes):
  # a helper to convert a number to bytes (big endian).   Thus:
  # _convert_number_to_big_endian_string(1,4) -> "\x00\x00\x00\x01"
  # _convert_number_to_big_endian_string(65535,2) -> "\xff\xff"

  currentstring = ""
  currentnumber = numbertoconvert

  for num in range(numberofbytes):
    thisbyte = currentnumber & 255
    currentnumber = currentnumber / 256

    currentstring = chr(thisbyte) + currentstring

  # shouldn't be hit because the caller should check
  assert(currentnumber == 0)
  return currentstring




def _convert_big_endian_string_to_number(stringtoconvert):
  # a helper to convert a number to bytes (big endian).   The number is always
  # unsigned Thus:
  # _convert_big_endian_string_to_number("\x00\x00\x00\x01") -> 1
  # _convert_big_endian_string_to_number("\xff\xff") -> 65536

  currentnumber = 0

  for thisbyte in stringtoconvert:
    currentnumber = currentnumber * 256
    currentnumber = currentnumber + ord(thisbyte)

  return currentnumber




def struct_pack(formatstring, *args):
  """
   <Purpose>
      Puts data in a structure that is convenient to pass to C.

   <Arguments>
      formatstring: The format string (See the python docs).   Caveat, if 
           integer, etc.  types are used they *must* contain an endianness 
           character

      args: argument tuple for the formatstring


   <Exceptions>
      ValueError if the wrong number of arguments are passed

      TypeError, ValueError, or IndexError if the format string is malformed

   <Side Effects>
      None.

   <Returns>
      The string containing the packed data
  """

  if type(formatstring) != str:
    raise TypeError("Format string must have type str, not '"+str(type(formatstring))+"'")

  # okay, let's iterate through these and remove stuff as we go!
  currentformatstring = formatstring

  arglist = list(args)

  # this will be built as we go
  retstring = ""
  while currentformatstring and arglist:

    #### Get the endianness! ###

    endianness = "none"
    
    # Let's figure out the endianness
    if currentformatstring[0] == '>' or currentformatstring[0] == '!':
      endianness = "big"
      currentformatstring = currentformatstring[1:]

    elif currentformatstring[0] == '<':
      endianness = "little"
      currentformatstring = currentformatstring[1:]


    #### Get the repeatcount! ###

    # now let's see if there is a repeatcount
    repeatcount = 1
    repeatcountstring = ""
    while currentformatstring[0] in '1234567890':
      repeatcountstring += currentformatstring[0]
      currentformatstring = currentformatstring[1:]
    
    # there is!   Let's set it...
    if repeatcountstring:
      repeatcount = int(repeatcountstring)
    


    #### Handle the type! ###

    # figure out the type of this...
    typetopack = currentformatstring[0]
    currentformatstring = currentformatstring[1:]

    # need to special case empty string...
    if repeatcount == 0 and typetopack == 's' and arglist[0] == '':
      arglist.pop(0)
      continue

    # let's go through this for each thing to pack and add it!
    for thisitem in range(repeatcount):

      # get this arg...
      thisarg = arglist.pop(0)

      # it's a string!   Must not have endianness!!!
      if typetopack == 's':
        if endianness != "none":
          raise TypeError("String must not have endianness")

        if type(thisarg) != str:
          raise TypeError("String format argument not a string")

        if len(thisarg) != repeatcount:
          raise TypeError("String format argument does not match length of argument "+str(len(thisarg))+" != "+str(repeatcount))
      
        retstring += thisarg
        # add the string all at once...
        break



      # it's a signed or unsigned char (1 byte)!   Must have endianness!!!
      elif typetopack == 'b' or typetopack == 'B':
        if endianness == "none":
          raise TypeError("byte must have endianness")

        if type(thisarg) != int and type(thisarg) != long:
          raise TypeError("1-byte int format argument not a long or int")
  
        # let's check the ranges
        if typetopack == 'b':
          if not (thisarg >= -(2**7) and thisarg < 2**7):
            raise ValueError("Integer "+str(thisarg)+" out of range for type 'b'")
        else:
          if not (thisarg >= 0 and thisarg < 2**8):
            raise ValueError("Integer "+str(thisarg)+" out of range for type 'B'")

        if typetopack == 'b' and thisarg < 0:
          # if signed let's do a conversion to an unsigned!
          # Magic code!   Add BYTE_MAX + 1!
          thisarg = thisarg + 2**8

        # okay, so now we have the big-endian description...
        thisargstring = _convert_number_to_big_endian_string(thisarg,1)
 
        # if it's little-endian, let's reverse it!
        if endianness == "little":
          thisargstring = thisargstring[::-1]
          
        # and append it.
        retstring += thisargstring





      # it's a signed or unsigned integer (2 byte)!   Must have endianness!!!
      elif typetopack == 'h' or typetopack == 'H':
        if endianness == "none":
          raise TypeError("short must have endianness")

        if type(thisarg) != int and type(thisarg) != long:
          raise TypeError("2-byte int format argument not a long or int")
  
        # let's check the ranges
        if typetopack == 'h':
          if not (thisarg >= -(2**15) and thisarg < 2**15):
            raise ValueError("Integer "+str(thisarg)+" out of range for type 'h'")
        else:
          if not (thisarg >= 0 and thisarg < 2**16):
            raise ValueError("Integer "+str(thisarg)+" out of range for type 'H'")

        if typetopack == 'h' and thisarg < 0:
          # if signed let's do a conversion to an unsigned!
          # Magic code!   Add SHORT_MAX + 1!
          thisarg = thisarg + 2**16

        # okay, so now we have the big-endian description...
        thisargstring = _convert_number_to_big_endian_string(thisarg,2)
 
        # if it's little-endian, let's reverse it!
        if endianness == "little":
          thisargstring = thisargstring[::-1]
          
        # and append it.
        retstring += thisargstring



      # it's a signed or unsigned integer (4 byte)!   Must have endianness!!!
      elif typetopack == 'i' or typetopack == 'I':
        if endianness == "none":
          raise TypeError("Integer must have endianness")

        if type(thisarg) != int and type(thisarg) != long:
          raise TypeError("4-byte int format argument not a long or int")
  
        # let's check the ranges
        if typetopack == 'i':
          if not (thisarg >= -(2**31) and thisarg < 2**31):
            raise ValueError("Integer "+str(thisarg)+" out of range for type 'i'")
        else:
          if not (thisarg >= 0 and thisarg < 2**32):
            raise ValueError("Integer "+str(thisarg)+" out of range for type 'I'")

        if typetopack == 'i' and thisarg < 0:
          # if signed let's do a conversion to an unsigned!
          # Magic code!   Add UINT_MAX + 1!
          thisarg = thisarg + 2**32 

        # okay, so now we have the big-endian description...
        thisargstring = _convert_number_to_big_endian_string(thisarg,4)
 
        # if it's little-endian, let's reverse it!
        if endianness == "little":
          thisargstring = thisargstring[::-1]
          
        # and append it.
        retstring += thisargstring
        



      # it's a signed or unsigned integer (8 byte)!   Must have endianness!!!
      elif typetopack == 'q' or typetopack == 'Q':
        if endianness == "none":
          raise TypeError("Long long must have endianness")

        if type(thisarg) != int and type(thisarg) != long:
          raise TypeError("8-byte int format argument not a long or int")
  
        # let's check the ranges
        if typetopack == 'q':
          if not (thisarg >= -(2**63) and thisarg < 2**63):
            raise ValueError("Integer "+str(thisarg)+" out of range for type 'q'")
        else:
          if not (thisarg >= 0 and thisarg < 2**64):
            raise ValueError("Integer "+str(thisarg)+" out of range for type 'Q'")

        if typetopack == 'q' and thisarg < 0:
          # if signed let's do a conversion to an unsigned!
          # Magic code!   Add ULONGLONG_MAX + 1!
          thisarg = thisarg + 2**64

        # okay, so now we have the big-endian description...
        thisargstring = _convert_number_to_big_endian_string(thisarg,8)
 
        # if it's little-endian, let's reverse it!
        if endianness == "little":
          thisargstring = thisargstring[::-1]
          
        # and append it.
        retstring += thisargstring


      else:
        raise TypeError("Unknown format type '"+typetopack+"'")
    

  #### Return the result! ###


  # all done, did everything get consumed?
  if currentformatstring:
    raise ValueError("Not enough arguments for formatstring in struct.pack")

  if arglist:
    raise ValueError("Too many arguments for formatstring in struct.pack")

  # yes?   okay, let's return!
  return retstring




# this is very similar to the previous only we return a list instead of a
# string.   Most of the parsing code is copy-pasted over since it is just
# walking through the format string...


def struct_unpack(formatstring, packedstring):
  """
   <Purpose>
      Puts data in a structure that is convenient to pass to C.

   <Arguments>
      formatstring: The format string (See the python docs).   Caveat, if 
           integer, etc.  types are used they *must* contain an endianness 
           character

      packedstring: the string of packed data...


   <Exceptions>
      ValueError, IndexError, TypeError, etc. if the args are malformed

   <Side Effects>
      None.

   <Returns>
      The list containing the unpacked data
  """

  if type(formatstring) != str:
    raise TypeError("Format string must have type str, not '"+str(type(formatstring))+"'")

  if type(packedstring) != str:
    raise TypeError("Packed string must have type str, not '"+str(type(packedstring))+"'")

  # let's check the size and see if this matches.   We also check the format
  # and endianness at the same time.
  expectedpackedstringlength = struct_calcsize(formatstring)
  
  if expectedpackedstringlength != len(packedstring):
    raise ValueError("Expected packed string of length "+str(expectedpackedstringlength)+", got "+str(len(packedstring)))

  # okay, let's iterate through these and remove stuff as we go!
  currentformatstring = formatstring
  currentpackedstring = packedstring


  # this will be built as we go
  retlist = []

  # keep going while there are tokens to consume, or None's (which dont have packed space)
  while (currentformatstring and currentpackedstring):
    #### Get the endianness! ###

    endianness = "none"
    
    # Let's figure out the endianness
    if currentformatstring[0] == '>' or currentformatstring[0] == '!':
      endianness = "big"
      currentformatstring = currentformatstring[1:]

    elif currentformatstring[0] == '<':
      endianness = "little"
      currentformatstring = currentformatstring[1:]


    #### Get the repeatcount! ###

    # now let's see if there is a repeatcount
    repeatcount = 1
    repeatcountstring = ""
    while currentformatstring[0] in '1234567890':
      repeatcountstring += currentformatstring[0]
      currentformatstring = currentformatstring[1:]
    
    # there is!   Let's set it...
    if repeatcountstring:
      repeatcount = int(repeatcountstring)
    

 


    #### Handle the type! ###

    # figure out the type of this...
    typetounpack = currentformatstring[0]
    currentformatstring = currentformatstring[1:]

    # I need to special case a length 0 string...
    if repeatcount == 0 and typetounpack == 's':
      retlist.append('')

    # let's go through this for each thing to unpack
    for thisitem in range(repeatcount):

      # it's a string!   Must not have endianness!!!
      if typetounpack == 's':
        # shouldn't happen because we checked above
        assert(endianness == "none")
        assert(len(currentpackedstring) >= repeatcount)

        # strings should be reconstructed as a string, not a list of bytes...
        retlist.append(currentpackedstring[:repeatcount])
        currentpackedstring = currentpackedstring[repeatcount:]
     
        # ... so exit!
        break



      # it's a signed or unsigned byte / char (1 byte)!  Must have endianness!!!
      elif typetounpack == 'b' or typetounpack == 'B':
        # shouldn't happen because we checked above
        assert(endianness != "none")
        assert(len(currentpackedstring) >= 1)
  
        # flip the endianness to big (if applicable)
        thisnumberstring = currentpackedstring[:1]
        if endianness == "little":
          thisnumberstring = thisnumberstring[::-1]

        currentpackedstring = currentpackedstring[1:]

        # okay, so now we have the big-endian description...
        thisnumber = _convert_big_endian_string_to_number(thisnumberstring)
 

        if typetounpack == 'b' and thisnumber >= 2**7:
          # if signed let's do a conversion to an unsigned!
          # Magic code!   Subtract USHORT_MAX - 1!
          thisnumber = thisnumber - 2**8

        # and append it.
        retlist.append(thisnumber)
        


      # it's a signed or unsigned short (2 byte)!   Must have endianness!!!
      elif typetounpack == 'h' or typetounpack == 'H':
        # shouldn't happen because we checked above
        assert(endianness != "none")
        assert(len(currentpackedstring) >= 2)
  
        # flip the endianness to big (if applicable)
        thisnumberstring = currentpackedstring[:2]
        if endianness == "little":
          thisnumberstring = thisnumberstring[::-1]

        currentpackedstring = currentpackedstring[2:]

        # okay, so now we have the big-endian description...
        thisnumber = _convert_big_endian_string_to_number(thisnumberstring)
 

        if typetounpack == 'h' and thisnumber >= 2**15:
          # if signed let's do a conversion to an unsigned!
          # Magic code!   Subtract USHORT_MAX - 1!
          thisnumber = thisnumber - 2**16

        # and append it.
        retlist.append(thisnumber)
        


      # it's a signed or unsigned integer (4 byte)!   Must have endianness!!!
      elif typetounpack == 'i' or typetounpack == 'I':
        # shouldn't happen because we checked above
        assert(endianness != "none")
        assert(len(currentpackedstring) >= 4)
  
        # flip the endianness to big (if applicable)
        thisnumberstring = currentpackedstring[:4]
        if endianness == "little":
          thisnumberstring = thisnumberstring[::-1]

        currentpackedstring = currentpackedstring[4:]

        # okay, so now we have the big-endian description...
        thisnumber = _convert_big_endian_string_to_number(thisnumberstring)
 

        if typetounpack == 'i' and thisnumber >= 2**31:
          # if signed let's do a conversion to an unsigned!
          # Magic code!   Subtract UINT_MAX - 1!
          thisnumber = thisnumber - 2**32 

        # and append it.
        retlist.append(thisnumber)
        

      # it's a signed or unsigned integer (8 byte)!   Must have endianness!!!
      elif typetounpack == 'q' or typetounpack == 'Q':
        # shouldn't happen because we checked above
        assert(endianness != "none")
        assert(len(currentpackedstring) >= 8)
  
        # flip the endianness to big (if applicable)
        thisnumberstring = currentpackedstring[:8]
        if endianness == "little":
          thisnumberstring = thisnumberstring[::-1]

        currentpackedstring = currentpackedstring[8:]

        # okay, so now we have the big-endian description...
        thisnumber = _convert_big_endian_string_to_number(thisnumberstring)
 

        if typetounpack == 'q' and thisnumber >= 2**63:
          # if signed let's do a conversion to an unsigned!
          # Magic code!   Subtract ULONGLONG_MAX - 1!
          thisnumber = thisnumber - 2**64

        # and append it.
        retlist.append(thisnumber)

        # Pointer
      elif typetounpack == 'P':
        # shouldn't happen because we checked above
        assert(endianness == "none")
        assert(len(currentpackedstring) >= 4)
  
 
        thisnumberstring = currentpackedstring[:4]
 
        currentpackedstring = currentpackedstring[4:]

        # okay, so now we have the big-endian description...
        thisnumber = _convert_big_endian_string_to_number(thisnumberstring)

        # NULL -> None, and Any other number will be in hex
        if thisnumber == 0:
          retlist.append(None)
        else:
          retlist.append(hex(thisnumber))
 
      else:
        raise TypeError("Unknown format type '"+typetounpack+"'")
    

  #### Return the result! ###

  # need to handle trailing empty strings...
  while currentformatstring.startswith('0s'):
    retlist.append('')
    currentformatstring = currentformatstring[2:]

  # all done, did everything get consumed?
  if currentformatstring:
    raise ValueError("Not enough arguments for formatstring in struct.unpack,\
remains: %s"%(currentformatstring))

  if currentpackedstring:
    raise ValueError("Too many arguments for formatstring in struct.unpack")

  # yes?   okay, let's return!
  return retlist




def struct_calcsize(formatstring):
  """
   <Purpose>
      Given a formatstring, indicates the correct packed string size.   

   <Arguments>
      formatstring: The format string (See the python docs).   Caveat, if 
           integer, etc.  types are used they *must* contain an endianness 
           character

   <Exceptions>
      ValueError, IndexError, TypeError, etc. if the args are malformed

   <Side Effects>
      None.

   <Returns>
      A numeric length (>=0)
  """

  if type(formatstring) != str:
    raise TypeError("Format string must have type str, not '"+str(type(formatstring))+"'")

  
  currentlength = 0

  # this will hold the position inside of the formatstring.   It's what we 
  # move along to make progress.
  position = 0

  # we'll move the position in the formatstring as we go...
  while position < len(formatstring):

    #### Do our limited endianness checking... ###

    specifiesendianness = False
    # We'll ignore endianness characters other than to check for existance
    if formatstring[position] in ['>','!','<']:
      position = position + 1
      specifiesendianness = True
    #### Get the repeatcount! ###

    # now let's see if there is a repeatcount
    repeatcount = 1
    repeatcountstring = ""
    while formatstring[position] in '1234567890':
      repeatcountstring += formatstring[position]
      position = position + 1
    
    # there is!   Let's set it...
    if repeatcountstring:
      repeatcount = int(repeatcountstring)
    


    #### Handle the type! ###

    # figure out the type of this...
    typetounpack = formatstring[position]
    position = position + 1

    # it's a string!   Must not have endianness!!!
    if typetounpack == 's':

      if specifiesendianness:
        raise ValueError("A string cannot have endianness specified! (position "+str(position)+" of '"+formatstring+"')")
      
      # add the size of a char + the number of chars
      currentlength += 1 * repeatcount



    # it's a signed or unsigned char / byte!   Must have endianness!!!
    elif typetounpack == 'b' or typetounpack == 'B':

      if not specifiesendianness:
        raise ValueError("A byte must have endianness specified! (position "+str(position)+" of '"+formatstring+"')")

      # add the size of a byte + the number of bytes
      currentlength += 1 * repeatcount



    # it's a signed or unsigned integer (2 byte)!   Must have endianness!!!
    elif typetounpack == 'h' or typetounpack == 'H':

      if not specifiesendianness:
        raise ValueError("A short must have endianness specified! (position "+str(position)+" of '"+formatstring+"')")

      # add the size of a short + the number of shorts
      currentlength += 2 * repeatcount


    # it's a signed or unsigned integer (4 byte)!   Must have endianness!!!
    elif typetounpack == 'i' or typetounpack == 'I':

      if not specifiesendianness:
        raise ValueError("An integer must have endianness specified! (position "+str(position)+" of '"+formatstring+"')")


      # add the size of an integer + the number of integers
      currentlength += 4 * repeatcount

    # it's a signed or unsigned long long (8 byte)!   Must have endianness!!!
    elif typetounpack == 'q' or typetounpack == 'Q':

      if not specifiesendianness:
        raise ValueError("An integer must have endianness specified! (position "+str(position)+" of '"+formatstring+"')")


      # add the size of an integer + the number of integers
      currentlength += 8 * repeatcount

    # Pointer!!!
    elif typetounpack == 'P':

      if specifiesendianness:
        raise ValueError("An pointer must not have endianness specified! (position "+str(position)+" of '"+formatstring+"')")

      # add the size of an integer + the number of integers
      currentlength += 4 * repeatcount

    else:
      raise TypeError("Unknown format type '"+typetounpack+"' at (position "+str(position)+" of '"+formatstring+"')")
  return currentlength



#end include struct.repy

VERSION = "$Rev: 6269 $"


SILENT = True # Try to produce output as close as the OS would
               # this means no debug/error messages!

TRACE = False  # Trace system calls? (somewhat like strace) 



SYSCALL = "syscall"               # shortcut to syscall dict items
FILES = "FILES"                   # these also make a typo more specific
COMP = "comp"                                # than a dict lookup error
ERRNO = "errno.h"
MBOX = "mbox"
LOCK = "lock"
PROGRAM = "program"
CMD_LINE = "command_line_args"
SUCCESS = 0

PRODUCTION = False
COMP_MODE = "component_mode"

# the size of the transmission buffer.  We should never send something
# bigger than this!
TX_BUF_MAX = (4096 * 4) - 16   # 16 bytes of header
RX_BUF_MAX = (4096 * 4)


if not TRACE:
  def log(arg):
    """Turn off logging"""
    pass


def warning(*msg):
  if not SILENT:
    for part in msg:
      print part,
    print



def assert_warning(logic, message):
  """Like assert, but only warn"""
  if not logic:
    log( "Warning:"+ message)


def curr_comp():
  return mycontext[mycontext[COMP]]


def comp(num):
  return mycontext[num]


def unimplemented(who):
  """what to do when we come across some code that needs to be finished.
  For now, lets just keep running, but really this should not happen
  so we should exit.  """
  message = "a unimplemented function has been called " + str(who)
  if PRODUCTION:
    log("error: " + message)
    exitall()
  else:
    log("warning: " + message)

#begin include lind_rpc.repy
"""

Chris Matthews  2011
cmatthew@cs.uvic.ca

Classes for Lind RPC.

Response is a super class used for sending data back, which can be either an
error or success.

"""


class Response:
    """ An Response to a RPC request.

    <Purpose>

    This object is responsible sending responses to specific system
    calls.  It is loaded with data, then can build a reply struct
    which can then be sent back to NaCl through an IMC channel.

    The Response can be in one of two states, an Error response (for
    calls that have failed somehow), or a success response. An error
    response has an error code and a message for perror to display. A
    success has a return code and optionally a data string.

    TODO: error message is not yet displayed by perror.
    """
    message = "No error message set"
    data = ""

    def __init__(self, response_type, is_error, return_code):
        assert isinstance(response_type, str), "response type is not a string"
        self.response_type = response_type
        assert isinstance(is_error, bool), "is error is not a boolean"
        self.is_error = is_error

        if isinstance(return_code, str):
            try:
                self.return_code = curr_comp()[ERRNO][return_code]
            except KeyError:
                raise Exception("Return code is not a valid error number.")
        elif isinstance(return_code, int):
            self.return_code = return_code
        else:
            raise Exception("Invalid return code.")
        assert isinstance(self.return_code, int), \
               "return code is not a int, or a stirng which mapped to an int"

    def make_struct(self):
        """
        <Purpose>

        Get the representation of this Response in struct format.  A
        struct is a string, which when sent to C can be cast as a
        struct and used nativly.  The struct format is iiii123s, wich
        is:
        struct {
        int message_len;
        int magic_number;
        int is_in_error; int return_or_error_code; char data_or_message[];
        };

        """
        reply = None
        if self.is_error:
            # message format <size, magic, is_error, code, message>
            reply = struct_pack("<i<i<i<i" + str(len(self.message)) + "s", \
                                len(self.message) + 16, \
                                101010, 1, self.return_code,\
                                self.message)
        else:
            # message format <size, magic, is_error, code, data>
            reply = struct_pack("<i<i<i<i" + str(len(self.data)) + "s", \
                                len(self.data) + 16, 101010, 0, \
                                self.return_code, self.data)
        return reply

    def __str__(self):
        """Human readable format for debugging"""
        if self.is_error:
            type_str = "Error"
        else:
            type_str = "Success"
        return type_str + " in " + self.response_type + " with code " + \
               str(self.return_code) + " with data of size " + \
               str(len(self.data)) + " with data " + str(self.data)


def ErrorResponseBuilder(who, code, message):
    """ Build an error response object.

    <Arguments>
        who: Which portion of the system or system call is making this reply.
        code: Positive error code to return, or string from errno.h to resolve
        to a number.

        message: A detailed message about the error.
        """
    if not SILENT:
        print "Note:", str(who), "got return code", code, ":", message
    r = Response(who, True, code)
    r.message = message
    return r


def SuccessResponseBuilder(who, code, data=None):
    """Build an success response object.

    <Arugments>
        who: Which portion of the system or system call is making this reply.
        code: the integer return code to return.
        data: the data this call returns (as a string), if any.
    """
    r = Response(who, False, code)
    if data != None:
        r.data = data
    return r

#end include lind_rpc.repy


#begin include lind_parsers.repy
"""
Chris Matthews (2012) cmatthew@cs.uvic.ca

This file contains parsers and packers for C structs.

"""


def inet_ntoa(ipaddress):
    """
    Convert an IP address in integer form to a presentation string

    This is

    """
    a, b, c, d = struct_unpack("<B<B<B<B", ipaddress)
    return str(a) + "." + str(b) + "." + str(c) + "." + str(d)


def inet_aton(ipaddress):
    """
    Convert an IP address in presentation format to its integer octet format

    """
    return struct_unpack("<I", struct_pack("<B<B<B<B", \
                                           *map(int, ipaddress.split("."))))[0]


struct_sockaddr_format = '<h>H<I<Q'  # family, port, address, padding


def parse_sockaddr_struct(sock):
    """parse a struct sockaddr, and pull out family, port, ip and padding"""
    fmt = struct_sockaddr_format
    assert struct_calcsize(fmt) == 16
    return struct_unpack(fmt, sock)


def pack_struct_sockaddr(family, ip, port):
    packed_ip = inet_aton(ip)
    return struct_pack(struct_sockaddr_format, family, port, packed_ip, 0)


# struct pollfd {
#     int   fd;         /* file descriptor */
#     short events;     /* requested events */
#     short revents;    /* returned events */
#     };

single_struct_pollfd_fmt = "<I<h<h"


def parse_struct_pollfds(pollfds_str, nfds):
    struct_siz = struct_calcsize(single_struct_pollfd_fmt)
    mynfds = len(pollfds_str) / struct_siz
    assert mynfds == nfds, "Struct pollfd size missmatch."

    def split(input, size):
        return [input[start:start + size] \
                for start in range(0, len(input), size)]

    structs = split(pollfds_str, struct_siz)

    result = map(lambda x: struct_unpack(single_struct_pollfd_fmt, x), structs)
    result = map(lambda x: {'fd': x[0],
                            'events': x[1],
                            'revents': x[2]},
                 result)
    return result


def pack_struct_pollfds(pollfds_dict, nfds):
    format = single_struct_pollfd_fmt * nfds
    elements = map(lambda x: (x['fd'], x['events'], x['revents']), 
                   pollfds_dict)
    elements = [item for sublist in elements for item in sublist]
    return struct_pack(format, *elements)


def pack_stat_struct(struct_tuple):
    """Given a tuple with stat fields, pack it into a string"""
    (my_st_dev, my_st_ino, my_st_mode, my_st_nlink, my_st_uid, my_st_gid,
     my_st_rdev, my_st_size, my_st_blksize, my_st_blocks,
     my_st_atime, my_st_atimeus, my_st_mtime, \
     my_st_mtimeus, my_st_ctime, my_st_ctimeus) = struct_tuple

    if type(my_st_rdev) == tuple:
        ma = my_st_rdev[0]
        mi = my_st_rdev[1]
        my_st_rdev = (((ma) << 20) | (mi))
        
    result = struct_pack('<Q<Q<I<I<I<I<Q<q<q<q<Q<Q<Q<Q<Q<Q',
                         my_st_dev, my_st_ino, my_st_mode, my_st_nlink, \
                         my_st_uid, my_st_gid, my_st_rdev, my_st_size, \
                         my_st_blksize, my_st_blocks, my_st_atime, \
                            my_st_atimeus, my_st_mtime, my_st_mtimeus, \
                         my_st_ctime, my_st_ctimeus)
    return result


def pack_statfs_struct(fsd):
    """struct statfs {
                    long    f_type;     -- type of file system (see below)
                    long    f_bsize;    -- optimal transfer block size
                    long    f_blocks;   -- total data blocks in file system
                    long    f_bfree;    -- free blocks in fs
                    long    f_bavail;   -- free blocks avail to non-superuser
                    long    f_files;    -- total file nodes in file system
                    long    f_ffree;    -- free file nodes in fs
                    fsid_t  f_fsid;     -- file system id
                    long    f_namelen;  -- maximum length of filenames
    """
    (tipe, bsize, blocks, bfree, bavail, files, ffree,\
     fsid, namelen, frsize, spare) = (fsd['f_type'],
                                      fsd['f_bsize'],
                                      fsd['f_blocks'],
                                      fsd['f_bfree'],
                                      fsd['f_bavail'],
                                      fsd['f_files'],
                                      fsd['f_files'],
                                      fsd['f_fsid'],
                                      fsd['f_namelen'],
                                      fsd['f_frsize'],
                                      fsd['f_spare'])

    format = '<q<q<q<q<q<q<q<Q<q<q8s'
    result = struct_pack(format, tipe, bsize, blocks, bfree, bavail, \
                         files, ffree, fsid, namelen, frsize, spare)
    return result


SEC_PER_MICROSEC = 0.000001
MICROSEC_PER_SEC = 1000000

def parse_timeval(timeval_str):
    """given a struct timeval, make it into a float in seconds.

    @return a float in seceonds, then each sec and usec member
    """
    
    tv_sec, tv_usec = struct_unpack("<Q<Q",timeval_str)
    return ((tv_sec + (SEC_PER_MICROSEC * tv_usec)), tv_sec, tv_usec)


def pack_struct_timeval(tv_sec, tv_usec):
    """given a struct timeval, make it into a float in seconds.

    @return a float in seceonds, then each sec and usec member
    """
    new_struct= struct_pack("<Q<Q",tv_sec, tv_usec)
    return new_struct

    

#end include lind_parsers.repy

#begin include lind_fs_constants.py
"""
  Author: Justin Cappos
  Module: File system constants for Lind.   This is things like the mode bits
          and macros.

  Start Date: December 17th, 2011

"""

# Mostly used with access()
F_OK = 0
X_OK = 1
W_OK = 2
R_OK = 4


O_RDONLY = 00
O_WRONLY = 01
O_RDWR = 02

# we will use this to get the flags
O_RDWRFLAGS = O_RDONLY | O_WRONLY | O_RDWR

O_CREAT = 0100
O_EXCL = 0200
O_NOCTTY = 0400
O_TRUNC = 01000
O_APPEND = 02000
O_NONBLOCK = 04000
# O_NDELAY=O_NONBLOCK
O_SYNC = 010000
# O_FSYNC=O_SYNC
O_ASYNC = 020000
O_CLOEXEC = 02000000

S_IRWXA = 00777
S_IRWXU = 00700
S_IRUSR = 00400
S_IWUSR = 00200
S_IXUSR = 00100
S_IRWXG = 00070
S_IRGRP = 00040
S_IWGRP = 00020
S_IXGRP = 00010
S_IRWXO = 00007
S_IROTH = 00004
S_IWOTH = 00002
S_IXOTH = 00001


# file types for open / stat, etc.
S_IFBLK = 24576
S_IFCHR = 8192
S_IFDIR = 16384
S_IFIFO = 4096
S_IFLNK = 40960
S_IFREG = 32768
S_IFSOCK = 49152

# the above type mode is these 4 bits.   I want to be able to pull them out...
S_FILETYPEFLAGS = 2**12 + 2**13 + 2**14 + 2**15

S_IWRITE = 128
S_ISUID = 2048
S_IREAD = 256
S_ENFMT = 1024
S_ISGID = 1024

SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

F_DUPFD = 0
F_GETFD = 1
F_SETFD = 2
F_GETFL = 3
F_SETFL = 4
F_GETLK = 5
F_GETLK64 = 5
F_SETLK = 6
F_SETLK64 = 6
F_SETLKW = 7
F_SETLKW64 = 7
F_SETOWN = 8
F_GETOWN = 9
F_SETSIG = 10
F_GETSIG = 11
F_SETLEASE = 1024
F_GETLEASE = 1025
F_NOTIFY = 1026

# for fcntl to manipulate file descriptor flags..
FD_CLOEXEC = 02000000

# for the lock calls
F_RDLCK = 0
F_WRLCK = 1
F_UNLCK = 2
F_EXLCK = 4
F_SHLCK = 8

# for flock syscall
LOCK_SH = 1
LOCK_EX = 2
LOCK_UN = 8
LOCK_NB = 4


# the longest path in Linux
PATH_MAX = 4096

#largest file descriptor
MAX_FD = 1024
STARTINGFD = 10


# for dirents...
DEFAULT_UID=1000
DEFAULT_GID=1000

# when saving the metadata file on disk,
# what name should we use:
DEFAULT_METADATA_FILENAME = "lind.metadata"



# convert file mode (S_) to dirent type (D_SIR_)
def get_direnttype_from_mode(mode):
  if IS_DIR(mode):
    return DT_DIR
  if IS_REG(mode):
    return DT_REG
  if IS_SOCK(mode):
    return DT_SOCK

  # otherwise, return unknown for now...
  return DT_UNKNOWN


# types for getdents d_type field

#default
DT_UNKNOWN = 0

#named pipe
DT_FIFO = 1

#character device
DT_CHR = 2

#directory
DT_DIR = 4

#block device
DT_BLK = 6

# regular file
DT_REG = 8

#link
DT_LNK = 10

# unix domain socket
DT_SOCK = 12

# dont know what this is for?!  but it is in dirent.h
DT_WHT = 14

# default name for metadata
DEFAULT_METADATA_FILENAME = "lind.metadata"


# some MACRO helpers...
def IS_DIR(mode):
  if mode & S_FILETYPEFLAGS == S_IFDIR:
    return True
  else:
    return False

def IS_REG(mode):
  if mode & S_FILETYPEFLAGS == S_IFREG:
    return True
  else:
    return False


def IS_CHR(mode):
  return (mode & S_FILETYPEFLAGS) == S_IFCHR


def IS_SOCK(mode):
  if mode & S_FILETYPEFLAGS == S_IFSOCK:
    return True
  else:
    return False


def IS_RDONLY(flags):
  if flags & O_RDWRFLAGS == O_RDONLY:
    return True
  else:
    return False


def IS_WRONLY(flags):
  if flags & O_RDWRFLAGS == O_WRONLY:
    return True
  else:
    return False


def IS_RDWR(flags):
  if flags & O_RDWRFLAGS == O_RDWR:
    return True
  else:
    return False

def IS_NONBLOCKING(fd_flags, recv_flags):
  if ((fd_flags & O_NONBLOCK) != 0) or ((recv_flags & O_NONBLOCK) != 0):
    return True
  else:
    return False

#end include lind_fs_constants.py

def check_valid_fd_handle(num):
  assert isinstance(num, int)
  assert (STARTINGFD <= num <= MAX_FD), "invalid handle %d" % num


#begin include errno.repy
# This code is to transulate between errnos in RePy which we keep as String
# literals to the integer values which C needs.
# For the most part this is just used at the marshaling stage


def errno_name_to_num(name, component_num=1):
    """Given an errno symbolic name, give back the integer
    value define in errno.h

    """
    #use the first table, if no other specificed. It is always there
    return comp(component_num)[ERRNO][name]


def setup_errnos(component_num=1):

    #setup error codes
    comp(component_num)[ERRNO] = {
        'EPERM':1,	# Operation not permitted 
        'ENOENT':2, # No such file or directory
        'ESRCH': 3,	# No such process 
        'EINTR': 4,	# Interrupted system call 
        'EIO': 5,	# I/O error 
        'ENXIO': 6,	# No such device or address 
        'E2BIG': 7,	# Argument list too long 
        'ENOEXEC': 8,	# Exec format error 
        'EBADF': 9,	# Bad file number 
        'ECHILD':10,	# No child processes 
        'EAGAIN':11,	# Try again 
        'ENOMEM':12,	# Out of memory 
        'EACCES':13,	# Permission denied 
        'EFAULT':14,	# Bad address 
        'ENOTBLK':15,	# Block device required 
        'EBUSY':16,	# Device or resource busy 
        'EEXIST':17,	# File exists 
        'EXDEV':18,	# Cross-device link 
        'ENODEV':19,	# No such device 
        'ENOTDIR':20,	# Not a directory 
        'EISDIR':21,	# Is a directory 
        'EINVAL':22,	# Invalid argument 
        'ENFILE':23,	# File table overflow 
        'EMFILE':24,	# Too many open files 
        'ENOTTY':25,	# Not a typewriter 
        'ETXTBSY':26,	# Text file busy 
        'EFBIG':27,	# File too large 
        'ENOSPC':28,	# No space left on device 
        'ESPIPE':29,	# Illegal seek 
        'EROFS':30,	# Read-only file system 
        'EMLINK':31,	# Too many links 
        'EPIPE':32,	# Broken pipe 
        'EDOM':33,	# Math argument out of domain of func 
        'ERANGE':34,	# Math result not representable 

        'EDEADLK':35,	# Resource deadlock would occur 
        'ENAMETOOLONG':36,	# File name too long 
        'ENOLCK':37,  # No record locks available 
        'ENOSYS':38,	# Function not implemented 
        'ENOTEMPTY':39,	# Directory not empty 
        'ELOOP':40,	# Too many symbolic links encountered 
        'EWOULDBLOCK':11, # Operation would block, returns EAGAIN 
        'ENOMSG':42,	# No message of desired type 
        'EIDRM':43,	# Identifier removed 
        'ECHRNG':44,	# Channel number out of range 
        'EL2NSYNC':45,	# Level 2 not synchronized 
        'EL3HLT':46,	# Level 3 halted 
        'EL3RST':47,	# Level 3 reset 
        'ELNRNG':48,	# Link number out of range 
        'EUNATCH':49,	# Protocol driver not attached 
        'ENOCSI':50,	# No CSI structure available 
        'EL2HLT':51,	# Level 2 halted 
        'EBADE':52,	# Invalid exchange 
        'EBADR':53,	# Invalid request descriptor 
        'EXFULL':54,	# Exchange full 
        'ENOANO':55,	# No anode 
        'EBADRQC':56,	# Invalid request code 
        'EBADSLT':57,	# Invalid slot 
        'EBFONT':59,	# Bad font file format 
        'ENOSTR':60,	# Device not a stream 
        'ENODATA':61,	# No data available 
        'ETIME':62,	# Timer expired 
        'ENOSR':63,	# Out of streams resources 
        'ENONET':64,	# Machine is not on the network 
        'ENOPKG':65,	# Package not installed 
        'EREMOTE':66,	# Object is remote 
        'ENOLINK':67,	# Link has been severed 
        'EADV':68,	# Advertise error 
        'ESRMNT':69,	# Srmount error 
        'ECOMM':70,	# Communication error on send 
        'EPROTO':71,	# Protocol error 
        'EMULTIHOP':72,	# Multihop attempted 
        'EDOTDOT':73,	# RFS specific error 
        'EBADMSG':74,	# Not a data message 
        'EOVERFLOW':75,	# Value too large for defined data type 
        'ENOTUNIQ':76,	# Name not unique on network 
        'EBADFD':77,	# File descriptor in bad state 
        'EREMCHG':78,	# Remote address changed 
        'ELIBACC':79,	# Can not access a needed shared library 
        'ELIBBAD':80,	# Accessing a corrupted shared library 
        'ELIBSCN':81,	# .lib section in a.out corrupted 
        'ELIBMAX':82,	# Attempting to link in too many shared libraries 
        'ELIBEXEC':83,	# Cannot exec a shared library directly 
        'EILSEQ':84,	# Illegal byte sequence 
        'ERESTART':85,	# Interrupted system call should be restarted 
        'ESTRPIPE':86,	# Streams pipe error 
        'EUSERS':87,	# Too many users 
        'ENOTSOCK':88,	# Socket operation on non-socket 
        'EDESTADDRREQ':89,	# Destination address required 
        'EMSGSIZE':90,	# Message too long 
        'EPROTOTYPE':91,	# Protocol wrong type for socket 
        'ENOPROTOOPT':92,	# Protocol not available 
        'EPROTONOSUPPORT':93,	# Protocol not supported 
        'ESOCKTNOSUPPORT':94,	# Socket type not supported 
        'EOPNOTSUPP':95,	# Operation not supported on transport endpoint 
        'EPFNOSUPPORT':96,	# Protocol family not supported 
        'EAFNOSUPPORT':97,	# Address family not supported by protocol 
        'EADDRINUSE':98,	# Address already in use 
        'EADDRNOTAVAIL':99,	# Cannot assign requested address 
        'ENETDOWN':100,	# Network is down 
        'ENETUNREACH':101,	# Network is unreachable 
        'ENETRESET':102,	# Network dropped connection because of reset 
        'ECONNABORTED':103,	# Software caused connection abort 
        'ECONNRESET':104,	# Connection reset by peer 
        'ENOBUFS':105,	# No buffer space available 
        'EISCONN':106,	# Transport endpoint is already connected 
        'ENOTCONN':107,	# Transport endpoint is not connected 
        'ESHUTDOWN':108,	# Cannot send after transport endpoint shutdown 
        'ETOOMANYREFS':109,	# Too many references: cannot splice 
        'ETIMEDOUT':110,	# Connection timed out 
        'ECONNREFUSED':111,	# Connection refused 
        'EHOSTDOWN':112,	# Host is down 
        'EHOSTUNREACH':113,	# No route to host 
        'EALREADY':114,	# Operation already in progress 
        'EINPROGRESS':115,	# Operation now in progress 
        'ESTALE':116,	# Stale NFS file handle 
        'EUCLEAN':117,	# Structure needs cleaning 
        'ENOTNAM':118,	# Not a XENIX named type file 
        'ENAVAIL':119,	# No XENIX semaphores available 
        'EISNAM':120,	# Is a named type file 
        'EREMOTEIO':121,	# Remote I/O error 
        'EDQUOT':122,	# Quota exceeded 
        'ENOMEDIUM':123,	# No medium found 
        'EMEDIUMTYPE':124,	# Wrong medium type 
        'ECANCELED':125,	# Operation Canceled 
        'ENOKEY':126,	# Required key not available 
        'EKEYEXPIRED':127,	# Key has expired 
        'EKEYREVOKED':128,	# Key has been revoked 
        'EKEYREJECTED':129,	# Key was rejected by service 
        # for robust mutexes 
        'EOWNERDEAD':130,	# Owner died 
        'ENOTRECOVERABLE':131	# State not recoverable
        }



#end include errno.repy

#begin include lind_net_constants.py
"""
  Author: Justin Cappos
  Module: Network constants for Lind.   This is things like the #defines
          and macros.

  Start Date: January 14th, 2012

"""









################### Mostly used with socket() / socketpair()


# socket types...

SOCK_STREAM = 1    # stream socket
SOCK_DGRAM = 2     # datagram socket
SOCK_RAW = 3       # raw-protocol interface
SOCK_RDM = 4       # reliably-delivered message
SOCK_SEQPACKET = 5 # sequenced packet stream
SOCK_CLOEXEC = 02000000
SOCK_NONBLOCK = 0x4000


# Address families...

AF_UNSPEC = 0        # unspecified
AF_UNIX = 1          # local to host (pipes)
AF_LOCAL = AF_UNIX   # backward compatibility
PF_FILE = AF_UNIX    # common on Linux
AF_INET = 2          # internetwork: UDP, TCP, etc.
AF_IMPLINK = 3       # arpanet imp addresses
AF_PUP = 4           # pup protocols: e.g. BSP
AF_CHAOS = 5         # mit CHAOS protocols
AF_NS = 6            # XEROX NS protocols
AF_ISO = 7           # ISO protocols
AF_OSI = AF_ISO
AF_ECMA = 8          # European computer manufacturers
AF_DATAKIT = 9       # datakit protocols
AF_CCITT = 10        # CCITT protocols, X.25 etc
AF_SNA = 11          # IBM SNA
AF_DECnet = 12       # DECnet
AF_DLI = 13          # DEC Direct data link interface
AF_LAT = 14          # LAT
AF_HYLINK = 15       # NSC Hyperchannel
AF_APPLETALK = 16    # Apple Talk
AF_ROUTE = 17        # Internal Routing Protocol
AF_LINK = 18         # Link layer interface
pseudo_AF_XTP = 19   # eXpress Transfer Protocol (no AF)
AF_COIP = 20         # connection-oriented IP, aka ST II
AF_CNT = 21          # Computer Network Technology
pseudo_AF_RTIP = 22  # Help Identify RTIP packets
AF_IPX = 23          # Novell Internet Protocol
AF_SIP = 24          # Simple Internet Protocol
pseudo_AF_PIP = 25   # Help Identify PIP packets
pseudo_AF_BLUE = 26  # Identify packets for Blue Box - Not used
AF_NDRV = 27         # Network Driver 'raw' access
AF_ISDN = 28         # Integrated Services Digital Network
AF_E164 = AF_ISDN    # CCITT E.164 recommendation
pseudo_AF_KEY = 29   # Internal key-management function
AF_INET6 = 30        # IPv6
AF_NATM = 31         # native ATM access
AF_SYSTEM = 32       # Kernel event messages
AF_NETBIOS = 33      # NetBIOS
AF_PPP = 34          # PPP communication protocol
pseudo_AF_HDRCMPLT = 35 # Used by BPF to not rewrite headers in interface output routines
AF_RESERVED_36 = 36  # Reserved for internal usage
AF_IEEE80211 = 37    # IEEE 802.11 protocol
AF_MAX = 38

# protocols...

IPPROTO_IP = 0          # dummy for IP
IPPROTO_ICMP = 1        # control message protocol
IPPROTO_IGMP = 2        # group mgmt protocol
IPPROTO_GGP = 3         # gateway^2 (deprecated)
IPPROTO_IPV4 = 4        # IPv4 encapsulation
IPPROTO_IPIP = IPPROTO_IPV4        # for compatibility
IPPROTO_TCP = 6         # tcp
IPPROTO_ST = 7          # Stream protocol II
IPPROTO_EGP = 8         # exterior gateway protocol
IPPROTO_PIGP = 9        # private interior gateway
IPPROTO_RCCMON = 10     # BBN RCC Monitoring
IPPROTO_NVPII = 11      # network voice protocol
IPPROTO_PUP = 12        # pup
IPPROTO_ARGUS = 13      # Argus
IPPROTO_EMCON = 14      # EMCON
IPPROTO_XNET = 15       # Cross Net Debugger
IPPROTO_CHAOS = 16      # Chaos
IPPROTO_UDP = 17        # user datagram protocol
IPPROTO_MUX = 18        # Multiplexing
IPPROTO_MEAS = 19       # DCN Measurement Subsystems
IPPROTO_HMP = 20        # Host Monitoring
IPPROTO_PRM = 21        # Packet Radio Measurement
IPPROTO_IDP = 22        # xns idp
IPPROTO_TRUNK1 = 23     # Trunk-1
IPPROTO_TRUNK2 = 24     # Trunk-2
IPPROTO_LEAF1 = 25      # Leaf-1
IPPROTO_LEAF2 = 26      # Leaf-2
IPPROTO_RDP = 27        # Reliable Data
IPPROTO_IRTP = 28       # Reliable Transaction
IPPROTO_TP = 29         # tp-4 w/ class negotiation
IPPROTO_BLT = 30        # Bulk Data Transfer
IPPROTO_NSP = 31        # Network Services
IPPROTO_INP = 32        # Merit Internodal
IPPROTO_SEP = 33        # Sequential Exchange
IPPROTO_3PC = 34        # Third Party Connect
IPPROTO_IDPR = 35       # InterDomain Policy Routing
IPPROTO_XTP = 36        # XTP
IPPROTO_DDP = 37        # Datagram Delivery
IPPROTO_CMTP = 38       # Control Message Transport
IPPROTO_TPXX = 39       # TP++ Transport
IPPROTO_IL = 40         # IL transport protocol
IPPROTO_IPV6 = 41       # IP6 header
IPPROTO_SDRP = 42       # Source Demand Routing
IPPROTO_ROUTING = 43    # IP6 routing header
IPPROTO_FRAGMENT = 44   # IP6 fragmentation header
IPPROTO_IDRP = 45       # InterDomain Routing
IPPROTO_RSVP = 46       # resource reservation
IPPROTO_GRE = 47        # General Routing Encap.
IPPROTO_MHRP = 48       # Mobile Host Routing
IPPROTO_BHA = 49        # BHA
IPPROTO_ESP = 50        # IP6 Encap Sec. Payload
IPPROTO_AH = 51         # IP6 Auth Header
IPPROTO_INLSP = 52      # Integ. Net Layer Security
IPPROTO_SWIPE = 53      # IP with encryption
IPPROTO_NHRP = 54       # Next Hop Resolution
# 55-57: Unassigned
IPPROTO_ICMPV6 = 58     # ICMP6
IPPROTO_NONE = 59       # IP6 no next header
IPPROTO_DSTOPTS = 60    # IP6 destination option
IPPROTO_AHIP = 61       # any host internal protocol
IPPROTO_CFTP = 62       # CFTP
IPPROTO_HELLO = 63      # "hello" routing protocol
IPPROTO_SATEXPAK = 64   # SATNET/Backroom EXPAK
IPPROTO_KRYPTOLAN = 65  # Kryptolan
IPPROTO_RVD = 66        # Remote Virtual Disk
IPPROTO_IPPC = 67       # Pluribus Packet Core
IPPROTO_ADFS = 68       # Any distributed FS
IPPROTO_SATMON = 69     # Satnet Monitoring
IPPROTO_VISA = 70       # VISA Protocol
IPPROTO_IPCV = 71       # Packet Core Utility
IPPROTO_CPNX = 72       # Comp. Prot. Net. Executive
IPPROTO_CPHB = 73       # Comp. Prot. HeartBeat
IPPROTO_WSN = 74        # Wang Span Network
IPPROTO_PVP = 75        # Packet Video Protocol
IPPROTO_BRSATMON = 76   # BackRoom SATNET Monitoring
IPPROTO_ND = 77         # Sun net disk proto (temp.)
IPPROTO_WBMON = 78      # WIDEBAND Monitoring
IPPROTO_WBEXPAK = 79    # WIDEBAND EXPAK
IPPROTO_EON = 80        # ISO cnlp
IPPROTO_VMTP = 81       # VMTP
IPPROTO_SVMTP = 82      # Secure VMTP
IPPROTO_VINES = 83      # Banyon VINES
IPPROTO_TTP = 84        # TTP
IPPROTO_IGP = 85        # NSFNET-IGP
IPPROTO_DGP = 86        # dissimilar gateway prot.
IPPROTO_TCF = 87        # TCF
IPPROTO_IGRP = 88       # Cisco/GXS IGRP
IPPROTO_OSPFIGP = 89    # OSPFIGP
IPPROTO_SRPC = 90       # Strite RPC protocol
IPPROTO_LARP = 91       # Locus Address Resoloution
IPPROTO_MTP = 92        # Multicast Transport
IPPROTO_AX25 = 93       # AX.25 Frames
IPPROTO_IPEIP = 94      # IP encapsulated in IP
IPPROTO_MICP = 95       # Mobile Int.ing control
IPPROTO_SCCSP = 96      # Semaphore Comm. security
IPPROTO_ETHERIP = 97    # Ethernet IP encapsulation
IPPROTO_ENCAP = 98      # encapsulation header
IPPROTO_APES = 99       # any private encr. scheme
IPPROTO_GMTP = 100      # GMTP
IPPROTO_PIM = 103       # Protocol Independent Mcast
IPPROTO_IPCOMP = 108    # payload compression (IPComp)
IPPROTO_PGM = 113       # PGM
IPPROTO_SCTP = 132      # SCTP
IPPROTO_DIVERT = 254    # divert pseudo-protocol
IPPROTO_RAW = 255       # raw IP packet
IPPROTO_MAX = 256
# last return value of *_input(), meaning "all job for this pkt is done".
IPPROTO_DONE = 257








##################### Protocol families are derived from above...

PF_UNSPEC = AF_UNSPEC
PF_LOCAL = AF_LOCAL
PF_UNIX = PF_LOCAL           # backward compatibility
PF_FILE = PF_LOCAL           # used on Linux
PF_INET = AF_INET
PF_IMPLINK = AF_IMPLINK
PF_PUP = AF_PUP
PF_CHAOS = AF_CHAOS
PF_NS = AF_NS
PF_ISO = AF_ISO
PF_OSI = AF_ISO
PF_ECMA = AF_ECMA
PF_DATAKIT = AF_DATAKIT
PF_CCITT = AF_CCITT
PF_SNA = AF_SNA
PF_DECnet = AF_DECnet
PF_DLI = AF_DLI
PF_LAT = AF_LAT
PF_HYLINK = AF_HYLINK
PF_APPLETALK = AF_APPLETALK
PF_ROUTE = AF_ROUTE
PF_LINK = AF_LINK
PF_XTP = pseudo_AF_XTP      # really just proto family, no AF
PF_COIP = AF_COIP
PF_CNT = AF_CNT
PF_SIP = AF_SIP
PF_IPX = AF_IPX             # same format as AF_NS
PF_RTIP = pseudo_AF_RTIP    # same format as AF_INET
PF_PIP = pseudo_AF_PIP
PF_NDRV = AF_NDRV
PF_ISDN = AF_ISDN
PF_KEY = pseudo_AF_KEY
PF_INET6 = AF_INET6
PF_NATM = AF_NATM
PF_SYSTEM = AF_SYSTEM
PF_NETBIOS = AF_NETBIOS
PF_PPP = AF_PPP
PF_RESERVED_36 = AF_RESERVED_36
PF_MAX = AF_MAX



#################### max listen value
SOMAXCONN = 128




#################### for sendmsg and recvmsg

# These aren't the same as in Linux.   There is no MSG_NOSIGNAL, etc.
# Since I copied these from a Mac, these will be different than for Lind

MSG_OOB = 0x1
MSG_PEEK = 0x2
MSG_DONTROUTE = 0x4
MSG_EOR = 0x8
MSG_TRUNC = 0x10
MSG_CTRUNC = 0x20
MSG_WAITALL = 0x40
MSG_DONTWAIT = 0x80
MSG_EOF = 0x100
MSG_WAITSTREAM = 0x200
MSG_FLUSH = 0x400
MSG_HOLD = 0x800
MSG_SEND = 0x1000
MSG_HAVEMORE = 0x2000
MSG_NEEDSA = 0x10000
MSG_NOSIGNAL = 0x4000





#################### for shutdown()

SHUT_RD = 0
SHUT_WR = 1
SHUT_RDWR = 2





################### setsockopt / getsockopt...
SOL_SOCKET = 1
SO_DEBUG = 1
SO_REUSEADDR = 2
SO_TYPE = 3
SO_ERROR = 4
SO_DONTROUTE = 5
SO_BROADCAST = 6
SO_SNDBUF = 7
SO_RCVBUF = 8
SO_SNDBUFFORCE = 32
SO_RCVBUFFORCE = 33
SO_KEEPALIVE = 9
SO_OOBINLINE = 10
SO_NO_CHECK = 11
SO_PRIORITY = 12
SO_LINGER = 13
SO_BSDCOMPAT = 14
SO_REUSEPORT = 15
SO_PASSCRED = 16
SO_PEERCRED = 17
SO_RCVLOWAT = 18
SO_SNDLOWAT = 19
SO_RCVTIMEO = 20
SO_SNDTIMEO = 21

SO_SECURITY_AUTHENTICATION = 22
SO_SECURITY_ENCRYPTION_TRANSPORT = 23
SO_SECURITY_ENCRYPTION_NETWORK = 24

SO_BINDTODEVICE = 25

#/* Socket filtering */
SO_ATTACH_FILTER = 26
SO_DETACH_FILTER = 27

SO_PEERNAME = 28
SO_TIMESTAMP = 29
SCM_TIMESTAMP = SO_TIMESTAMP

SO_ACCEPTCONN = 30

SO_PEERSEC = 31
SO_PASSSEC = 34
SO_TIMESTAMPNS = 35
SCM_TIMESTAMPNS = SO_TIMESTAMPNS

SO_MARK = 36

SO_TIMESTAMPING = 37
SCM_TIMESTAMPING = SO_TIMESTAMPING

SO_PROTOCOL = 38
SO_DOMAIN = 39

SO_RXQ_OVFL = 40


# # More setsockopt / getsockopt

# SO_SNDBUF = 0x1001               # send buffer size
# SO_RCVBUF = 0x1002               # receive buffer size
# SO_SNDLOWAT = 0x1003             # send low-water mark
# SO_RCVLOWAT = 0x1004             # receive low-water mark
# SO_SNDTIMEO = 0x1005             # send timeout
# SO_RCVTIMEO = 0x1006             # receive timeout
# SO_ERROR = 0x1007             # get error status and clear
# SO_TYPE = 0x1008                 # get socket type
# SO_NREAD = 0x1020                # APPLE: get 1st-packet byte count
# SO_NKE = 0x1021                  # APPLE: Install socket-level NKE
# SO_NOSIGPIPE = 0x1022            # APPLE: No SIGPIPE on EPIPE
# SO_NOADDRERR = 0x1023            # APPLE: Returns EADDRNOTAVAIL when src is not available anymore
# SO_NWRITE = 0x1024               # APPLE: Get number of bytes currently in send socket buffer
# SO_REUSESHAREUID = 0x1025        # APPLE: Allow reuse of port/socket by different userids
# SO_NOTIFYCONFLICT = 0x1026       # APPLE: send notification if there is a bind on a port which is already in use
# SO_UPCALLCLOEEWAIT = 0x1027      # APPLE: block on close until an upcall returns
# SO_LINGER_SEC = 0x1080           # linger on close if data present (in seconds)
# SO_RESTRICTIONS = 0x1081         # APPLE: deny inbound/outbound/both/flag set
# SO_RESTRICT_DENYIN = 0x00000001  # flag for SO_RESTRICTIONS - deny inbound
# SO_RESTRICT_DENYOUT = 0x00000002 # flag for SO_RESTRICTIONS - deny outbound
# SO_RESTRICT_DENYSET = 0x80000000 # flag for SO_RESTRICTIONS - deny has been set
# SO_RANDOMPORT = 0x1082           # APPLE: request local port randomization
# SO_NP_EXTENSIONS = 0x1083        # To turn off some POSIX behavior
# SO_LABEL = 0x1010                # socket's MAC label
# SO_PEERLABEL = 0x1011            # socket's peer MAC label

TCP_NODELAY = 0x01           # don't delay send to coalesce packets
TCP_MAXSEG = 0x02            # set maximum segment size
TCP_NOPUSH = 0x04            # don't push last block of write
TCP_NOOPT = 0x08             # don't use TCP options
TCP_KEEPALIVE = 0x10         # idle time used when SO_KEEPALIVE is enabled
TCP_CONNECTIONTIMEOUT = 0x20 # connection timeout
PERSIST_TIMEOUT = 0x40       # time after which a connection in persist timeout
                             # will terminate.
                             # see draft-ananth-tcpm-persist-02.txt
TCP_RXT_CONNDROPTIME = 0x80  # time after which tcp retransmissions will be
                             # stopped and the connection will be dropped
TCP_RXT_FINDROP = 0x100      # When set, a connection is dropped after 3 FINs


# Use this to specify options on a socket.   Use the protocol with setsockopt
# to specify something for all sockets with a protocol
SOL_SOCKET = 1
SOL_TCP = IPPROTO_TCP
SOL_UDP = IPPROTO_UDP


POLLIN = 01  # There is data to read.
POLLPRI	= 02 #There is urgent data to read.
POLLOUT	= 04 # Writing now will not block.
POLLERR = 010 # Error condition.
POLLHUP =  020 # Hung up.
POLLNVAL =  040 # Invalid polling request.

#end include lind_net_constants.py

#begin include serialize.repy
"""
Author: Justin Cappos


Start date: October 9th, 2009

Purpose: A simple library that serializes and deserializes built-in repy types.
This includes strings, integers, floats, booleans, None, complex, tuples, 
lists, sets, frozensets, and dictionaries.

There are no plans for including objects.

Note: that all items are treated as separate references.   This means things
like 'a = []; a.append(a)' will result in an infinite loop.   If you have
'b = []; c = (b,b)' then 'c[0] is c[1]' is True.   After deserialization 
'c[0] is c[1]' is False.

I can add support or detection of this if desired.
"""

# The basic idea is simple.   Say the type (a character) followed by the 
# type specific data.    This is adequate for simple types
# that do not contain other types.   Types that contain other types, have
# a length indicator and then the underlying items listed sequentially.   
# For a dict, this is key1value1key2value2.



def serializedata(data):
  """
   <Purpose>
      Convert a data item of any type into a string such that we can 
      deserialize it later.

   <Arguments>
      data: the thing to seriailize.   Can be of essentially any type except
            objects.

   <Exceptions>
      TypeError if the type of 'data' isn't allowed

   <Side Effects>
      None.

   <Returns>
      A string suitable for deserialization.
  """

  # this is essentially one huge case statement...

  # None
  if type(data) == type(None):
    return 'N'

  # Boolean
  elif type(data) == type(True):
    if data == True:
      return 'BT'
    else:
      return 'BF'

  # Integer / Long
  elif type(data) is int or type(data) is long:
    datastr = str(data) 
    return 'I'+datastr


  # Float
  elif type(data) is float:
    datastr = str(data) 
    return 'F'+datastr


  # Complex
  elif type(data) is complex:
    datastr = str(data) 
    if datastr[0] == '(' and datastr[-1] == ')':
      datastr = datastr[1:-1]
    return 'C'+datastr



  # String
  elif type(data) is str:
    return 'S'+data


  # List or tuple or set or frozenset
  elif type(data) is list or type(data) is tuple or type(data) is set or type(data) is frozenset:
    # the only impact is the first letter...
    if type(data) is list:
      mystr = 'L'
    elif type(data) is tuple:
      mystr = 'T'
    elif type(data) is set:
      mystr = 's'
    elif type(data) is frozenset:
      mystr = 'f'
    else:
      raise Exception("InternalError: not a known type after checking")

    for item in data:
      thisitem = serializedata(item)
      # Append the length of the item, plus ':', plus the item.   1 -> '2:I1'
      mystr = mystr + str(len(thisitem))+":"+thisitem

    mystr = mystr + '0:'

    return mystr


  # dict
  elif type(data) is dict:
    mystr = 'D'

    keysstr = serializedata(data.keys())
    # Append the length of the list, plus ':', plus the list.  
    mystr = mystr + str(len(keysstr))+":"+keysstr
    
    # just plop the values on the end.
    valuestr = serializedata(data.values())
    mystr = mystr + valuestr

    return mystr


  # Unknown!!!
  else:
    raise TypeError("Unknown type '"+str(type(data))+"' for data :"+str(data))



def deserializedata(datastr):
  """
   <Purpose>
      Convert a serialized data string back into its original types.

   <Arguments>
      datastr: the string to deseriailize.

   <Exceptions>
      ValueError if the string is corrupted
      TypeError if the type of 'data' isn't allowed

   <Side Effects>
      None.

   <Returns>
      Items of the original type
  """

  if type(datastr) != str:
    raise TypeError("Cannot deserialize non-string of type '"+str(type(datastr))+"'")
  typeindicator = datastr[0]
  restofstring = datastr[1:]

  # this is essentially one huge case statement...

  # None
  if typeindicator == 'N':
    if restofstring != '':
      raise ValueError("Malformed None string '"+restofstring+"'")
    return None

  # Boolean
  elif typeindicator == 'B':
    if restofstring == 'T':
      return True
    elif restofstring == 'F':
      return False
    raise ValueError("Malformed Boolean string '"+restofstring+"'")

  # Integer / Long
  elif typeindicator == 'I':
    try:
      return int(restofstring) 
    except ValueError:
      raise ValueError("Malformed Integer string '"+restofstring+"'")


  # Float
  elif typeindicator == 'F':
    try:
      return float(restofstring) 
    except ValueError:
      raise ValueError("Malformed Float string '"+restofstring+"'")

  # Float
  elif typeindicator == 'C':
    try:
      return complex(restofstring) 
    except ValueError:
      raise ValueError("Malformed Complex string '"+restofstring+"'")



  # String
  elif typeindicator == 'S':
    return restofstring

  # List / Tuple / set / frozenset / dict
  elif typeindicator == 'L' or typeindicator == 'T' or typeindicator == 's' or typeindicator == 'f':
    # We'll split this and keep adding items to the list.   At the end, we'll
    # convert it to the right type

    thislist = []

    data = restofstring
    # We'll use '0:' as our 'end separator'
    while data != '0:':
      lengthstr, restofdata = data.split(':', 1)
      length = int(lengthstr)

      # get this item, convert to a string, append to the list.
      thisitemdata = restofdata[:length]
      thisitem = deserializedata(thisitemdata)
      thislist.append(thisitem)

      # Now toss away the part we parsed.
      data = restofdata[length:]

    if typeindicator == 'L':
      return thislist
    elif typeindicator == 'T':
      return tuple(thislist)
    elif typeindicator == 's':
      return set(thislist)
    elif typeindicator == 'f':
      return frozenset(thislist)
    else:
      raise Exception("InternalError: not a known type after checking")


  elif typeindicator == 'D':

    lengthstr, restofdata = restofstring.split(':', 1)
    length = int(lengthstr)

    # get this item, convert to a string, append to the list.
    keysdata = restofdata[:length]
    keys = deserializedata(keysdata)

    # The rest should be the values list.
    values = deserializedata(restofdata[length:])

    if type(keys) != list or type(values) != list or len(keys) != len(values):
      raise ValueError("Malformed Dict string '"+restofstring+"'")
    
    thisdict = {}
    for position in xrange(len(keys)):
      thisdict[keys[position]] = values[position]
    
    return thisdict




  # Unknown!!!
  else:
    raise ValueError("Unknown typeindicator '"+str(typeindicator)+"' for data :"+str(restofstring))




#end include serialize.repy

#begin include lind_fs_calls.py
"""
  Author: Justin Cappos
  Module: File system calls for Lind.   This is essentially POSIX written in
          Repy V2.   

  Start Date: December 17th, 2011

  My goal is to write a simple and relatively accurate implementation of POSIX
  in Repy V2.   This module contains most of the file system calls.   A lind
  client can execute those calls and they will be mapped into my Repy V2 
  code where I will more or less faithfully execute them.   Since Repy V2
  does not support permissions, directories, etc., I will fake these.   To 
  do this I will create a metadata file / dictionary which contains 
  metadata of this sort.   I will persist this metadata and re-read it upon
  initialization.

  Rather than do all of the struct packing, etc. here, I will do it in another
  routine.   The reason is that I want to be able to test this in Python / Repy
  without unpacking / repacking.

"""
  
# At a conceptual level, the system works like this:
#   1) Files are written and managed by my program.   The actual name on disk
#      will not correspond in any way with the filename.   The name on disk
#      is chosen by my code and the filename only appears in the metadata.
#   2) A dictionary exists which stores file data.   Since there may be 
#      multiple hard links to a file, the dictionary is keyed by "inode"
#      instead of filename.   The value of each entry is a dictionary that
#      contains the file mode data, size, link count, owner, group, and other 
#      information.
#   3) The metadata for every directory contains a list of filenames in that
#      directory and their associated "inodes".
#   4) "Inodes" are simply unique ids per file and have no other meaning.   
#      They are generated sequentially.
#   5) Every open file has an entry in the filedescriptortable.   This 
#      is a dictionary that is keyed by fd, with the values consisting of
#      a dictionary with the position, flags, a lock, and inode keys.
#      The inode values are used to update / check the file size after writeat 
#      calls and for calls like fstat.
#   6) A file's data is mapped the filename FILEDATAPREFIX+str(inode)
#   7) Open file objects are kept in a separate table, the fileobjecttable that
#      is keyed by inode.  This makes it easier to support multiple open file 
#      descriptors that point to the same file. 
#
# BUG: I created a table which allows one to look up an "inode"
#      given a filename.   It will break certain things in certain weird corner
#      cases with dir symlinks, permissions, etc.   However, it will make the
#      code simpler and faster
#   I called it: fastinodelookuptable = {}
#
#   As with Linux, etc. there is a 'current directory' that calls which take a 
#      filename use as the first part of their path.   All other filenames that
#      do not begin with '/' start from here.
#
# Here is how some example calls work at a high level:
#   unlink: removes filename -> inode map / decrements the link count.  If 
#           the link count is zero, deletes the file.
#   link: increments the link count and adds a new filename -> inode map.  
#   rename: updates the directory's filename -> inode map.
#   getdents: returns data from the directory's filename -> inode map.
#   mkdir / rmdir: creates a directory / removes a directory
#   chdir: sets the current directory for other calls
#   stat / access: provides metadata about a file / directory / etc.
#   open: makes an entry in the file descriptor table for a file
#   read / write: use the file descriptor to perform the action
#   lseek: update the file descriptor table entry for position.


# I'm not overly concerned about efficiency right now.   I'm more worried
# about correctness.   As a result, I'm not going to optimize anything yet.
#


# To describe the metadata format, I'll start at the lowest levels and build
# up.   At a conceptual level, files, directories, symlinks, etc. are at the
# bottom level.   Directories contain references to files, symlinks, and other
# directories.   These are all entries in a table keyed by inode.
#
# A file's metadata looks like this:
#
# {'size':1033, 'uid':1000, 'gid':1000, 'mode':33261, 'linkcount':2,
#  'atime':1323630836, 'ctime':1323630836, 'mtime':1323630836}
# See the stat command for more information about what these mean...
#
# 
# A directory's metadata looks very similar:
# {'size':1033, 'uid':1000, 'gid':1000, 'mode':16877, 
#  'atime':1323630836, 'ctime':1323630836, 'mtime':1323630836,
#  'linkcount':4,    # the number of dir entries...
#  'filename_to_inode_dict': {'foo':1234, '.':102, '..':10, 'bar':2245}
# See the stat command for more information about what these mean...
#
#
# Symbolic links, devices, etc. will be done later (if needed)
#
#
# These are all entries in the inode table.   It is keyed by inode and maps
# to these entries.   The root directory is always at position 
# ROOTDIRECTORYINODE. 
#
#
# At the highest level, the metadata is in a dictionary like this:
#
# filesystemmetadata = {'nextinode':1201,   # the next unused inode number
#                       'dev_id':20,        # the device ID returned to stat
#                       'inodetable': {...} # described above
#

# Store all of the information about the file system in a dict...
# This should not be 0 because this is considered to be deleted

ROOTDIRECTORYINODE = 1

METADATAFILENAME = 'lind.metadata'

FILEDATAPREFIX = 'linddata.'

filesystemmetadata = {}

# A lock that prevents inconsistencies in metadata
filesystemmetadatalock = createlock()


# fast lookup table...   (Should I deprecate this?)
fastinodelookuptable = {}

# contains open file descriptor information... (keyed by fd)
filedescriptortable = {}

# contains file objects... (keyed by inode)
fileobjecttable = {}

# I use this so that I can assign to a global string (currentworkingdirectory)
# without using global, which is blocked by RepyV2
fs_calls_context = {}

# Where we currently are at...

fs_calls_context['currentworkingdirectory'] = '/'

SILENT=True

def warning(*msg):
  if not SILENT:
    for part in msg:
      print part,
    print


# This is raised to return an error...
class SyscallError(Exception):
  """A system call had an error"""


# This is raised if part of a call is not implemented
class UnimplementedError(Exception):
  """A call was called with arguments that are not fully implemented"""


def _load_lower_handle_stubs():
  """The lower file hadles need stubs in the descriptor talbe."""

  filedescriptortable[0] = {'position':0, 'inode':0, 'lock':createlock(), 'flags':O_RDWRFLAGS, 'note':'this is a stub1'}
  filedescriptortable[1] = {'position':0, 'inode':1, 'lock':createlock(), 'flags':O_RDWRFLAGS, 'note':'this is a stub2'}
  filedescriptortable[2] = {'position':0, 'inode':2, 'lock':createlock(), 'flags':O_RDWRFLAGS, 'note':'this is a stub3'}


def load_fs(name=METADATAFILENAME):
  """ Help to correcly load a filesystem, if one exists, otherwise
  make a new empty one.  To do this, check if metadata exists.
  If it doesnt, call _blank_fs_init, if it DOES exist call restore_metadata

  This is the best entry point for programs loading the file subsystem.
  """
  try:
    # lets see if the metadata file is already here?
    f = openfile(name, False)
  except FileNotFoundError, e:
    warning("Note: No filesystem found, building a fresh one.")
    _blank_fs_init()
    load_fs_special_files()
  else:
    f.close()
    try:
      restore_metadata(name)
    except (IndexError, KeyError), e:
      print "Error: Cannot reload filesystem.  Run lind_fsck for details."
      exitall(1)
  _load_lower_handle_stubs()


def load_fs_special_files():
  """ If called adds special files in standard locations.
  Specifically /dev/null, /dev/urandom and /dev/random
  """
  try: 
     mkdir_syscall("/dev", S_IRWXA)
  except SyscallError as e:
    warning( "making /dev failed. Skipping",str(e))

  # load /dev/null
  try:
    mknod_syscall("/dev/null", S_IFCHR, (1,3))
  except SyscallError as e:
    warning("making /dev/null failed. Skipping", str(e))

  # load /dev/urandom
  try:
    mknod_syscall("/dev/urandom", S_IFCHR, (1,9))
  except SyscallError as e:
    warning("making /dev/urandcom failed. Skipping",str(e))

  # load /dev/random
  try:
    mknod_syscall("/dev/random", S_IFCHR, (1,8))
  except SyscallError as e:
    warning("making /dev/random failed. Skipping", str(e))


# To have a simple, blank file system, simply run this block of code.
# 
def _blank_fs_init():

  # kill all left over data files...
  # metadata will be killed on persist.
  for filename in listfiles():
    if filename.startswith(FILEDATAPREFIX):
      removefile(filename)

  # Now setup blank data structures
  filesystemmetadata['nextinode'] = 3
  filesystemmetadata['dev_id'] = 20
  filesystemmetadata['inodetable'] = {}
  filesystemmetadata['inodetable'][ROOTDIRECTORYINODE] = {'size':0, 
            'uid':DEFAULT_UID, 'gid':DEFAULT_GID, 
            'mode':S_IFDIR | S_IRWXA, # directory + all permissions
            'atime':1323630836, 'ctime':1323630836, 'mtime':1323630836,
            'linkcount':2,    # the number of dir entries...
            'filename_to_inode_dict': {'.':ROOTDIRECTORYINODE, 
            '..':ROOTDIRECTORYINODE}}
    
  fastinodelookuptable['/'] = ROOTDIRECTORYINODE

  # it makes no sense this wasn't done before...
  persist_metadata(METADATAFILENAME)



# These are used to initialize and stop the system
def persist_metadata(metadatafilename):

  metadatastring = serializedata(filesystemmetadata)

  
  # open the file (clobber) and write out the information...
  try:
    removefile(metadatafilename)
  except FileNotFoundError:
    pass
  metadatafo = openfile(metadatafilename,True)
  metadatafo.writeat(metadatastring,0)
  metadatafo.close()



def restore_metadata(metadatafilename):
  # should only be called with a fresh system...
  assert(filesystemmetadata == {})

  # open the file and write out the information...
  metadatafo = openfile(metadatafilename,True)
  metadatastring = metadatafo.readat(None, 0)
  metadatafo.close()

  # get the dict we want
  desiredmetadata = deserializedata(metadatastring)

  # I need to put things in the dict, but it's not a global...   so instead
  # add them one at a time.   It should be empty to start with
  for item in desiredmetadata:
    filesystemmetadata[item] = desiredmetadata[item]


  # I need to rebuild the fastinodelookuptable. let's do this!
  _rebuild_fastinodelookuptable()



# I'm already added.
def _recursive_rebuild_fastinodelookuptable_helper(path, inode):
  
  # for each entry in my table...
  for entryname,entryinode in filesystemmetadata['inodetable'][inode]['filename_to_inode_dict'].iteritems():
    
    # if it's . or .. skip it.
    if entryname == '.' or entryname == '..':
      continue

    # always add it...
    entrypurepathname = _get_absolute_path(path+'/'+entryname)
    fastinodelookuptable[entrypurepathname] = entryinode

    # and recurse if a directory...
    if 'filename_to_inode_dict' in filesystemmetadata['inodetable'][entryinode]:
      _recursive_rebuild_fastinodelookuptable_helper(entrypurepathname,entryinode)
    

def _rebuild_fastinodelookuptable():
  # first, empty it...
  for item in fastinodelookuptable:
    del fastinodelookuptable[item]

  # now let's go through and add items...
  
  # I need to add the root.   
  fastinodelookuptable['/'] = ROOTDIRECTORYINODE
  # let's recursively do the rest...
  
  _recursive_rebuild_fastinodelookuptable_helper('/', ROOTDIRECTORYINODE)










######################   Generic Helper functions   #########################



# private helper function that converts a relative path or a path with things
# like foo/../bar to a normal path.
def _get_absolute_path(path):
  
  # should raise an ENOENT error...
  if path == '':
    return path

  # If it's a relative path, prepend the CWD...
  if path[0] != '/':
    path = fs_calls_context['currentworkingdirectory'] + '/' + path


  # now I'll split on '/'.   This gives a list like: ['','foo','bar'] for 
  # '/foo/bar'
  pathlist = path.split('/')

  # let's remove the leading ''
  assert(pathlist[0] == '')
  pathlist = pathlist[1:]

  # Now, let's remove any '.' entries...
  while True:
    try:
      pathlist.remove('.')
    except ValueError:
      break

  # Also remove any '' entries...
  while True:
    try:
      pathlist.remove('')
    except ValueError:
      break

  # NOTE: This makes '/foo/bar/' -> '/foo/bar'.   I think this is okay.
  
  # for a '..' entry, remove the previous entry (if one exists).   This will
  # only work if we go left to right.
  position = 0
  while position < len(pathlist):
    if pathlist[position] == '..':
      # if there is a parent, remove it and this entry.  
      if position > 0:
        del pathlist[position]
        del pathlist[position-1]

        # go back one position and continue...
        position = position -1
        continue

      else:
        # I'm at the beginning.   Remove this, but no need to adjust position
        del pathlist[position]
        continue

    else:
      # it's a normal entry...   move along...
      position = position + 1


  # now let's join the pathlist!
  return '/'+'/'.join(pathlist)


# private helper function
def _get_absolute_parent_path(path):
  return _get_absolute_path(path+'/..')
  



#################### The actual system calls...   #############################




##### FSTATFS  #####


# return statfs data for fstatfs and statfs
def _istatfs_helper(inode):
  """
  """

  # I need to compute the amount of disk available / used
  limits, usage, stoptimes = getresources()

  # I'm going to fake large parts of this.   
  myfsdata = {}

  myfsdata['f_type'] = 0xBEEFC0DE   # unassigned.   New to us...

  myfsdata['f_bsize'] = 4096        # Match the repy V2 block size

  myfsdata['f_blocks'] = int(limits['diskused']) / 4096   

  myfsdata['f_bfree'] = (int(limits['diskused']-usage['diskused'])) / 4096  
  # same as above...
  myfsdata['f_bavail'] = (int(limits['diskused']-usage['diskused'])) / 4096  

  # file nodes...   I think this is infinite...
  myfsdata['f_files'] = 1024*1024*1024

  # free file nodes...   I think this is also infinite...
  myfsdata['f_files'] = 1024*1024*512

  myfsdata['f_fsid'] = filesystemmetadata['dev_id']

  # we don't really have a limit, but let's say 254
  myfsdata['f_namelen'] = 254

  # same as blocksize...
  myfsdata['f_frsize'] = 4096 
  
  # it's supposed to be 5 bytes...   Let's try null characters...
  #CM: should be 8 bytes by my calc
  myfsdata['f_spare'] = '\x00'*8


  return myfsdata


def fstatfs_syscall(fd):
  """ 
    http://linux.die.net/man/2/fstatfs
  """

  # is the file descriptor valid?
  if fd not in filedescriptortable:
    raise SyscallError("fstatfs_syscall","EBADF","The file descriptor is invalid.")

  
  # if so, return the information...
  return _istatfs_helper(filedescriptortable[fd]['inode'])












##### STATFS  #####


def statfs_syscall(path):
  """ 
    http://linux.die.net/man/2/statfs
  """
  # in an abundance of caution, I'll grab a lock...
  filesystemmetadatalock.acquire(True)

  # ... but always release it...
  try:
    truepath = _get_absolute_path(path)

    # is the path there?
    if truepath not in fastinodelookuptable:
      raise SyscallError("statfs_syscall","ENOENT","The path does not exist.")

    thisinode = fastinodelookuptable[truepath]
      
    return _istatfs_helper(thisinode)

  finally:
    filesystemmetadatalock.release()







    




##### ACCESS  #####

def access_syscall(path, amode):
  """
    See: http://linux.die.net/man/2/access
  """

  
  # lock to prevent things from changing while we look this up...
  filesystemmetadatalock.acquire(True)

  # ... but always release the lock
  try:

    # get the actual name.   Remove things like '../foo'
    truepath = _get_absolute_path(path)

    if truepath not in fastinodelookuptable:
      raise SyscallError("access_syscall","ENOENT","A directory in the path does not exist or file not found.")

    # BUG: This code should really walk the directories instead of using this 
    # table...   This will have to be fixed for symlinks to work.
    thisinode = fastinodelookuptable[truepath]


    # BUG: This should take the UID / GID of the requestor in mind

    # if all of the bits for this file are set as requested, then indicate
    # success (return 0)
    if filesystemmetadata['inodetable'][thisinode]['mode'] & amode == amode:
      return 0

    raise SyscallError("access_syscall","EACESS","The requested access is denied.")

  finally:
    persist_metadata(METADATAFILENAME)
    # release the lock
    filesystemmetadatalock.release()






##### CHDIR  #####





def chdir_syscall(path):
  """ 
    http://linux.die.net/man/2/chdir
  """

  # Note: I don't think I need locking here.   I don't modify any state and 
  # only check the fs state once...

  # get the actual name.   Remove things like '../foo'
  truepath = _get_absolute_path(path)

  # If it doesn't exist...
  if truepath not in fastinodelookuptable:
    raise SyscallError("chdir_syscall","ENOENT","A directory in the path does not exist.")

  # let's update and return success (0)
  fs_calls_context['currentworkingdirectory'] = truepath
  

  return 0




##### MKDIR  #####

def mkdir_syscall(path, mode):
  """ 
    http://linux.die.net/man/2/mkdir
  """

  # lock to prevent things from changing while we look this up...
  filesystemmetadatalock.acquire(True)

  # ... but always release it...
  try:
    if path == '':
      raise SyscallError("mkdir_syscall","ENOENT","Path does not exist.")

    truepath = _get_absolute_path(path)

    # is the path there?
    if truepath in fastinodelookuptable:
      raise SyscallError("mkdir_syscall","EEXIST","The path exists.")

      
    # okay, it doesn't exist (great!).   Does it's parent exist and is it a 
    # dir?
    trueparentpath = _get_absolute_parent_path(path)

    if trueparentpath not in fastinodelookuptable:
      raise SyscallError("mkdir_syscall","ENOENT","Path does not exist.")

    parentinode = fastinodelookuptable[trueparentpath]
    if not IS_DIR(filesystemmetadata['inodetable'][parentinode]['mode']):
      raise SyscallError("mkdir_syscall","ENOTDIR","Path's parent is not a directory.")


    # TODO: I should check permissions...


    assert(mode & S_IRWXA == mode)

    # okay, great!!!   We're ready to go!   Let's make the new directory...
    dirname = truepath.split('/')[-1]

    # first, make the new directory...
    newinode = filesystemmetadata['nextinode']
    filesystemmetadata['nextinode'] += 1

    newinodeentry = {'size':0, 'uid':DEFAULT_UID, 'gid':DEFAULT_GID, 
            'mode':mode | S_IFDIR,  # DIR+rwxr-xr-x
            # BUG: I'm listing some arbitrary time values.  I could keep a time
            # counter too.
            'atime':1323630836, 'ctime':1323630836, 'mtime':1323630836,
            'linkcount':2,    # the number of dir entries...
            'filename_to_inode_dict': {'.':newinode, '..':parentinode}}
    
    # ... and put it in the table..
    filesystemmetadata['inodetable'][newinode] = newinodeentry


    filesystemmetadata['inodetable'][parentinode]['filename_to_inode_dict'][dirname] = newinode
    # increment the link count on the dir...
    filesystemmetadata['inodetable'][parentinode]['linkcount'] += 1

    # finally, update the fastinodelookuptable and return success!!!
    fastinodelookuptable[truepath] = newinode
    
    return 0

  finally:
    persist_metadata(METADATAFILENAME)
    filesystemmetadatalock.release()







##### RMDIR  #####

def rmdir_syscall(path):
  """ 
    http://linux.die.net/man/2/rmdir
  """

  # lock to prevent things from changing while we look this up...
  filesystemmetadatalock.acquire(True)

  # ... but always release it...
  try:
    truepath = _get_absolute_path(path)

    # Is it the root?
    if truepath == '/':
      raise SyscallError("rmdir_syscall","EINVAL","Cannot remove the root directory.")
      
    # is the path there?
    if truepath not in fastinodelookuptable:
      raise SyscallError("rmdir_syscall","EEXIST","The path does not exist.")

    thisinode = fastinodelookuptable[truepath]
      
    # okay, is it a directory?
    if not IS_DIR(filesystemmetadata['inodetable'][thisinode]['mode']):
      raise SyscallError("rmdir_syscall","ENOTDIR","Path is not a directory.")

    # Is it empty?
    if filesystemmetadata['inodetable'][thisinode]['linkcount'] > 2:
      raise SyscallError("rmdir_syscall","ENOTEMPTY","Path is not empty.")

    # TODO: I should check permissions...


    trueparentpath = _get_absolute_parent_path(path)
    parentinode = fastinodelookuptable[trueparentpath]


    # remove the entry from the inode table...
    del filesystemmetadata['inodetable'][thisinode]


    # We're ready to go!   Let's clean up the file entry
    dirname = truepath.split('/')[-1]
    # remove the entry from the parent...

    del filesystemmetadata['inodetable'][parentinode]['filename_to_inode_dict'][dirname]
    # decrement the link count on the dir...
    filesystemmetadata['inodetable'][parentinode]['linkcount'] -= 1

    # finally, clean up the fastinodelookuptable and return success!!!
    del fastinodelookuptable[truepath]
    
    return 0

  finally:
    persist_metadata(METADATAFILENAME)
    filesystemmetadatalock.release()









##### LINK  #####


def link_syscall(oldpath, newpath):
  """ 
    http://linux.die.net/man/2/link
  """

  # lock to prevent things from changing while we look this up...
  filesystemmetadatalock.acquire(True)

  # ... but always release it...
  try:
    trueoldpath = _get_absolute_path(oldpath)

    # is the old path there?
    if trueoldpath not in fastinodelookuptable:
      raise SyscallError("link_syscall","ENOENT","Old path does not exist.")

    oldinode = fastinodelookuptable[trueoldpath]
    # is oldpath a directory?
    if IS_DIR(filesystemmetadata['inodetable'][oldinode]['mode']):
      raise SyscallError("link_syscall","EPERM","Old path is a directory.")
  
    # TODO: I should check permissions...

    # okay, the old path info seems fine...
    
    if newpath == '':
      raise SyscallError("link_syscall","ENOENT","New path does not exist.")

    truenewpath = _get_absolute_path(newpath)

    # does the newpath exist?   It shouldn't
    if truenewpath in fastinodelookuptable:
      raise SyscallError("link_syscall","EEXIST","newpath already exists.")
      
    # okay, it doesn't exist (great!).   Does it's parent exist and is it a 
    # dir?
    truenewparentpath = _get_absolute_parent_path(newpath)

    if truenewparentpath not in fastinodelookuptable:
      raise SyscallError("link_syscall","ENOENT","New path does not exist.")

    newparentinode = fastinodelookuptable[truenewparentpath]
    if not IS_DIR(filesystemmetadata['inodetable'][newparentinode]['mode']):
      raise SyscallError("link_syscall","ENOTDIR","New path's parent is not a directory.")


    # TODO: I should check permissions...



    # okay, great!!!   We're ready to go!   Let's make the file...
    newfilename = truenewpath.split('/')[-1]
    # first, make the directory entry...
    filesystemmetadata['inodetable'][newparentinode]['filename_to_inode_dict'][newfilename] = oldinode
    # increment the link count on the dir...
    filesystemmetadata['inodetable'][newparentinode]['linkcount'] += 1

    # ... and the file itself
    filesystemmetadata['inodetable'][oldinode]['linkcount'] += 1

    # finally, update the fastinodelookuptable and return success!!!
    fastinodelookuptable[truenewpath] = oldinode
    
    return 0

  finally:
    persist_metadata(METADATAFILENAME)
    filesystemmetadatalock.release()






##### UNLINK  #####



def unlink_syscall(path):
  """ 
    http://linux.die.net/man/2/unlink
  """

  # lock to prevent things from changing while we do this...
  filesystemmetadatalock.acquire(True)

  # ... but always release it...
  try:
    truepath = _get_absolute_path(path)

    # is the path there?
    if truepath not in fastinodelookuptable:
      raise SyscallError("unlink_syscall","ENOENT","The path does not exist.")

    thisinode = fastinodelookuptable[truepath]
      
    # okay, is it a directory?
    if IS_DIR(filesystemmetadata['inodetable'][thisinode]['mode']):
      raise SyscallError("unlink_syscall","EISDIR","Path is a directory.")

    # TODO: I should check permissions...


    trueparentpath = _get_absolute_parent_path(path)
    parentinode = fastinodelookuptable[trueparentpath]




    # We're ready to go!   Let's clean up the file entry
    dirname = truepath.split('/')[-1]
    # remove the entry from the parent...

    del filesystemmetadata['inodetable'][parentinode]['filename_to_inode_dict'][dirname]
    # decrement the link count on the dir...
    filesystemmetadata['inodetable'][parentinode]['linkcount'] -= 1

    # clean up the fastinodelookuptable
    del fastinodelookuptable[truepath]


    # decrement the link count...
    filesystemmetadata['inodetable'][thisinode]['linkcount'] -= 1

    # If zero, remove the entry from the inode table
    if filesystemmetadata['inodetable'][thisinode]['linkcount'] == 0:
      del filesystemmetadata['inodetable'][thisinode]

      # TODO: I also would remove the file.   However, I need to do special
      # things if it's open, like wait until it is closed to remove it.
    
    return 0

  finally:
    persist_metadata(METADATAFILENAME)
    filesystemmetadatalock.release()






##### STAT  #####



def stat_syscall(path):
  """ 
    http://linux.die.net/man/2/stat
  """
  # in an abundance of caution, I'll grab a lock...
  filesystemmetadatalock.acquire(True)

  # ... but always release it...
  try:
    truepath = _get_absolute_path(path)

    # is the path there?
    if truepath not in fastinodelookuptable:
      raise SyscallError("stat_syscall","ENOENT","The path does not exist.")

    thisinode = fastinodelookuptable[truepath]
    
    # If its a character file, call the helper function.
    if IS_CHR(filesystemmetadata['inodetable'][thisinode]['mode']):
      return _istat_helper_chr_file(thisinode)
   
    return _istat_helper(thisinode)

  finally:
    persist_metadata(METADATAFILENAME)
    filesystemmetadatalock.release()

   


##### FSTAT  #####

def fstat_syscall(fd):
  """ 
    http://linux.die.net/man/2/fstat
  """
  # TODO: I don't handle socket objects.   I should return something like: 
  # st_mode=49590, st_ino=0, st_dev=0L, st_nlink=0, st_uid=501, st_gid=20, 
  # st_size=0, st_atime=0, st_mtime=0, st_ctime=0

  # is the file descriptor valid?
  if fd not in filedescriptortable:
    raise SyscallError("fstat_syscall","EBADF","The file descriptor is invalid.")

  # if so, return the information...
  inode = filedescriptortable[fd]['inode']
  if fd in [0,1,2] or \
    (filedescriptortable[fd] is filedescriptortable[0] or \
     filedescriptortable[fd] is filedescriptortable[1] or \
     filedescriptortable[fd] is filedescriptortable[2] \
    ):
    return (filesystemmetadata['dev_id'],          # st_dev
          inode,                                 # inode
            49590, #mode
          1,  # links
          DEFAULT_UID, # uid
          DEFAULT_GID, #gid
          0,                                     # st_rdev     ignored(?)
          0, # size
          0,                                     # st_blksize  ignored(?)
          0,                                     # st_blocks   ignored(?)
          0,
          0,                                     # atime ns
          0,
          0,                                     # mtime ns
          0,
          0,                                     # ctime ns
        )
  if IS_CHR(filesystemmetadata['inodetable'][inode]['mode']):
    return _istat_helper_chr_file(inode)
  return _istat_helper(inode)



# private helper routine that returns stat data given an inode
def _istat_helper(inode):
  ret =  (filesystemmetadata['dev_id'],          # st_dev
          inode,                                 # inode
          filesystemmetadata['inodetable'][inode]['mode'],
          filesystemmetadata['inodetable'][inode]['linkcount'],
          filesystemmetadata['inodetable'][inode]['uid'],
          filesystemmetadata['inodetable'][inode]['gid'],
          0,                                     # st_rdev     ignored(?)
          filesystemmetadata['inodetable'][inode]['size'],
          0,                                     # st_blksize  ignored(?)
          0,                                     # st_blocks   ignored(?)
          filesystemmetadata['inodetable'][inode]['atime'],
          0,                                     # atime ns
          filesystemmetadata['inodetable'][inode]['mtime'],
          0,                                     # mtime ns
          filesystemmetadata['inodetable'][inode]['ctime'],
          0,                                     # ctime ns
        )
  return ret






##### OPEN  #####


# get the next free file descriptor
def get_next_fd():
  # let's get the next available fd number.   The standard says we need to 
  # return the lowest open fd number.
  for fd in range(STARTINGFD, MAX_FD):
    if not fd in filedescriptortable:
      return fd

  raise SyscallError("open_syscall","EMFILE","The maximum number of files are open.")
  

def open_syscall(path, flags, mode):
  """ 
    http://linux.die.net/man/2/open
  """

  # in an abundance of caution, lock...   I think this should only be needed
  # with O_CREAT flags...
  filesystemmetadatalock.acquire(True)

  # ... but always release it...
  try:
    if path == '':
      raise SyscallError("open_syscall","ENOENT","The file does not exist.")

    truepath = _get_absolute_path(path)

    # is the file missing?
    if truepath not in fastinodelookuptable:

      # did they use O_CREAT?
      if not O_CREAT & flags:
        raise SyscallError("open_syscall","ENOENT","The file does not exist.")
      
      # okay, it doesn't exist (great!).   Does it's parent exist and is it a 
      # dir?
      trueparentpath = _get_absolute_parent_path(path)

      if trueparentpath not in fastinodelookuptable:
        raise SyscallError("open_syscall","ENOENT","Path does not exist.")

      parentinode = fastinodelookuptable[trueparentpath]
      if not IS_DIR(filesystemmetadata['inodetable'][parentinode]['mode']):
        raise SyscallError("open_syscall","ENOTDIR","Path's parent is not a directory.")



      # okay, great!!!   We're ready to go!   Let's make the new file...
      filename = truepath.split('/')[-1]

      # first, make the new file's entry...
      newinode = filesystemmetadata['nextinode']
      filesystemmetadata['nextinode'] += 1

      # be sure there aren't extra mode bits...   No errno seems to exist for 
      # this.
      assert(mode & (S_IRWXA|S_FILETYPEFLAGS) == mode)

      effective_mode = (S_IFCHR | mode) if (S_IFCHR & flags) != 0 else (S_IFREG | mode)

      newinodeentry = {'size':0, 'uid':DEFAULT_UID, 'gid':DEFAULT_GID, 
            'mode':effective_mode,
            # BUG: I'm listing some arbitrary time values.  I could keep a time
            # counter too.
            'atime':1323630836, 'ctime':1323630836, 'mtime':1323630836,
            'linkcount':1}
    
      # ... and put it in the table..
      filesystemmetadata['inodetable'][newinode] = newinodeentry


      # let's make the parent point to it...
      filesystemmetadata['inodetable'][parentinode]['filename_to_inode_dict'][filename] = newinode
      # ... and increment the link count on the dir...
      filesystemmetadata['inodetable'][parentinode]['linkcount'] += 1

      # finally, update the fastinodelookuptable
      fastinodelookuptable[truepath] = newinode

      # this file must not exist or it's an internal error!!!
      openfile(FILEDATAPREFIX+str(newinode),True).close()

    # if the file did exist, were we told to create with exclusion?
    else:
      # did they use O_CREAT and O_EXCL?
      if O_CREAT & flags and O_EXCL & flags:
        raise SyscallError("open_syscall","EEXIST","The file exists.")

      # This file should be removed.   If O_RDONLY is set, the behavior
      # is undefined, so this is okay, I guess...
      if O_TRUNC & flags:
        inode = fastinodelookuptable[truepath]

        # if it exists, close the existing file object so I can remove it...
        if inode in fileobjecttable:
          fileobjecttable[inode].close()
          # reset the size to 0
          filesystemmetadata['inodetable'][inode]['size'] = 0

        # remove the file...
        removefile(FILEDATAPREFIX+str(inode))

        # always open the file.
        fileobjecttable[inode] = openfile(FILEDATAPREFIX+str(inode),True)


    # TODO: I should check permissions...

    # At this point, the file will exist... 

    # Let's find the inode
    inode = fastinodelookuptable[truepath]

    
    # get the next fd so we can use it...
    thisfd = get_next_fd()
  

    # Note, directories can be opened (to do getdents, etc.).   We shouldn't
    # actually open something in this case...
    # Is it a regular file?
    if IS_REG(filesystemmetadata['inodetable'][inode]['mode']):
      # this is a regular file.  If it's not open, let's open it! 
      if inode not in fileobjecttable:
        thisfo = openfile(FILEDATAPREFIX+str(inode),False)
        fileobjecttable[inode] = thisfo

    # I'm going to assume that if you use O_APPEND I only need to 
    # start the pointer in the right place.
    if O_APPEND & flags:
      position = filesystemmetadata['inodetable'][inode]['size']
    else:
      # else, let's start at the beginning
      position = 0
    

    # TODO handle read / write locking, etc.

    # Add the entry to the table!

    filedescriptortable[thisfd] = {'position':position, 'inode':inode, 'lock':createlock(), 'flags':flags&O_RDWRFLAGS}

    # Done!   Let's return the file descriptor.
    return thisfd

  finally:
    persist_metadata(METADATAFILENAME)
    filesystemmetadatalock.release()







##### CREAT  #####

def creat_syscall(pathname, mode):
  """ 
    http://linux.die.net/man/2/creat
  """

  try:

    return open_syscall(pathname, O_CREAT | O_TRUNC | O_WRONLY, mode)
  
  except SyscallError, e:
    # If it's a system call error, return our call name instead.
    assert(e[0]=='open_syscall')
    
    raise SyscallError('creat_syscall',e[1],e[2])
  






##### LSEEK  #####

def lseek_syscall(fd, offset, whence):
  """ 
    http://linux.die.net/man/2/lseek
  """

  # check the fd
  if fd not in filedescriptortable:
    raise SyscallError("lseek_syscall","EBADF","Invalid file descriptor.")

  # if we are any of the odd handles(stderr, sockets), we cant seek, so just report we are at 0
  if filedescriptortable[fd]['inode'] in [0,1,2]:
    return 0
  # Acquire the fd lock...
  filedescriptortable[fd]['lock'].acquire(True)


  # ... but always release it...
  try:

    # we will need the file size in a moment, but also need to check the type
    try:
      inode = filedescriptortable[fd]['inode']
    except KeyError:
      raise SyscallError("lseek_syscall","ESPIPE","This is a socket, not a file.")
    
    # Let's figure out if this has a length / pointer...
    if IS_REG(filesystemmetadata['inodetable'][inode]['mode']):
      # straightforward if it is a file...
      filesize = filesystemmetadata['inodetable'][inode]['size']

    elif IS_DIR(filesystemmetadata['inodetable'][inode]['mode']):
      # if a directory, let's use the number of entries
      filesize = len(filesystemmetadata['inodetable'][inode]['filename_to_inode_dict'])

    else:
      # otherwise we don't know
      raise SyscallError("lseek_syscall","EINVAL","File descriptor does not refer to a regular file or directory.")
      

    # Figure out where we will seek to and check it...
    if whence == SEEK_SET:
      eventualpos = offset
    elif whence == SEEK_CUR:
      eventualpos = filedescriptortable[fd]['position']+offset
    elif whence == SEEK_END:
      eventualpos = filesize+offset
    else:
      raise SyscallError("lseek_syscall","EINVAL","Invalid whence.")

    # did we fall off the front?
    if eventualpos < 0:
      raise SyscallError("lseek_syscall","EINVAL","Seek before position 0 in file.")

    # did we fall off the back?
    # if so, we'll handle this when we do a write.   The correct behavior is
    # to write '\0' bytes between here and that pos.

    # do the seek and return success (the position)!
    filedescriptortable[fd]['position'] = eventualpos

    return eventualpos

  finally:
    # ... release the lock
    filedescriptortable[fd]['lock'].release()







##### READ  #####

def read_syscall(fd, count):
  """ 
    http://linux.die.net/man/2/read
  """

  # BUG: I probably need a filedescriptortable lock to prevent an untimely
  # close call or similar from messing everything up...

  # check the fd
  if fd not in filedescriptortable:
    raise SyscallError("read_syscall","EBADF","Invalid file descriptor.")

  # Is it open for reading?
  if IS_WRONLY(filedescriptortable[fd]['flags']): 
    raise SyscallError("read_syscall","EBADF","File descriptor is not open for reading.")

  # Acquire the fd lock...
  filedescriptortable[fd]['lock'].acquire(True)

  # ... but always release it...
  try:

    # get the inode so I can and check the mode (type)
    inode = filedescriptortable[fd]['inode']

    # If its a character file, call the helper function.
    if IS_CHR(filesystemmetadata['inodetable'][inode]['mode']):
      return _read_chr_file(inode, count)

    # Is it anything other than a regular file?
    if not IS_REG(filesystemmetadata['inodetable'][inode]['mode']):
      raise SyscallError("read_syscall","EINVAL","File descriptor does not refer to a regular file.")
      

    # let's do a readat!
    position = filedescriptortable[fd]['position']
    data = fileobjecttable[inode].readat(count,position)

    # and update the position
    filedescriptortable[fd]['position'] += len(data)

    return data

  finally:
    # ... release the lock
    filedescriptortable[fd]['lock'].release()









##### WRITE  #####



def write_syscall(fd, data):
  """ 
    http://linux.die.net/man/2/write
  """

  # BUG: I probably need a filedescriptortable lock to prevent an untimely
  # close call or similar from messing everything up...

  # check the fd
  if fd not in filedescriptortable:
    raise SyscallError("write_syscall","EBADF","Invalid file descriptor.")

  if filedescriptortable[fd]['inode'] in [0,1,2]:
    return len(data)

  # Is it open for writing?
  if IS_RDONLY(filedescriptortable[fd]['flags']): 
    raise SyscallError("write_syscall","EBADF","File descriptor is not open for writing.")


  # Acquire the fd lock...
  filedescriptortable[fd]['lock'].acquire(True)

  # ... but always release it...
  try:

    # get the inode so I can update the size (if needed) and check the type
    inode = filedescriptortable[fd]['inode']

    # If its a character file, call the helper function.
    if IS_CHR(filesystemmetadata['inodetable'][inode]['mode']):
      return _write_chr_file(inode, data)

    # Is it anything other than a regular file?
    if not IS_REG(filesystemmetadata['inodetable'][inode]['mode']):
      raise SyscallError("write_syscall","EINVAL","File descriptor does not refer to a regular file.")
      

    # let's get the position...
    position = filedescriptortable[fd]['position']
    
    # and the file size...
    filesize = filesystemmetadata['inodetable'][inode]['size']

    # if the position is past the end of the file, write '\0' bytes to fill
    # up the gap...
    blankbytecount = position - filesize

    if blankbytecount > 0:
      # let's write the blank part at the end of the file...
      fileobjecttable[inode].writeat('\0'*blankbytecount,filesize)
      

    # writeat never writes less than desired in Repy V2.
    fileobjecttable[inode].writeat(data,position)

    # and update the position
    filedescriptortable[fd]['position'] += len(data)

    # update the file size if we've extended it
    if filedescriptortable[fd]['position'] > filesize:
      filesystemmetadata['inodetable'][inode]['size'] = filedescriptortable[fd]['position']
      
    # we always write it all, so just return the length of what we were passed.
    # We do not mention whether we write blank data (if position is after the 
    # end)
    return len(data)

  finally:
    # ... release the lock
    filedescriptortable[fd]['lock'].release()







##### CLOSE  #####

# private helper.   Get the fds for an inode (or [] if none)
def _lookup_fds_by_inode(inode):
  returnedfdlist = []
  for fd in filedescriptortable:
    if not IS_SOCK_DESC(fd) and filedescriptortable[fd]['inode'] == inode:
      returnedfdlist.append(fd)
  return returnedfdlist


# is this file descriptor a socket? 
def IS_SOCK_DESC(fd):
  if 'domain' in filedescriptortable[fd]:
    return True
  else:
    return False



# BAD this is copied from net_calls, but there is no way to get it
def _cleanup_socket(fd):
  if 'socketobjectid' in filedescriptortable[fd]:
    thesocket = socketobjecttable[filedescriptortable[fd]['socketobjectid']]
    thesocket.close()
    localport = filedescriptortable[fd]['localport']
    try:
      _release_localport(localport, filedescriptortable[fd]['protocol'])
    except KeyError:
      pass
    del socketobjecttable[filedescriptortable[fd]['socketobjectid']]
    del filedescriptortable[fd]['socketobjectid']
    
    filedescriptortable[fd]['state'] = NOTCONNECTED
    return 0




# private helper that allows this to be called in other places (like dup2)
# without changing to re-entrant locks
def _close_helper(fd):
  # if we are a socket, we dont change disk metadata
  if IS_SOCK_DESC(fd):
    _cleanup_socket(fd)
    return 0

  # get the inode for the filedescriptor
  inode = filedescriptortable[fd]['inode']

  # If it's not a regular file, we have nothing to close...
  if not IS_REG(filesystemmetadata['inodetable'][inode]['mode']):

    # double check that this isn't in the fileobjecttable
    if inode in fileobjecttable:
      raise Exception("Internal Error: non-regular file in fileobjecttable")
   
    # and return success
    return 0

  # so it's a regular file.

  # get the list of file descriptors for the inode
  fdsforinode = _lookup_fds_by_inode(inode)

  # I should be in there!
  assert(fd in fdsforinode)

  # I should only close here if it's the last use of the file.   This can
  # happen due to dup, multiple opens, etc.
  if len(fdsforinode) > 1:
    # Is there more than one descriptor open?   If so, return success
    return 0

  # now let's close it and remove it from the table
  fileobjecttable[inode].close()

  del fileobjecttable[inode]

  # success!
  return 0



def close_syscall(fd):
  """ 
    http://linux.die.net/man/2/close
  """

  # BUG: I probably need a filedescriptortable lock to prevent race conditions
  # check the fd
  if fd not in filedescriptortable:
    raise SyscallError("close_syscall","EBADF","Invalid file descriptor.")
  try:
    if filedescriptortable[fd]['inode'] in [0,1,2]:
      return 0
  except KeyError:
    pass
  # Acquire the fd lock, if there is one.
  if 'lock' in filedescriptortable[fd]:
    filedescriptortable[fd]['lock'].acquire(True)

  # ... but always release it...
  try:
    return _close_helper(fd)

  finally:
    # ... release the lock, if there is one
    persist_metadata(METADATAFILENAME)
    if 'lock' in filedescriptortable[fd]:
      filedescriptortable[fd]['lock'].release()
    del filedescriptortable[fd]







##### DUP2  #####


# private helper that allows this to be used by dup
def _dup2_helper(oldfd,newfd):

  # if the new file descriptor is too low or too high
  # NOTE: I want to support dup2 being used to replace STDERR, STDOUT, etc.
  #      The Lind code may pass me descriptors less than STARTINGFD
  if newfd >= MAX_FD or newfd < 0:
    # BUG: the STARTINGFD isn't really too low.   It's just lower than we
    # support
    raise SyscallError("dup2_syscall","EBADF","Invalid new file descriptor.")

  # if they are equal, return them
  if newfd == oldfd:
    return newfd

  # okay, they are different.   If the new fd exists, close it.
  if newfd in filedescriptortable:
    # should not result in an error.   This only occurs on a bad fd 
    _close_helper(newfd)


  # Okay, we need the new and old to point to the same thing.
  # NOTE: I am not making a copy here!!!   They intentionally both
  # refer to the same instance because manipulating the position, etc.
  # impacts both.
  filedescriptortable[newfd] = filedescriptortable[oldfd]

  return newfd




def dup2_syscall(oldfd,newfd):
  """ 
    http://linux.die.net/man/2/dup2
  """

  # check the fd
  if oldfd not in filedescriptortable:
    raise SyscallError("dup2_syscall","EBADF","Invalid old file descriptor.")

  # Acquire the fd lock...
  filedescriptortable[oldfd]['lock'].acquire(True)


  # ... but always release it...
  try:
    return _dup2_helper(oldfd, newfd)

  finally:
    # ... release the lock
    filedescriptortable[oldfd]['lock'].release()




##### DUP  #####

def dup_syscall(fd):
  """ 
    http://linux.die.net/man/2/dup
  """


  # check the fd
  if fd not in filedescriptortable and fd >= STARTINGFD:
    raise SyscallError("dup_syscall","EBADF","Invalid old file descriptor.")

  # Acquire the fd lock...
  filedescriptortable[fd]['lock'].acquire(True)

  try: 
    # get the next available file descriptor
    try:
      nextfd = get_next_fd()
    except SyscallError, e:
      # If it's an error getting the fd, return our call name instead.
      assert(e[0]=='open_syscall')
    
      raise SyscallError('dup_syscall',e[1],e[2])
  
    # this does the work.   It should _never_ raise an exception given the
    # checks we've made...
    return _dup2_helper(fd, nextfd)
  
  finally:
    # ... release the lock
    filedescriptortable[fd]['lock'].release()
  






##### FCNTL  #####



def fcntl_syscall(fd, cmd, *args):
  """ 
    http://linux.die.net/man/2/fcntl
  """
  # this call is totally crazy!   I'll just implement the basics and add more
  # as is needed.

  # BUG: I probably need a filedescriptortable lock to prevent race conditions

  # check the fd
  if fd not in filedescriptortable:
    raise SyscallError("fcntl_syscall","EBADF","Invalid file descriptor.")

  # Acquire the fd lock...
  filedescriptortable[fd]['lock'].acquire(True)

  # ... but always release it...
  try:
    # if we're getting the flags, return them... (but this is just CLO_EXEC, 
    # so ignore)
    if cmd == F_GETFD:
      if len(args) > 0:
        raise SyscallError("fcntl_syscall", "EINVAL", "Argument is more than\
          maximun allowable value.")
      return int((filedescriptortable[fd]['flags'] & FD_CLOEXEC) != 0)

    # set the flags...
    elif cmd == F_SETFD:
      assert(len(args) == 1)
      filedescriptortable[fd]['flags'] |= args[0]
      return 0

    # if we're getting the flags, return them...
    elif cmd == F_GETFL:
      assert(len(args) == 0)
      return filedescriptortable[fd]['flags']

    # set the flags...
    elif cmd == F_SETFL:
      assert(len(args) == 1)
      assert(type(args[0]) == int or type(args[0]) == long)
      filedescriptortable[fd]['flags'] = args[0]
      return 0

    # This is saying we'll get signals for this.   Let's punt this...
    elif cmd == F_GETOWN:
      assert(len(args) == 0)
      # Saying traditional SIGIO behavior...
      return 0

    # indicate that we want to receive signals for this FD...
    elif cmd == F_SETOWN:
      assert(len(args) == 1)
      assert(type(args[0]) == int or type(args[0]) == long)
      # this would almost certainly say our PID (if positive) or our process
      # group (if negative).   Either way, we do nothing and return success.
      return 0


    else:
      # This is either unimplemented or malformed.   Let's raise
      # an exception.
      raise UnimplementedError('FCNTL with command '+str(cmd)+' is not yet implemented.')

  finally:
    # ... release the lock
    filedescriptortable[fd]['lock'].release()









##### GETDENTS  #####



def getdents_syscall(fd, quantity):
  """ 
    http://linux.die.net/man/2/getdents
  """

  # BUG: I probably need a filedescriptortable lock to prevent race conditions

  # BUG BUG BUG: Do I really understand this spec!?!?!?!

  # check the fd
  if fd not in filedescriptortable:
    raise SyscallError("getdents_syscall","EBADF","Invalid file descriptor.")

  # Sanitizing the Input, there are people who would send other types too.
  if not isinstance(quantity, (int, long)):
    raise SyscallError("getdents_syscall","EINVAL","Invalid type for buffer size.")

  # This is the minimum number of bytes, that should be provided.
  if quantity < 24:
    raise SyscallError("getdents_syscall","EINVAL","Buffer size is too small.")

  # Acquire the fd lock...
  filedescriptortable[fd]['lock'].acquire(True)

  # ... but always release it...
  try:

    # get the inode so I can read the directory entries
    inode = filedescriptortable[fd]['inode']

    # Is it a directory?
    if not IS_DIR(filesystemmetadata['inodetable'][inode]['mode']):
      raise SyscallError("getdents_syscall","EINVAL","File descriptor does not refer to a directory.")
      
    returninodefntuplelist = []
    bufferedquantity = 0

    # let's move the position forward...
    startposition = filedescriptortable[fd]['position']
    # return tuple with inode, name, type tuples...
    for entryname,entryinode in list(filesystemmetadata['inodetable'][inode]['filename_to_inode_dict'].iteritems())[startposition:]:
      # getdents returns the mode also (at least on Linux)...
      entrytype = get_direnttype_from_mode(filesystemmetadata['inodetable'][entryinode]['mode'])

      # Get the size of each entry, the size should be a multiple of 8.
      # The size of each entry is determined by sizeof(struct linux_dirent) which is 20 bytes plus the length of name of the file.
      # So, size of each entry becomes : 21 => 24, 26 => 32, 32 => 32.
      currentquantity = (((20 + len(entryname)) + 7) / 8) * 8

      # This is the overall size of entries parsed till now, if size exceeds given size, then stop parsing and return
      bufferedquantity += currentquantity
      if bufferedquantity > quantity:
        break

      returninodefntuplelist.append((entryinode, entryname, entrytype, currentquantity))

    # and move the position along.   Go no further than the end...
    filedescriptortable[fd]['position'] = min(startposition + len(returninodefntuplelist),\
      len(filesystemmetadata['inodetable'][inode]['filename_to_inode_dict']))
    
    return returninodefntuplelist

  finally:
    # ... release the lock
    filedescriptortable[fd]['lock'].release()



#### CHMOD ####


def chmod_syscall(path, mode):
  """
    http://linux.die.net/man/2/chmod
  """
  # in an abundance of caution, I'll grab a lock...
  filesystemmetadatalock.acquire(True)

  # ... but always release it...
  try:
    truepath = _get_absolute_path(path)

    # is the path there?
    if truepath not in fastinodelookuptable:
      raise SyscallError("chmod_syscall", "ENOENT", "The path does not exist.")

    thisinode = fastinodelookuptable[truepath]

    # be sure there aren't extra mode bits... No errno seems to exist for this
    assert(mode & (S_IRWXA|S_FILETYPEFLAGS) == mode)

    # should overwrite any previous permissions, according to POSIX.   However,
    # we want to keep the 'type' part of the mode from before
    filesystemmetadata['inodetable'][thisinode]['mode'] = (filesystemmetadata['inodetable'][thisinode]['mode'] &~S_IRWXA) | mode

  finally:
    persist_metadata(METADATAFILENAME)
    filesystemmetadatalock.release()
  return 0

#### TRUNCATE  ####


def truncate_syscall(path, length):
  """
    http://linux.die.net/man/2/truncate
  """

  fd = open_syscall(path, O_RDWR, S_IRWXA)

  ret = ftruncate_syscall(fd, length)

  close_syscall(fd)

  return ret


#### FTRUNCATE ####


def ftruncate_syscall(fd, new_len):
  """
    http://linux.die.net/man/2/ftruncate
  """
  

  # check the fd
  if fd not in filedescriptortable and fd >= STARTINGFD:
    raise SyscallError("ftruncate_syscall","EBADF","Invalid old file descriptor.")

  if new_len < 0:
    raise SyscallError("ftruncate_syscall", "EINVAL", "Incorrect length passed.")

  # Acquire the fd lock...
  desc = filedescriptortable[fd]
  desc['lock'].acquire(True)

  try: 

        # we will need the file size in a moment, but also need to check the type
    try:
      inode = desc['inode']
    except KeyError:
      raise SyscallError("lseek_syscall","ESPIPE","This is a socket, not a file.")
    
    
    filesize = filesystemmetadata['inodetable'][inode]['size']

    if filesize < new_len:
      # we must pad with zeros
      blankbytecount = new_len - filesize 
      fileobjecttable[inode].writeat('\0'*blankbytecount,filesize)
      
    else:
      # we must cut
      to_save = fileobjecttable[inode].readat(new_len,0)
      fileobjecttable[inode].close()
      # remove the old file
      removefile(FILEDATAPREFIX+str(inode))
      # make a new blank one
      fileobjecttable[inode] = openfile(FILEDATAPREFIX+str(inode),True)

      fileobjecttable[inode].writeat(to_save, 0)

      
    filesystemmetadata['inodetable'][inode]['size'] = new_len
        
  finally:
    desc['lock'].release() 

  return 0

#### MKNOD ####

# for now, I am considering few assumptions:
# 1. It is only used for creating character special files.
# 2. I am not bothering about S_IRWXA in mode. (I need to fix this).
# 3. /dev/null    : (1, 3)
#    /dev/random  : (1, 8)
#    /dev/urandom : (1, 9)
#    The major and minor device number's should be passed in as a 2-tuple.

def mknod_syscall(path, mode, dev):
  """
    http://linux.die.net/man/2/mknod
  """
  if path == '':
    raise SyscallError("mknod_syscall","ENOENT","The file does not exist.")

  truepath = _get_absolute_path(path)

  # check if file already exists, if so raise an error.
  if truepath in fastinodelookuptable:
    raise SyscallError("mknod_syscall", "EEXIST", "file already exists.")

  # FIXME: mode should also accept user permissions(S_IRWXA)
  if not mode & S_FILETYPEFLAGS == mode: 
    raise SyscallError("mknod_syscall", "EINVAL", "mode requested creation\
      of something other than regular file, device special file, FIFO or socket")

  # FIXME: for now, lets just only create character special file 
  if not IS_CHR(mode):
    raise UnimplementedError("Only Character special files are supported.")

  # this has nothing to do with syscall, so I will raise UnimplementedError.
  if type(dev) is not tuple or len(dev) != 2:
    raise UnimplementedError("Third argument should be 2-tuple.")

  # Create a file, but don't open it. openning a chr_file should be done only using
  # open_syscall. S_IFCHR flag will ensure that the file is not opened.
  fd = open_syscall(path, mode | O_CREAT, S_IRWXA)

  # add the major and minor device no.'s, I did it here so that the code can be managed
  # properly, instead of putting everything in open_syscall.
  inode = filedescriptortable[fd]['inode']
  filesystemmetadata['inodetable'][inode]['rdev'] = dev
 
  # close the file descriptor... 
  close_syscall(fd)
  return 0


#### Helper Functions for Character Files.####
# currently supported devices are:
# 1. /dev/null
# 2. /dev/random
# 3. /dev/urandom

def _read_chr_file(inode, count):
  """
   helper function for reading data from chr_file's.
  """

  # check if it's a /dev/null. 
  if filesystemmetadata['inodetable'][inode]['rdev'] == (1, 3):
    return ''
  # /dev/random
  elif filesystemmetadata['inodetable'][inode]['rdev'] == (1, 8):
    return randombytes()[0:count]
  # /dev/urandom
  # FIXME: urandom is supposed to be non-blocking.
  elif filesystemmetadata['inodetable'][inode]['rdev'] == (1, 9):
    return randombytes()[0:count]
  else:
    raise UnimplementedError("Given device is not supported.")


def _write_chr_file(inode, data):
  """
   helper function for writing data to chr_file's.
  """

  # check if it's a /dev/null.
  if filesystemmetadata['inodetable'][inode]['rdev'] == (1, 3):
    return len(data)
  # /dev/random
  # There's no real /dev/random file, just vanish it into thin air.
  elif filesystemmetadata['inodetable'][inode]['rdev'] == (1, 8):
    return len(data)
  # /dev/urandom
  # There's no real /dev/random file, just vanish it into thin air.
  elif filesystemmetadata['inodetable'][inode]['rdev'] == (1, 9):
    return len(data)
  else:
    raise UnimplementedError("Given device is not supported.")


def _istat_helper_chr_file(inode):
  ret =  (5,          # st_dev, its always 5 for chr_file's.
          inode,                                 # inode
          filesystemmetadata['inodetable'][inode]['mode'],
          filesystemmetadata['inodetable'][inode]['linkcount'],
          filesystemmetadata['inodetable'][inode]['uid'],
          filesystemmetadata['inodetable'][inode]['gid'],
          filesystemmetadata['inodetable'][inode]['rdev'],
          filesystemmetadata['inodetable'][inode]['size'],
          0,                                     # st_blksize  ignored(?)
          0,                                     # st_blocks   ignored(?)
          filesystemmetadata['inodetable'][inode]['atime'],
          0,                                     # atime ns
          filesystemmetadata['inodetable'][inode]['mtime'],
          0,                                     # mtime ns
          filesystemmetadata['inodetable'][inode]['ctime'],
          0,                                     # ctime ns
        )
  return ret

#### USER/GROUP IDENTITIES ####


def getuid_syscall():
  """
    http://linux.die.net/man/2/getuid
  """
  # I will return 1000, since this is also used in stat
  return DEFAULT_UID

def geteuid_syscall():
  """
    http://linux.die.net/man/2/geteuid
  """
  # I will return 1000, since this is also used in stat
  return DEFAULT_UID

def getgid_syscall():
  """
    http://linux.die.net/man/2/getgid
  """
  # I will return 1000, since this is also used in stat
  return DEFAULT_GID

def getegid_syscall():
  """
    http://linux.die.net/man/2/getegid
  """
  # I will return 1000, since this is also used in stat
  return DEFAULT_GID


#### RESOURCE LIMITS  ####

# FIXME: These constants should be specified in a different file, 
# it at all additional support needs to be added.
NOFILE_CUR = 1024
NOFILE_MAX = 4*1024

STACK_CUR = 8192*1024
STACK_MAX = 2**32

def getrlimit_syscall(res_type):
  """
    http://linux.die.net/man/2/getrlimit

    NOTE: Second argument is deprecated. 
  """
  if res_type == RLIMIT_NOFILE:
    return (NOFILE_CUR, NOFILE_MAX)
  elif res_type == RLIMIT_STACK:
    return (STACK_CUR, STACK_MAX)
  else:
    raise UnimplementedError("The resource type is unimplemented.")

def setrlimit_syscall(res_type, limits):
  """
    http://linux.die.net/man/2/setrlimit
  """

  if res_type == RLIMIT_NOFILE:
    # always make sure that, current value is less than or equal to Max value.
    if NOFILE_CUR > NOFILE_MAX:
      raise SyscallException("setrlimit", "EPERM", "Should not exceed Max limit.")

    # FIXME: I should update the value which should be per program.
    # since, Lind doesn't need this right now, I will pass.
    return 0

  else:
    raise UnimplementedError("This resource type is unimplemented")

#### FLOCK SYSCALL  ####

def flock_syscall(fd, operation):
  """
    http://linux.die.net/man/2/flock
  """
  if fd not in filedescriptortable:
    raise SyscallError("flock_syscall", "EBADF" "Invalid file descriptor.")

  # if we are anything besides the allowed flags, fail
  if operation & ~(LOCK_SH|LOCK_EX|LOCK_NB|LOCK_UN):
    raise SyscallError("flock_syscall", "EINVAL", "operation is invalid.")

  if operation & LOCK_SH:
    raise UnimplementedError("Shared lock is not yet implemented.")

  # check whether its a blocking or non-blocking lock...
  if operation & LOCK_EX and operation & LOCK_NB: 
    if filedescriptortable[fd]['lock'].acquire(False): 
      return 0
    else: # raise an error, if there's another lock already holding this
      raise SyscallError("flock_syscall", "EWOULDBLOCK", "Operation would block.")
  elif operation & LOCK_EX:
    filedescriptortable[fd]['lock'].acquire(True)
    return 0

  if operation & LOCK_UN:
    filedescriptortable[fd]['lock'].release()
    return 0

def rename_syscall(old, new):
  """
  http://linux.die.net/man/2/rename
  TODO: this needs to be fixed up.
  """
  filesystemmetadatalock.acquire(True)
  try:
    true_old_path = _get_absolute_path(old)
    true_new_path = _get_absolute_path(new)

    if true_old_path not in fastinodelookuptable:
      raise SyscallError("rename_syscall", "ENOENT", "Old file does not exist")

    if true_new_path == '':
      raise SyscallError("rename_syscall", "ENOENT", "New file does not exist")

    trueparentpath_old = _get_absolute_parent_path(true_old_path)
    parentinode = fastinodelookuptable[trueparentpath_old]

    inode = fastinodelookuptable[true_old_path]

    newname = true_new_path.split('/')[-1]
    filesystemmetadata['inodetable'][parentinode]['filename_to_inode_dict'][newname] = inode

    fastinodelookuptable[true_new_path] = inode

    oldname = true_old_path.split('/')[-1]
    del filesystemmetadata['inodetable'][parentinode]['filename_to_inode_dict'][oldname]
    del fastinodelookuptable[true_old_path]

  finally:
    filesystemmetadatalock.release()
  return 0

#end include lind_fs_calls.py

#begin include lind_net_calls.py
"""
  Author: Justin Cappos
  Module: Network calls for Lind.   This is essentially POSIX written in
          Repy V2.   

  Start Date: January 14th, 2012

  My goal is to write a simple and relatively accurate implementation of POSIX
  in Repy V2.   This module contains most of the network calls.   A lind
  client can execute those calls and they will be mapped into my Repy V2 
  code where I will more or less faithfully execute them.   Since Repy V2
  does not support some of the socket options, I will fake (or ignore) these.
  There will also be a few minor parts of the implementation that might 
  need to interact with the file system portion of the API.   This will be 
  for things like getting file descriptors / socket descriptors.
  For Unix domain sockets, etc. we'll use loopback sockets.

  Much like the fs API, rather than do all of the struct packing, etc. here, I 
  will do it elsewhere.  This will allow me to test this in Python / Repy
  without unpacking / repacking.

"""

# Since Repy does not have a concept of descriptors or binding before 
# connecting, we will fake all of this.   I will determine the usable ports
# and then choose from them when it's unspecified.


# I'm not overly concerned about efficiency right now.   I'm more worried
# about correctness.   As a result, I'm not going to optimize anything yet.
#

# I'll keep a little metadata for each socket descriptor (in the file
# descriptor table).   It will look like this:
# {'domain': AF_INET, 'type': SOCK_STREAM, 'protocol': IPPROTO_TCP, 
#  'localip': '1.2.3.4', 'localport':12345, 'remoteip': '5.6.7.8', 
#  'remoteport':6789, 'socketobjectid':5, 'mode':S_IFSOCK | 0666, 'options':0,
#  'sndbuf':131070, 'rcvbuf': 262140, 'state':NOTCONNECTED}
#
# To make dup and dup2 work correctly, I'll keep a socketobjecttable instead
# of including them in the filedescriptortable...
#


# States for my own internal use:

NOTCONNECTED = 128
CONNECTED = 256
LISTEN = 512

# contains open file descriptor information... (keyed by fd)
# filedescriptortable = {}

# contains socket objects... (keyed by id)   Mostly done for dup / dup2
socketobjecttable = {}

connectedsocket = []

# This is raised to return an error...   It's the same as for the file 
# system calls
class SyscallError(Exception):
  """A system call had an error"""


# This is raised if part of a call is not implemented
class UnimplementedError(Exception):
  """A call was called with arguments that are not fully implemented"""


class CompositeTCPSocket:
  """This class can be used in place of a regular repy socket,
  when you need to bind and operate on two sockets at once.
  """

  def __init__(self, ip1, ip2, port):
    self.ip1 = ip1
    self.ip2 = ip2
    self.port = port
    self.c1 = listenforconnection(ip1, port)
    self.c2 = listenforconnection(ip2, port)
  
  def close(self):
    self.c1.close()
    self.c2.close()
    

  def getconnection(self):
    try:
     conn = self.c1.getconnection()
    except SocketWouldBlockError, e:
      conn = self.c2.getconnection()
    return conn


class CompositeUDPSocket:
  """This class can be used in place of a regular repy socket,
  when you need to bind and operate on two sockets at once.
  """

  def __init__(self, ip1, ip2, port):
    self.ip1 = ip1
    self.ip2 = ip2
    self.port = port
    self.c1 = listenformessage(ip1, port)
    self.c2 = listenformessage(ip2, port)
  
  def close(self):
    self.c1.close()
    self.c2.close()
    

  def getmessage(self):
    try:
      msg = self.c1.getmessage()
    except SocketWouldBlockError, e:
      msg = self.c2.getmessage()
    return msg



######################   Generic Helper functions   #########################


# a list of udp ports already used.   This is used to help us figure out a good
# available port
_usedudpportsset = set([])
# these are the ports we possibly could use...
_usableudpportsset = map(int, getresources()[0]['messport'].copy())

# the same for tcp...
_usedtcpportsset = set([])
_usabletcpportsset = map(int, getresources()[0]['connport'].copy())

# collect all the port list operations
_port_operations_debug = []

_port_list_lock = createlock()
# We need a helper that gets an available port...
# Get the last unused port and return it...
def _get_available_udp_port():
  for port in list(_usableudpportsset)[::-1]:
    if port not in _usedudpportsset:
      _port_operations_debug.append("suggesting UDP port " + str(port))
      return port
  
  # this is probably the closest syscall.   No buffer space available...
  raise SyscallError("_get_available_udp_port","ENOBUFS","No UDP port available")


# A verbatim copy of the above...   It's so simple, I guess it's okay to do so
def _get_available_tcp_port():
  for port in list(_usabletcpportsset)[::-1]:
    if port not in _usedtcpportsset:
      _port_operations_debug.append("suggesting TCP port " + str(port))
      return port

  
  # this is probably the closest syscall.   No buffer space available...
  raise SyscallError("_get_available_tcp_port","ENOBUFS","No TCP port available")


def _reserve_localport(port, protocol):
  global _usedtcpportsset
  global _usedudpportsset
  
  _port_list_lock.acquire(True)
  status = True
  _port_operations_debug.append("Reserving port " + str(port))
  if protocol == IPPROTO_UDP:
    if port == 0:
      port = _get_available_udp_port()
    if port not in _usedudpportsset:
      _usedudpportsset.add(port)
    else:
      status = False
  elif protocol == IPPROTO_TCP:
    if port == 0:
      port = _get_available_tcp_port()

    if port not in _usedtcpportsset:
      _usedtcpportsset.add(port)
    else:
      status = False
  _port_list_lock.release()
  if not status:
    warning("_reserve_local_port", _port_operations_debug)
  return (status, port)

# give a port and protocol, return the port to that portocol's pool
def _release_localport(port, protocol):
  global _usedtcpportsset
  global _usedudpportsset
  _port_list_lock.acquire(True)
  _port_operations_debug.append("Releasing port " + str(port))

  try:
    if protocol == IPPROTO_UDP:
      _usedudpportsset.remove(port)
    elif protocol == IPPROTO_TCP:
      _usedtcpportsset.remove(port)
  except KeyError:
    warning("Warning: freeing a port which is already free.  Port is", port)
    warning(_port_operations_debug)
  finally:
    _port_list_lock.release()

STARTINGSOCKOBJID = 0
MAXSOCKOBJID = 1024


# get an available socket object ID...
def _get_next_socketobjid():
  for sockobjid in range(STARTINGSOCKOBJID,MAXSOCKOBJID):
    if not sockobjid in socketobjecttable:
      return sockobjid

  raise SyscallError("_get_next_socketobjid","ENOBUFS","Insufficient buffer space is available to create a new socketobjid")

def _insert_into_socketobjecttable(socketobj):
  nextentry = _get_next_socketobjid()
  socketobjecttable[nextentry] = socketobj
  return nextentry



#################### The actual system calls...   #############################



##### SOCKET  #####


# A private helper that initializes a socket given validated arguments.
def _socket_initializer(domain,socktype,protocol, blocking=False, cloexec=False):
  # get a file descriptor
  flags = 0
  if blocking:
    flags = flags | O_NONBLOCK
  if cloexec:
    flags = flags | O_CLOEXEC
  newfd = get_next_fd()
  
  # NOTE: I'm intentionally omitting the 'inode' field.  This will make most
  # of the calls I did not change break.
  filedescriptortable[newfd] = {
      'mode':S_IFSOCK|0666, # set rw-rw-rw- perms too. This is what POSIX does.
      'domain':domain,
      'type':socktype,      # I'm using this name because it's used by POSIX.
      'protocol':protocol,
      # BUG: I may need to handle the global setting of options here...
      'options':0,          # start with all options off...
      'sndbuf':131070,      # buffersize (only used by getsockopt)
      'rcvbuf':262140,      # buffersize (only used by getsockopt)
      'state':NOTCONNECTED, # we start without any connection
      'lock':createlock(),
      'flags':flags,
      'errno':0
# We don't set the ip / ports or socketobjectid because they are unknown now.
  }
  return newfd
      


# int socket(int domain, int type, int protocol);
def socket_syscall(domain, socktype, protocol):
  """ 
    http://linux.die.net/man/2/socket
  """
  # this code is basically one huge case statement by domain

  # sock type is stored in last 3 or 4 bits, the rest is flags

  real_socktype = socktype & 7 # the type without the extra flags

  blocking = (socktype & SOCK_NONBLOCK) != 0 # check the non-blocking flag
  cloexec = (socktype & SOCK_CLOEXEC) != 0 # check the cloexec flag

  if blocking:
    warning("Warning: trying to create a non-blocking socket - we don't support that yet.")

  # okay, let's do different things depending on the domain...
  if domain == PF_INET:

    
    if real_socktype == SOCK_STREAM:
      # If is 0, set to default (IPPROTO_TCP)
      if protocol == 0:
        protocol = IPPROTO_TCP


      if protocol != IPPROTO_TCP:
        raise UnimplementedError("The only SOCK_STREAM implemented is TCP.  Unknown protocol:"+str(protocol))
      
      return _socket_initializer(domain,real_socktype,protocol, blocking, cloexec)


    # datagram!
    elif real_socktype == SOCK_DGRAM:
      # If is 0, set to default (IPPROTO_UDP)
      if protocol == 0:
        protocol = IPPROTO_UDP

      if protocol != IPPROTO_UDP:
        raise UnimplementedError("The only SOCK_DGRAM implemented is UDP.  Unknown protocol:"+str(protocol))
    
      return _socket_initializer(domain,real_socktype,protocol)
    else:
      raise UnimplementedError("Unimplemented sockettype: "+str(real_socktype))

  else:
    raise UnimplementedError("Unimplemented domain: "+str(domain))









##### BIND  #####


def bind_syscall(fd,localip,localport):
  """ 
    http://linux.die.net/man/2/bind
  """
  if fd not in filedescriptortable:
    raise SyscallError("bind_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("bind_syscall","ENOTSOCK","The descriptor is not a socket.")

  # Am I already bound?
  if 'localip' in filedescriptortable[fd]:
    raise SyscallError('bind_syscall','EINVAL',"The socket is already bound to an address")

  intent_to_rebind = False

  # Is someone else already bound to this address?
  for otherfd in filedescriptortable:
    # skip ours
    if fd == otherfd:
      continue

    # if not a socket, skip it...
    if 'domain' not in filedescriptortable[otherfd]:
      continue

    # if the protocol / domain/ type differ, ignore
    if filedescriptortable[otherfd]['domain'] != filedescriptortable[fd]['domain'] or filedescriptortable[otherfd]['type'] != filedescriptortable[fd]['type'] or filedescriptortable[otherfd]['protocol'] != filedescriptortable[fd]['protocol']:
      continue
    
    # if they are already bound to this address / port
    if 'localip' in filedescriptortable[otherfd] and filedescriptortable[otherfd]['localip'] == localip and filedescriptortable[otherfd]['localport'] == localport:
      # is SO_REUSEPORT in effect on both? I think everyone has to set 
      # SO_REUSEPORT (at least this is true on some OSes.   It's OS dependent)
      if filedescriptortable[fd]['options'] & filedescriptortable[otherfd]['options'] & SO_REUSEPORT == SO_REUSEPORT:
        # all is well, continue...
        intent_to_rebind = True
      else:
        raise SyscallError('bind_syscall','EADDRINUSE',"Another socket is already bound to this address")

  # BUG (?): hmm, how should I support multiple interfaces?   I could either 
  # force them to pick the result of getmyip here or could return a different 
  # error later....   I think I'll wait.
  if not intent_to_rebind:
    (ret, localport) = _reserve_localport(localport, filedescriptortable[fd]['protocol'])
    assert ret
  # If this is a UDP interface, then we should listen for udp datagrams
  # (there is no 'listen' so the time to start now)...
  if filedescriptortable[fd]['protocol'] == IPPROTO_UDP:
    if 'socketobjectid' in filedescriptortable[fd]:
      # BUG: I need to avoid leaking sockets, so I should close the previous...
      raise UnimplementedError("I should close the previous UDP listener when re-binding")
    if localip == '0.0.0.0':
      udpsockobj = CompositeUDPSocket('127.0.0.1', getmyip(), localport)
    else:
      udpsockobj = listenformessage(localip, localport)
    filedescriptortable[fd]['socketobjectid'] = _insert_into_socketobjecttable(udpsockobj) 

  # Done!   Let's set the information and bind later since Repy V2 doesn't 
  # support a separate call for binding...
  filedescriptortable[fd]['localip']=localip
  filedescriptortable[fd]['localport']=localport

  return 0






# int connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen);


##### CONNECT  #####


def connect_syscall(fd,remoteip,remoteport):
  """ 
    http://linux.die.net/man/2/connect
  """

  if fd not in filedescriptortable:
    raise SyscallError("connect_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("connect_syscall","ENOTSOCK","The descriptor is not a socket.")

  # includes CONNECTED and LISTEN
  if filedescriptortable[fd]['state'] != NOTCONNECTED:
    raise SyscallError("connect_syscall","EISCONN","The descriptor is already connected.")


  filedescriptortable[fd]['last_peek'] = ''


  # What I do depends on the protocol...
  # If UDP, set the items and return
  if filedescriptortable[fd]['protocol'] == IPPROTO_UDP:
    filedescriptortable[fd]['remoteip'] = remoteip
    filedescriptortable[fd]['remoteport'] = remoteport
    rc = 0
    try:
      a = filedescriptortable[fd]['localip']
    except KeyError:
      # if the local IP is not yet set, allocate it and bind to it.
      rc = bind_syscall(fd, getmyip(), _get_available_udp_port())
    return rc


  # it's TCP!
  elif filedescriptortable[fd]['protocol'] == IPPROTO_TCP:

    # Am I already bound?   If not, we'll need to get an ip / port
    if 'localip' not in filedescriptortable[fd]:
      localip = getmyip()
      
      localport = _get_available_tcp_port()
      while not _reserve_localport(localport, filedescriptortable[fd]['protocol'])[0]:
        localport = _get_available_tcp_port()
    else:
      localip = filedescriptortable[fd]['localip']
      localport = filedescriptortable[fd]['localport']



    try:
      # BUG: The timeout it configurable, right?
      newsockobj = openconnection(remoteip, remoteport, localip, localport, 10)

    except AddressBindingError, e:
      _release_localport(localport, filedescriptortable[fd]['protocol'])
      raise SyscallError('connect_syscall','ENETUNREACH','Network was unreachable because of inability to access local port / IP')

    except InternetConnectivityError, e:
      _release_localport(localport, filedescriptortable[fd]['protocol'])
      raise SyscallError('connect_syscall','ENETUNREACH','Network was unreachable because of inability to access local port / IP')

    except TimeoutError, e:
      _release_localport(localport, filedescriptortable[fd]['protocol'])
      raise SyscallError('connect_syscall','ETIMEDOUT','Connection timed out')

    except DuplicateTupleError, e:
      _release_localport(localport, filedescriptortable[fd]['protocol'])
      raise SyscallError('connect_syscall','EADDRINUSE','Network address in use')

    except ConnectionRefusedError, e:
      _release_localport(localport, filedescriptortable[fd]['protocol'])
      raise SyscallError('connect_syscall','ECONNREFUSED','Connection refused.')

    # fill in the file descriptor table...
    filedescriptortable[fd]['socketobjectid'] = _insert_into_socketobjecttable(newsockobj)
    filedescriptortable[fd]['localip'] = localip
    filedescriptortable[fd]['localport'] = localport
    filedescriptortable[fd]['remoteip'] = remoteip
    filedescriptortable[fd]['remoteport'] = remoteport
    filedescriptortable[fd]['state'] = CONNECTED
    filedescriptortable[fd]['errno'] = 0
    # change the state and return success
    return 0

  else:
    raise UnimplementedError("Unknown protocol in connect()")

    






# ssize_t sendto(int sockfd, const void *buf, size_t len, int flags, const struct sockaddr *dest_addr, socklen_t addrlen);

##### SENDTO  #####


def sendto_syscall(fd,message, remoteip,remoteport,flags):
  """ 
    http://linux.die.net/man/2/sendto
  """

  if fd not in filedescriptortable:
    raise SyscallError("sendto_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("sendto_syscall","ENOTSOCK","The descriptor is not a socket.")

  if flags != 0 and flags != MSG_NOSIGNAL:
    raise UnimplementedError("Flags are not understood by sendto!")

  # if there is no IP / port, call send instead.   It will assume the other
  # end is connected...
  if remoteip == '' and remoteport == 0:
    warning("Warning: sending back to send.")
    return send_syscall(fd,message, flags)

  if filedescriptortable[fd]['state'] == CONNECTED or filedescriptortable[fd]['state'] == LISTEN:
    raise SyscallError("sendto_syscall","EISCONN","The descriptor is connected.")


  if filedescriptortable[fd]['protocol'] == IPPROTO_TCP:
    raise SyscallError("sendto_syscall","EISCONN","The descriptor is connection-oriented.")
    
  # What I do depends on the protocol...
  # If UDP, set the items and return
  if filedescriptortable[fd]['protocol'] == IPPROTO_UDP:

    # If unspecified, use a new local port / the local ip
    if 'localip' not in filedescriptortable[fd]:
      localip = getmyip()
      localport = _get_available_udp_port()
    else:
      localip = filedescriptortable[fd]['localip']
      localport = filedescriptortable[fd]['localport']

    try:
      # BUG: The timeout it configurable, right?
      bytessent = sendmessage(remoteip, remoteport, message, localip, localport)
    except AddressBindingError, e:
      raise SyscallError('connect_syscall','ENETUNREACH','Network was unreachable because of inability to access local port / IP')
    except DuplicateTupleError, e:
      raise SyscallError('connect_syscall','EADDRINUSE','Network address in use')
 
    # fill in the file descriptor table...
    filedescriptortable[fd]['localip'] = localip
    filedescriptortable[fd]['localport'] = localport


    # return the characters sent!
    return bytessent

  else:
    raise UnimplementedError("Unknown protocol in sendto()")








# ssize_t send(int sockfd, const void *buf, size_t len, int flags);

##### SEND  #####


def send_syscall(fd, message, flags):
  """ 
    http://linux.die.net/man/2/send
  """
  if fd not in filedescriptortable:
    raise SyscallError("send_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("send_syscall","ENOTSOCK","The descriptor is not a socket.")

  if flags  != 0 and flags != MSG_NOSIGNAL: 
    raise UnimplementedError("Flagss are not understood by send!")

  # includes NOTCONNECTED and LISTEN
  if  filedescriptortable[fd]['protocol'] == IPPROTO_TCP and filedescriptortable[fd]['state'] != CONNECTED:
    raise SyscallError("send_syscall","ENOTCONN","The descriptor is not connected.")


  if filedescriptortable[fd]['protocol'] != IPPROTO_TCP and filedescriptortable[fd]['protocol'] != IPPROTO_UDP:
    raise SyscallError("send_syscall","EOPNOTSUPP","send not supported on this protocol.")
    
  # I'll check this anyways, because I later might have multiple protos 
  # supported
  if filedescriptortable[fd]['protocol'] == IPPROTO_TCP:

    # get the socket so I can send...
    sockobj = socketobjecttable[filedescriptortable[fd]['socketobjectid']]
    
    # retry until it does not block...
    while True:
      try:
        bytessent = sockobj.send(message)
      # sleep and retry
      except SocketWouldBlockError, e:
         sleep(RETRYWAITAMOUNT)
        
      except Exception, e:
        # I think this shouldn't happen.   A closed socket should go to
        # NOTCONNECTED state.   This is an internal error...
         raise 

      # return the characters sent!
      return bytessent
  elif filedescriptortable[fd]['protocol'] == IPPROTO_UDP:

    remoteip = filedescriptortable[fd]['remoteip']
    remoteport = filedescriptortable[fd]['remoteport']

    bytessent = sendto_syscall(fd, message, remoteip, remoteport, flags)
    return bytessent
  else:
    raise UnimplementedError("Unknown protocol in send()")

    

    





# ssize_t recvfrom(int sockfd, void *buf, size_t len, int flags, struct sockaddr *src_addr, socklen_t *addrlen);


##### RECVFROM  #####


# Wait this long between recv calls...
RETRYWAITAMOUNT = .00001


# Note that this call may be used by recv_syscall since they are so similar
def recvfrom_syscall(fd,length,flags):
  """ 
    http://linux.die.net/man/2/recvfrom
  """

  if fd not in filedescriptortable:
    raise SyscallError("recvfrom_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("recvfrom_syscall","ENOTSOCK","The descriptor is not a socket.")


  # What I do depends on the protocol...
  if filedescriptortable[fd]['protocol'] == IPPROTO_TCP:

    # includes NOTCONNECTED and LISTEN
    if filedescriptortable[fd]['state'] != CONNECTED:
      raise SyscallError("recvfrom_syscall","ENOTCONN","The descriptor is not connected."+str(filedescriptortable[fd]['state']))
    # is this a non-blocking recv OR a nonblocking socket?
    
    # I'm ready to recv, get the socket object...
    sockobj = socketobjecttable[filedescriptortable[fd]['socketobjectid']]
    peek = filedescriptortable[fd]['last_peek']
    remoteip = filedescriptortable[fd]['remoteip']
    remoteport = filedescriptortable[fd]['remoteport']
    # keep trying to get something until it works (or EOF)...
    while True:
      # if we have previous data from a peek, use that
      data = ''
      try:
        data = sockobj.recv(length)
      except SocketClosedRemote, e:
        data = ''
      except SocketClosedLocal, e:
        data = ''

      # sleep and retry!
      # If O_NONBLOCK was set, we should re-raise this here...
      except SocketWouldBlockError, e:
        if IS_NONBLOCKING(filedescriptortable[fd]['flags'], flags):
          raise e
        if peek == '':
          sleep(RETRYWAITAMOUNT)
          continue

      if peek == '':
        if (flags & MSG_PEEK) != 0:
          filedescriptortable[fd]['last_peek'] = data
        return remoteip, remoteport, data

      peek = peek + data
      if len(peek) <= length:
        ret_data = peek
        filedescriptortable[fd]['last_peek'] = ''
      else:
        ret_data = peek[:length]
        filedescriptortable[fd]['last_peek'] = peek[length:]
        # savd this data for later?
      if (flags & MSG_PEEK) != 0:
        # print "@@ peek next time"
        filedescriptortable[fd]['last_peek'] = peek
        
      return remoteip, remoteport, ret_data

  
   



  # If UDP, recieve a message and return...
  elif filedescriptortable[fd]['protocol'] == IPPROTO_UDP:
    # BUG / HELP!!!: Calling this with UDP and without binding does something I
    # don't really understand...   It seems to block but I don't know what is 
    # happening.   The socket isn't bound to a valid inode,etc from what I see.
    if 'localip' not in filedescriptortable[fd]:
      raise UnimplementedError("BUG / FIXME: Should bind before using UDP to recv / recvfrom")
    

    # get the udpsocket object...
    udpsockobj = socketobjecttable[filedescriptortable[fd]['socketobjectid']]



    # keep trying to get something until it works in most cases...
    while True:
      try:
        return udpsockobj.getmessage()

      # sleep and retry!
      # If O_NONBLOCK was set, we should re-raise this here...
      except SocketWouldBlockError, e:
        sleep(RETRYWAITAMOUNT)



  else:
    raise UnimplementedError("Unknown protocol in recvfrom()")









# ssize_t recv(int sockfd, void *buf, size_t len, int flags);

##### RECV  #####


def recv_syscall(fd, length, flags):
  """ 
    http://linux.die.net/man/2/recv
  """

  # TODO: Change read() to call recv when on a socket!!!

  remoteip, remoteport, message = recvfrom_syscall(fd, length, flags)

  # we don't need the remoteip or remoteport for this...
  return message

    






# int getsockname(int sockfd, struct sockaddr *addrsocklen_t *" addrlen);


##### GETSOCKNAME  #####


def getsockname_syscall(fd):
  """ 
    http://linux.die.net/man/2/getsockname
  """

  if fd not in filedescriptortable:
    raise SyscallError("getsockname_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("getsockname_syscall","ENOTSOCK","The descriptor is not a socket.")


  # if we know this, return it...
  if 'localip' in filedescriptortable[fd]:
    return filedescriptortable[fd]['localip'], filedescriptortable[fd]['localport']
  
  # otherwise, return '0.0.0.0', 0
  else:
    return '0.0.0.0',0
  

    


    




##### GETPEERNAME  #####


def getpeername_syscall(fd):
  """ 
    http://linux.die.net/man/2/getpeername
  """

  if fd not in filedescriptortable:
    raise SyscallError("getpeername_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("getpeername_syscall","ENOTSOCK","The descriptor is not a socket.")


  # if we don't know this, we should raise an exception
  if 'remoteip' not in filedescriptortable[fd]:
    raise SyscallError("getpeername_syscall","ENOTCONN","The descriptor is not connected.")

  # if we know this, return it...
  return filedescriptortable[fd]['remoteip'], filedescriptortable[fd]['remoteport']
  
  





# int listen(int sockfd, int backlog);



##### LISTEN  #####


# I ignore the backlog
def listen_syscall(fd,backlog):
  """ 
    http://linux.die.net/man/2/listen
  """

  if fd not in filedescriptortable:
    raise SyscallError("listen_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("listen_syscall","ENOTSOCK","The descriptor is not a socket.")

  # BUG: I need to check if someone else is already listening here...


  # If UDP, raise an exception
  if filedescriptortable[fd]['protocol'] == IPPROTO_UDP:
    raise SyscallError("listen_syscall","EOPNOTSUPP","This protocol does not support listening.")


  # it's TCP!
  elif filedescriptortable[fd]['protocol'] == IPPROTO_TCP:

    if filedescriptortable[fd]['state'] == LISTEN:
      # already done!
      return 0


    if 'localip' not in filedescriptortable[fd]:
      # the real POSIX impl picks a random port and listens on 0.0.0.0.   
      # I think this is unnecessary to implement.
      raise UnimplementedError("listen without bind")


    # If it's connected, this is still allowed, but I won't implement it...
    if filedescriptortable[fd]['state'] == CONNECTED:
      # BUG: I would need to close this (if the last) to handle this right...
      raise UnimplementedError("Listen should close the existing connected socket")


    # Is someone else already listening on this address?   This may happen
    # with SO_REUSEPORT
    for otherfd in filedescriptortable:
      # skip ours
      if fd == otherfd:
        continue

      # if not a socket, skip it...
      if 'domain' not in filedescriptortable[otherfd]:
        continue

      # if they are not listening, skip it...
      if filedescriptortable[otherfd]['state'] != LISTEN:
        continue

      # if the protocol / domain/ type differ, ignore
      if filedescriptortable[otherfd]['domain'] != filedescriptortable[fd]['domain'] or filedescriptortable[otherfd]['type'] != filedescriptortable[fd]['type'] or filedescriptortable[otherfd]['protocol'] != filedescriptortable[fd]['protocol']:
        continue

      # if they are already bound to this address / port
      if filedescriptortable[otherfd]['localip'] == filedescriptortable[fd]['localip'] and filedescriptortable[otherfd]['localport'] == filedescriptortable[fd]['localport']:
        raise SyscallError('bind_syscall','EADDRINUSE',"Another socket is already bound to this address")



    # otherwise, all is well.   Let's set it up!
    filedescriptortable[fd]['state'] = LISTEN


    # BUG: I'll let anything go through for now.   I'm fairly sure there will 
    # be issues I may need to handle later.
    # #CM: this is really annoying, so for now we bind to local ip
    if filedescriptortable[fd]['localip'] == "0.0.0.0":
      newsockobj = CompositeTCPSocket('127.0.0.1', getmyip(), filedescriptortable[fd]['localport'])
    else:
      newsockobj = listenforconnection(filedescriptortable[fd]['localip'], filedescriptortable[fd]['localport'])
    filedescriptortable[fd]['socketobjectid'] = _insert_into_socketobjecttable(newsockobj)

    # change the state and return success
    return 0

  else:
    raise UnimplementedError("Unknown protocol in listen()")

    








# int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen);




##### ACCEPT  #####


# returns ip, port, sockfd
def accept_syscall(fd, flags=0):
  """ 
    http://linux.die.net/man/2/accept
  """

  if fd not in filedescriptortable:
    raise SyscallError("accept_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("accept_syscall","ENOTSOCK","The descriptor is not a socket.")

  blocking = (flags & SOCK_NONBLOCK) != 0
  cloexec = (flags & SOCK_CLOEXEC) != 0

  # If UDP, raise an exception
  if filedescriptortable[fd]['protocol'] == IPPROTO_UDP:
    raise SyscallError("accept_syscall","EOPNOTSUPP","This protocol does not support listening.")

  # it's TCP!
  elif filedescriptortable[fd]['protocol'] == IPPROTO_TCP:

    # must be listening
    if filedescriptortable[fd]['state'] != LISTEN:
      raise SyscallError("accept_syscall","EINVAL","Must call listen before accept.")

    listeningsocket = socketobjecttable[filedescriptortable[fd]['socketobjectid']]
    
    # now we should loop (block) until we get an incoming connection
    while True:
      try:
        if connectedsocket != []:
          remoteip, remoteport, acceptedsocket = connectedsocket.pop(0)
        else:
          remoteip, remoteport, acceptedsocket = listeningsocket.getconnection() 

      # sleep and retry
      except SocketWouldBlockError, e:
        sleep(RETRYWAITAMOUNT)
      else:

        newfd = _socket_initializer(filedescriptortable[fd]['domain'],filedescriptortable[fd]['type'],filedescriptortable[fd]['protocol'], blocking, cloexec)
        filedescriptortable[newfd]['state'] = CONNECTED
        filedescriptortable[newfd]['localip'] = filedescriptortable[fd]['localip']
        newport = _get_available_tcp_port()
        (ret, newport) = _reserve_localport(newport, IPPROTO_TCP) 
        assert ret
        filedescriptortable[newfd]['localport'] = newport
        filedescriptortable[newfd]['remoteip'] = remoteip
        filedescriptortable[newfd]['remoteport'] = remoteport
        filedescriptortable[newfd]['socketobjectid'] = _insert_into_socketobjecttable(acceptedsocket)
        filedescriptortable[newfd]['last_peek'] = ''

        return remoteip, remoteport, newfd

  else:
    raise UnimplementedError("Unknown protocol in accept()")

    






# int getsockopt(int sockfd, int level, int optname, void *optval, socklen_t *optlen);


# I'm just going to set these binary options or return the previous setting.   
# In most cases, this will be while doing nothing.
STOREDSOCKETOPTIONS = [ SO_LINGER, # ignored
                        SO_KEEPALIVE, # ignored
                        SO_SNDLOWAT, # ignored
                        SO_RCVLOWAT, # ignored
                        SO_REUSEPORT, # used to allow duplicate binds...
                        SO_REUSEADDR,
                      ]


##### GETSOCKOPT  #####
def getsockopt_syscall(fd, level, optname):
  """ 
    http://linux.die.net/man/2/getsockopt
  """
  if fd not in filedescriptortable:
    raise SyscallError("getsockopt_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("getsockopt_syscall","ENOTSOCK","The descriptor is not a socket.")

  # This should really be SOL_SOCKET, however, we'll also handle a few others
  if level == SOL_UDP:
    raise UnimplementedError("UDP is not supported for getsockopt")

  # TCP...  Ignore most things...
  elif level == SOL_TCP:
    # do nothing
    
    raise UnimplementedError("TCP options not remembered by getsockopt")



  elif level == SOL_SOCKET:
    # this is where the work happens!!!

    if optname == SO_ACCEPTCONN:
      # indicate if we are accepting connections...
      if filedescriptortable[fd]['state'] == LISTEN:
        return 1
      else:
        return 0

    # if the option is a stored binary option, just return it...
    if optname in STOREDSOCKETOPTIONS:
      if (filedescriptortable[fd]['options'] & optname) == optname:
        return 1
      else:
        return 0

    # Okay, let's handle the (ignored) buffer settings...
    if optname == SO_SNDBUF:
      return filedescriptortable[fd]['sndbuf']

    if optname == SO_RCVBUF:
      return filedescriptortable[fd]['rcvbuf']

    # similarly, let's handle the SNDLOWAT and RCVLOWAT, etc.
    # BUG?: On Mac, this seems to be stored much like the buffer settings
    if optname == SO_SNDLOWAT or optname == SO_RCVLOWAT:
      return 1


    # return the type if asked...
    if optname == SO_TYPE:
      return filedescriptortable[fd]['type']

    # I guess this is always true!?!?   I certainly don't handle it.
    if optname == SO_OOBINLINE:
      return 1

    if optname == SO_ERROR:
      warning("Warning: returning no error because error reporting is not done correctly yet.")
      tmp = filedescriptortable[fd]['errno']
      filedescriptortable[fd]['errno'] = 0
      return tmp

    if optname == SO_REUSEADDR:
      return 0


    raise UnimplementedError("Unknown option in getsockopt(). option = %s"%(oct(optname)))

  else:
    raise UnimplementedError("Unknown level in getsockopt(). level = %s"%(oct(level)))








# int setsockopt(int sockfd, int level, int optname, const void *optval, socklen_t optlen);

##### SETSOCKOPT  #####
def setsockopt_syscall(fd, level, optname, optval):
  """ 
    http://linux.die.net/man/2/setsockopt
  """
  if fd not in filedescriptortable:
    raise SyscallError("setsockopt_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("setsockopt_syscall","ENOTSOCK","The descriptor is not a socket.")

  # This should really be SOL_SOCKET, however, we'll also handle a few others
  if level == SOL_UDP:
    raise UnimplementedError("UDP is not supported for setsockopt")

  # TCP...  Ignore most things...
  elif level == SOL_TCP:
    # do nothing
    if optname == TCP_NODELAY:
      return 0
 
    # otherwise return an error
    raise UnimplementedError("TCP options not remembered by setsockopt")


  elif level == SOL_SOCKET:
    # this is where the work happens!!!
    
    if optname == SO_ACCEPTCONN or optname == SO_TYPE or optname == SO_SNDLOWAT or optname == SO_RCVLOWAT:
      raise SyscallError("setsockopt_syscall","ENOPROTOOPT","Cannot set option using setsockopt. %d"%(optname))

    # if the option is a stored binary option, just return it...
    if optname in STOREDSOCKETOPTIONS:

      newoptions = filedescriptortable[fd]['options']
            
      # if the value is set, unset it...
      if (newoptions & optname) == optname:
        newoptions = newoptions - optname
        filedescriptortable[fd]['options'] = newoptions
        return 1

      # now let's set this if we were told to
      if optval:
        # this value should be 1!!!   Nothing else is allowed
        # assert(optval == 1), "Invalid optval"  This is not a valid assertion for SO_LINGER
        newoptions = newoptions | optname
      filedescriptortable[fd]['options'] = newoptions
      return 0
      

    # Okay, let's handle the (ignored) buffer settings...
    if optname == SO_SNDBUF:
      filedescriptortable[fd]['sndbuf'] = optval
      return 0

    if optname == SO_RCVBUF:
      filedescriptortable[fd]['rcvbuf'] = optval
      return 0

    # I guess this is always true!?!?   I certainly don't handle it.
    if optname == SO_OOBINLINE:
      # I can only handle this being true...
      assert(optval == 1), "Optval must be true"
      return 0

    raise UnimplementedError("Unknown option in setsockopt()" + str(optname))

  else:
    raise UnimplementedError("Unknown level in setsockopt()")





def _cleanup_socket(fd):
  if 'socketobjectid' in filedescriptortable[fd]:
    thesocket = socketobjecttable[filedescriptortable[fd]['socketobjectid']]
    thesocket.close()
    localport = filedescriptortable[fd]['localport']
    _release_localport(localport, filedescriptortable[fd]['protocol'])
    del socketobjecttable[filedescriptortable[fd]['socketobjectid']]
    del filedescriptortable[fd]['socketobjectid']
    
    filedescriptortable[fd]['state'] = NOTCONNECTED
    return 0




# int shutdown(int sockfd, int how);

##### SHUTDOWN  #####
def setshutdown_syscall(fd, how):
  """ 
    http://linux.die.net/man/2/shutdown
  """

  if fd not in filedescriptortable:
    raise SyscallError("shutdown_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("shutdown_syscall","ENOTSOCK","The descriptor is not a socket.")


  if how == SHUT_RD or how == SHUT_WR:

    raise UnimplementedError("Partial shutdown not implemented.")

  
  # let's shut this down...
  elif how == SHUT_RDWR:
    # BUG: need to check for duplicate entries (ala dup / dup2)
    _cleanup_socket(fd)
  else:
    # BUG: I'm not exactly clear as to how to handle this...
    
    raise SyscallError("shutdown_syscall","EINVAL","Shutdown given an invalid how")
  
  return 0







def _nonblock_peek_read(fd):
  """Do a read, but don't block or change the socket cursor. Called from select.

  @return False if socket will block, True if socket is ready for read. 
  """

  try:
    flags = O_NONBLOCK | MSG_PEEK
    data = recvfrom_syscall(fd, 1, flags)[2]
  except SocketWouldBlockError, e:
    return False
  except SyscallError, e:
    if e[1] == 'ENOTCONN':
      return False
    else:
      raise e
  except SocketClosedRemote, e:
    return False

  if len(data) == 1: #return True, if data is present...
    return True
  elif len(data) == 0: #return True, since it tells that remote socket is closed...
    return True
  else:
    return False
    # assert False, "Should never here here! data:%s"%(data)


def select_syscall(nfds, readfds, writefds, exceptfds, time):
  """ 
    http://linux.die.net/man/2/select
  """
  # for each fd in readfds,
  # if file, not socket, mark true
  # if socket
  #   perform read
  # if read fails with would block
  #   mark false
  # if read works, do it as a peek, so next time it won't block

  retval = 0
  
  # the bit vectors only support 1024 file descriptors, also lower FDs are not supported
  if nfds < STARTINGFD or nfds > MAX_FD:
    raise SyscallError("select_syscall","EINVAL","number of FDs is wrong: %s"%(str(nfds)))

  new_readfds = []
  new_writefds = []
  new_exceptfds = []

  start_time = getruntime()
  end_time = start_time + (time if time != None else -1)
  while True:

    # Reads
    for fd in readfds:
      if fd == 0:
        warning("Warning: Can't do select on stdin.")
        continue
      if fd not in filedescriptortable:
        raise SyscallError("select_syscall","EBADF","The file descriptor is invalid.")

      desc = filedescriptortable[fd]
      if not IS_SOCK_DESC(fd) and fd != 0:
        # files never block, so always say yes for them
        new_readfds.append(fd)
        retval += 1
      else:
        #Get an interim connection and save it, so when actual accept_syscall() is called
        #we pass the saved the connection.
        if filedescriptortable[fd]['state'] == LISTEN:
          listeningsocket = socketobjecttable[filedescriptortable[fd]['socketobjectid']]
          try:
            connectedsocket.append(listeningsocket.getconnection())
          except SocketWouldBlockError, e:
            pass
          else:
            new_readfds.append(fd)
            retval += 1
        #If the socket is not a listener, then it should be able to read data from socket.
        else:
        #sockets might block, lets check by doing a non-blocking peek read
          if filedescriptortable[fd]['protocol'] == IPPROTO_UDP or _nonblock_peek_read(fd):
            new_readfds.append(fd)
            retval += 1

    # Writes
    for fd in writefds:
      if fd not in filedescriptortable:
        raise SyscallError("select_syscall","EBADF","The file descriptor is invalid.")

      desc = filedescriptortable[fd]
      if not IS_SOCK_DESC(fd) or fd == 1 or fd == 2:
        # files never block, so always say yes for them
        new_writefds.append(fd)
        retval += 1
      else:
        #sockets d
        new_writefds.append(fd)
        retval += 1
        # assert not writefds, "Lind does not support socket writefds yet. FD=%d"%(fd)

    # Excepts
    assert not exceptfds, "Lind does not support exceptfds yet."

    # if the timeout is given as null or negative value, block forever until 
    # an event has occured, if timeout is provided as zero, return immediatly.
    # if positive time provided, wait until time expires and return
    
    if retval != 0 or time == 0 or (getruntime() >= end_time and time > 0):
      break
    else:
      sleep(RETRYWAITAMOUNT)
  leftover_time = time - (getruntime() - start_time)
  if leftover_time < 0:
     leftover_time = 0;
  return (retval, new_readfds, new_writefds, new_exceptfds, leftover_time)


def getifaddrs_syscall():
  """ 
    http://linux.die.net/man/2/getifaddrs

    Returns a list of the IP addresses of this machine.

    Fake most of the values.  I dont think an overly restrictive
    netmask is going to cause problems?
  """
  try:
    ip = getmyip()
  except:
    raise SyscallError("getifaddrs syscall","EADDRNOTAVAIL","Problem getting the" \
                       " local ip address.")
  broadcast = (ip.split('.')[0:3]) # the broadcast address is just x.y.z.255?
  broadcast = '.'.join(broadcast + ['255']) 
  return 0, [{'ifa_name':'eth0',
           'ifa_flags':0,
           'ifa_addr':ip,
           'ifa_netmask':'255.255.255.0', 
           'ifa_broadaddr':broadcast,
          },

          {'ifa_name':'lo0',
           'ifa_flags':0,
           'ifa_addr':'127.0.0.1',
           'ifa_netmask':'255.0.0.0',
           'ifa_broadaddr':'127.0.0.1',
          }
          ]


def poll_syscall(fds, timeout):
  """ 
    http://linux.die.net/man/2/poll

    returns a list of io status indicators for each of the
    file handles in fds

  """

  return_code = 0

  endtime = getruntime() + timeout
  while True:
    for structpoll in fds:
      fd = structpoll['fd']
      events = structpoll['events']
      read = events & POLLIN > 0 
      write = events & POLLOUT > 0 
      err = events & POLLERR > 0
      reads = []
      writes = []
      errors = []
      if read:
        reads.append(fd)
      if write:
        writes.append(fd)
      if err:
        errors.append(fd)

      #select with timeout set to zero, acts as a poll... 
      newfd = select_syscall(fd, reads, writes, errors, 0)
      
      # this FD found something
      mask = 0

      if newfd[0] > 0:
        mask = mask + (POLLIN if newfd[1] else 0)
        mask = mask + (POLLOUT if newfd[2] else 0) 
        mask = mask + (POLLERR if newfd[3] else 0)
        return_code += 1
      structpoll['revents'] = mask

    #if timeout is a negative value, then poll should run indefinitely
    #until there's an event in one of the descriptors.
    if (getruntime() > endtime and timeout >= 0) or return_code != 0:
      break
    else:
      sleep(RETRYWAITAMOUNT)

  return return_code, fds


#### SOCKETPAIR ####

SOCKETPAIR = "socketpair-socket"
SOCKETPAIR_LISTEN = "socketpair-listen"


def _helper_sockpair():
  """
    Helper function for socktpair() syscall. This is a thread that runs to
    establish a TCP connection and immediatly exists.
  """
  socketfd = mycontext[SOCKETPAIR]
  rc = listen_syscall(socketfd, 1)
  assert rc == 0, "Listen failed"
  rc = accept_syscall(mycontext[SOCKETPAIR]) 
  mycontext[SOCKETPAIR_LISTEN] = rc[2]

def socketpair_syscall(domain, socktype, protocol):
  """
    http://linux.die.net/man/2/socketpair
  """
  sv = []

  # Our implementation use TCP/UDP ports to mimic Unix domain sockets
  # so if we find that, swap to internet domain
  if domain == AF_UNIX:
    domain = AF_INET

  # create two sockets...
  sockfd = socket_syscall(domain, socktype, protocol)
  listfd = socket_syscall(domain, socktype, protocol)

  # TCP connection happens differently...
  if socktype == SOCK_STREAM:
    port1 = _get_available_tcp_port()
    rc = bind_syscall(sockfd, '127.0.0.1', port1)
    assert rc == 0, "Bind failed in socket pair"

    mycontext[SOCKETPAIR] = sockfd
    createthread(_helper_sockpair)
    sleep(.1)

    connect_syscall(listfd, '127.0.0.1', port1)
    sleep(.1)

    sv.append(mycontext[SOCKETPAIR_LISTEN])
    sv.append(listfd)

    # we need to close this socket...
    close_syscall(sockfd)

  # Make a connection oriented UDP.
  else:
    port1 = _get_available_udp_port()
    bind_syscall(sockfd, '127.0.0.1', port1)
    port2 = _get_available_udp_port()
    bind_syscall(listfd, '127.0.0.1', port2)

    connect_syscall(sockfd, '127.0.0.1', port2)
    connect_syscall(listfd, '127.0.0.1', port1)

    sv.append(sockfd)
    sv.append(listfd)

  return (0, sv)

#end include lind_net_calls.py

#begin include fs_open.repy
"""

Handlers for the open system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Open hadler pulls out the arguments, does any manditory checking
then calls the repy posix library open system call.  Then packs
the result back up.

"""


def lind_fs_open(args):
    """ open calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the flags, mode and file name in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the single int returned, or error.
    """

    flags = args[0]
    mode = args[1]
    file_name = args[2]
    try:
        result_fd = open_syscall(file_name, flags, mode)
    except SyscallError, e:
        message = "Could not find file: " + file_name + ":\n" + str(e[2]) + "\n"
        return ErrorResponseBuilder("fs_open", e[1], message)
    return SuccessResponseBuilder("fs_open", result_fd)


def lind_safe_fs_open(args):
    """ Safely wrap the open call.

    See dispatcher.repy for details.

    Check the mode flags and file for consistancy,
    then call the real open dispatcher.

    """
    #constants pulled from standard lib
    MASK = 3
    O_RDONLY = 00
    O_WRONLY = 01
    O_RDWR = 02

    flags = args[0]
    mode = args[1]
    file_name = args[2]

    assert isinstance(flags, int), "the flags should be an int"
    assert isinstance(mode, int), "the mode should be an int"
    assert isinstance(file_name, str), "filename should be a string"
    assert ((flags & MASK) == O_RDONLY or
            (flags & MASK) == O_WRONLY or
            (flags & MASK) == O_RDWR), \
            "the flags to not seem to be one of the expected. %o" % (flags)

    result = lind_fs_open(args)

    assert isinstance(result, Response), \
           "wrong return type %s" % (str(type(result)))
    if not result.is_error:
        assert (-1 <= result.return_code <= MAX_FD), "Must return a valid FD."

    return result

#end include fs_open.repy

#begin include fs_write.repy
def lind_fs_write(args):
    size = args[1]
    fd = args[0]
    buffer = args[2]
    if IS_SOCK_DESC(fd):
        try:
            result = send_syscall(fd, buffer, 0)
        except SyscallError, e:
            print "Write failed with", e
            return ErrorResponseBuilder("fs_write", e[1], e[2])
    else:
        try:
            result = write_syscall(fd, buffer)
        except SyscallError, e:
            return ErrorResponseBuilder("fs_write", e[1], e[2])
    return SuccessResponseBuilder("fs_write", result)


def lind_safe_fs_write(args):
    size = args[1]
    fd = args[0]
    buffer = args[2]

    assert size == len(buffer), "write size does not match buffer size"
    check_valid_fd_handle(fd)

    lind_fs_write(args)
    return SuccessResponseBuilder("fs_write", size)

#end include fs_write.repy

#begin include fs_fstatfs.repy

def lind_fs_fstatfs(args):
  """ Pull out arguments, and send off syscall. if it fails, handle exceptions then return a
  Response object.  """
  handle = args[0]
  try:
    result = pack_statfs_struct( fstatfs_syscall(handle) )
  except SyscallError, e:
    return ErrorResponseBuilder("fs_fstatfs", e[1], e[2])
  return SuccessResponseBuilder("fs_fstatfs", len(result), result)

def lind_safe_fs_fstatfs(args):
  """Check the validity of the arugments to the fstatfs syscall and what it returns"""
  handle = args[0]
  assert(len(args)==1), "fsstat should always have one argument"

  check_valid_fd_handle(handle)
  result = lind_fs_fstatfs(args)

  assert isinstance(result, Response), "wrong return type %s"%(str(type(result)))
  if not result.is_error:
    assert len(result.data)==88, "result must be exactly the size of struct statfs"
  return result

#end include fs_fstatfs.repy

#begin include fs_statfs.repy

def lind_fs_statfs(args):
  """ Pull out arguments, and send off syscall. if it fails, path exceptions then return a
  Response object.  """
  path = args[0]
  try:
    result = pack_statfs_struct( statfs_syscall(path) )
  except SyscallError, e:
    return ErrorResponseBuilder("fs_statfs", e[1], e[2])
  return SuccessResponseBuilder("fs_statfs",0, result)

def lind_safe_fs_statfs(args):
  """Check the validity of the arugments to the statfs syscall and what it returns"""
  path = args[0]
  assert(len(args)==1), "statfs should always have one argument"

  result = lind_fs_statfs(args)

  assert isinstance(result, Response), "wrong return type %s"%(str(type(result)))
  if not result.is_error:
    assert len(result.data)==88, "result must be exactly the size of struct statfs"
  return result

#end include fs_statfs.repy

#begin include comp.repy
def lind_comp_cia(args):
  """Component Interface Attach"""
  log("[info][syscall]Component Interface Attach Called with", args, "\n")

  # for now, just return the other compoent
  target = 0
  if mycontext[COMP] == 1:
    target = 2
  else:
    target = 1

  return SuccessResponseBuilder("comp_cia", target)


def lind_comp_call(args):
  """Component Call"""
  log("[info][syscall]Component Call Called with" + str(args),"\n")
  message = args[3]
  target_comp = args[0]
  comp(target_comp)[MBOX].append(message)
  return SuccessResponseBuilder("comp_call", 0)


def lind_comp_accept(args):
  """Component Accept"""
  log("[info][syscall]Component Accept Called with", args, "\n")
  try:
    mesg = curr_comp()[MBOX].pop(0)
  except IndexError:
    return SuccessResponseBuilder("comp_accpet", 0)
  return SuccessResponseBuilder("comp_accpet", len(mesg), mesg)


def lind_comp_recv(args):
  """Component Recv"""
  log("[info][syscall]Component Recv called with ", args, "\n")
  
  return SuccessResponseBuilder("comp_recv", 0)


#end include comp.repy

#begin include fs_access.repy
"""

Handlers for the access system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Access hadler pulls out the arguments, does any manditory checking
then calls the repy posix library access system call.  Then packs
the result back up.

"""


def lind_fs_access(args):
    """ access calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the flags, mode and file name in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the single int returned, or error.
    """

    mode = args[0]
    path = args[1]
    try:
        result = access_syscall(path, mode)
        print result
    except SyscallError, e:
        return ErrorResponseBuilder("fs_access", e[1], e[2])
    return SuccessResponseBuilder("fs_access", result)


def lind_safe_fs_access(args):
    """ Safely wrap the access call.

    See dispatcher.repy for details.

    Check the mode path for consistancy,
    then call the real access dispatcher.

    """

    mode = args[0]
    path = args[1]

    assert isinstance(mode, int), "the mode should be an int"

    assert isinstance(path, str), "filename should be a string"

    assert len(path) < PATH_MAX, " path is too long!"

    result = lind_fs_access(args)

    return result

#end include fs_access.repy

#begin include fs_read.repy
"""

Handlers for the read system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Read hadler pulls out the arguments, does any manditory checking
then calls the repy posix library read system call.  Then packs
the result back up.

"""


def lind_fs_read(args):
    """ read calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the handle and size in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the single int returned, or error.
    """

    handle = args[0]
    size = args[1]

    # so really this should be fixed
    # but right now big requests dont work!
    # so truncate the request
    if size > TX_BUF_MAX:
        size = TX_BUF_MAX

    if IS_SOCK_DESC(handle):
        try:
            if size == 0:
                size == TX_BUF_MAX
            result = recv_syscall(handle, size, 0)
        except SocketWouldBlockError as e:
            return ErrorResponseBuilder("fs_read", "EAGAIN", "Socket would block")
        except SyscallError, e:
            return ErrorResponseBuilder("fs_read", e[1], e[2])
    else:
        try:
            result = read_syscall(handle, size)
        except SyscallError, e:
            return ErrorResponseBuilder("fs_read", e[1], e[2])

    return SuccessResponseBuilder("fs_read", len(result), result)
        

def lind_safe_fs_read(args):
    """ Safely wrap the read call.

    See dispatcher.repy for details.

    Check the handle and size for consistancy,
    then call the real read dispatcher.

    """
    
    handle = args[0]
    size = args[1]
    check_valid_fd_handle(handle)
    assert isinstance(size, int)
    
    result = lind_fs_read(args)
    
    if result.is_error == False:
        assert(len(result.data) <= TX_BUF_MAX), "returning data larger than transmission buffer."
  
    return result

#end include fs_read.repy

#begin include fs_fstat.repy
"""

Handlers for the fxstat system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Fxstat hadler pulls out the arguments, does any manditory checking
then calls the repy posix library fxstat system call.  Then packs
the result back up.

"""


def lind_fs_fxstat(args):
    """ fxstat calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the handle and flags in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the struct returned, or error.
    """

    filedes = args[0]
    ver = args[1]

    if ver == 1:
        try:
            result = fstat_syscall(filedes)
        except SyscallError, e:
            return ErrorResponseBuilder("fs_fxstat", e[1], e[2])

        # This format is: dev,ino,mode,nlink,uid,gid,rdev,size,blksize,blocks
        # followed by 2Q for each timestamp.   The ns field is set to 0.
        packed = pack_stat_struct(result)
        
        return SuccessResponseBuilder("fs_fxstat", 0, packed)

    else:
        assert False, "not implemented"


def lind_safe_fs_fxstat(args):
    """ Safely wrap the fxstat call.

    See dispatcher.repy for details.

    Check the handle and flags and file for consistancy,
    then call the real fxstat dispatcher.

    """

    assert(len(args) == 2), "fsstat should always have two argument"
    handle = args[0]
    ver = args[1]

    assert(ver == 0 or ver == 1), "version has to be stat of fstat"

    check_valid_fd_handle(handle)

    result = lind_fs_fxstat(args)

    if result.is_error == False:
        assert len(result.data) == 112, \
               "result must be exactly the size of struct stat"
    return result

#end include fs_fstat.repy

#begin include fs_close.repy

def lind_fs_close(args):
  handle = args[0]
  try:
    result = close_syscall(handle)
  except SyscallError, e:
    return ErrorResponseBuilder("fs_close", e[1], e[2])

  return SuccessResponseBuilder("fs_close", result)

def lind_safe_fs_close(args):
  handle = args[0]
  check_valid_fd_handle(handle)

  return lind_fs_close(args)
  

#end include fs_close.repy

#begin include fs_lseek.repy
"""

Handlers for the lseek system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Lseek hadler pulls out the arguments, does any manditory checking
then calls the repy posix library lseek system call.  Then packs
the result back up.

"""


def lind_fs_lseek(args):
    """ lseek calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the paths in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the int returned, or error.
    """

    handle = args[1]
    whence = args[2]
    offset = args[0]

    try:
        result = lseek_syscall(handle, offset, whence)
    except SyscallError, e:
        return ErrorResponseBuilder("fs_lseek", e[1], e[2])

    reply = struct_pack("<q", result)
    return SuccessResponseBuilder("fs_lseek", 0, reply)


def lind_safe_fs_lseek(args):
    """ Safely wrap the lseek call.

    See dispatcher.repy for details.

    Check the paths for consistancy,
    then call the real lseek dispatcher.

    """

    offset = args[0]
    whence = args[2]
    handle = args[1]

    assert isinstance(offset, int) or isinstance(offset, long), "offset should be a int"
    assert isinstance(whence, int), "whence should be a int"


    assert(whence == SEEK_SET or \
           whence == SEEK_CUR or \
           whence == SEEK_END), ("invalid whence=%d" % (whence))

    check_valid_fd_handle(handle)

    result = lind_fs_lseek(args)

    if result.is_error == False:
        assert(len(result.data) == 8), "should return exactly and off_t"

    return result

#end include fs_lseek.repy

#begin include fs_mkdir.repy
#constants pulled from standard lib
MASK=3
O_RDONLY=00
O_WRONLY=01
O_RDWR=02
O_CREAT=0100
O_EXCL=0200
O_NOCTTY=0400
O_TRUNC=01000
O_APPEND=02000
O_NONBLOCK=04000
# O_NDELAY=O_NONBLOCK
O_SYNC=010000
# O_FSYNC=O_SYNC
O_ASYNC=020000

#ifdef __USE_GNU
# define O_DIRECT	 040000	/* Direct disk access.	*/
# define O_DIRECTORY	0200000	/* Must be a directory.	 */
# define O_NOFOLLOW	0400000	/* Do not follow links.	 */
# define O_NOATIME     01000000 /* Do not set atime.  */
# define O_CLOEXEC     02000000 /* Set close_on_exec.  */
#endif

#largest file descriptor
#TODO find out what the system limit is

def lind_fs_mkdir(args):
  mode = args[0]
  file_name = args[1]
  try:
    result_fd = mkdir_syscall(file_name, mode)
  except SyscallError,e:
    return ErrorResponseBuilder("fs_mkdir", e[1], e[2] )
  return SuccessResponseBuilder("fs_mkdir", result_fd)
  

def lind_safe_fs_mkdir(args):
    mode = args[0]
    file_name = args[1]

    assert isinstance(mode, int), "the mode should be an int"
    assert isinstance(file_name, str), "filename should be a string"

    result = lind_fs_mkdir(args)

    assert isinstance(result, Response), "wrong return type %s"%(str(type(result)))
    if not result.is_error:
      assert (result.return_code == 0), "Must return 0 on success." 
    else:
      pass
    return result


#end include fs_mkdir.repy

#begin include fs_rmdir.repy
def lind_fs_rmdir(args):
  file_name = args[0]
  try:
    result_fd = rmdir_syscall(file_name)
  except SyscallError,e:
    return ErrorResponseBuilder("fs_rmdir", e[1], e[2] )
  return SuccessResponseBuilder("fs_rmdir", result_fd)
  

def lind_safe_fs_rmdir(args):
    file_name = args[0]

    assert isinstance(file_name, str), "filename should be a string"

    result = lind_fs_rmdir(args)

    assert isinstance(result, Response), "wrong return type %s"%(str(type(result)))
    if not result.is_error:
      assert (result.return_code == 0), "Must return 0 on success." 
    else:
      print result.message
    return result


#end include fs_rmdir.repy

#begin include fs_chdir.repy
"""

Handlers for the chdir system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Chdir hadler pulls out the arguments, does any manditory checking
then calls the repy posix library chdir system call.  Then packs
the result back up.

"""


def lind_fs_chdir(args):
    """ chdir calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the flags, mode and file name in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the single int returned, or error.
    """


    file_name = args[0]
    try:
        result_fd = chdir_syscall(file_name)
    except SyscallError, e:
        return ErrorResponseBuilder("fs_chdir", e[1], e[2])
    return SuccessResponseBuilder("fs_chdir", result_fd)


def lind_safe_fs_chdir(args):
    """ Safely wrap the chdir call.

    See dispatcher.repy for details.

    Check the path for consistancy,
    then call the real chdir dispatcher.

    """

    file_name = args[0]

    assert isinstance(file_name, str), "filename should be a string"

    assert len(file_name) < PATH_MAX, " File name too long!"

    result = lind_fs_chdir(args)

    assert isinstance(result, Response), "wrong return type %s" % \
           (str(type(result)))
    if not result.is_error:
        assert (result.return_code == 0), \
               "Man page says access must return 0 on success."

    return result

#end include fs_chdir.repy

#begin include fs_link.repy
"""

Handlers for the link system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Link hadler pulls out the arguments, does any manditory checking
then calls the repy posix library link system call.  Then packs
the result back up.

"""


def lind_fs_link(args):
    """ link calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the paths in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the int returned, or error.
    """

    old_file_name = args[0]
    new_file_name = args[1]

    try:
        result = link_syscall(old_file_name, new_file_name)
    except SyscallError, e:
        return ErrorResponseBuilder("fs_link", e[1], e[2])
    return SuccessResponseBuilder("fs_link", result)


def lind_safe_fs_link(args):
    """ Safely wrap the link call.

    See dispatcher.repy for details.

    Check the paths for consistancy,
    then call the real link dispatcher.

    """

    file_name = args[0]

    assert isinstance(file_name, str), "filename should be a string"

    file_name = args[1]

    assert isinstance(file_name, str), "filename should be a string"

    result = lind_fs_link(args)

    assert isinstance(result, Response), "wrong return type %s" % \
           (str(type(result)))
    if not result.is_error:
        assert (result.return_code == 0), "Must return 0 on success."
    else:
        pass
    return result

#end include fs_link.repy

#begin include fs_unlink.repy
def lind_fs_unlink(args):
  file_name = args[0]
  try:
    result_fd = unlink_syscall(file_name)
  except SyscallError,e:
    return ErrorResponseBuilder("fs_unlink", e[1], e[2] )
  return SuccessResponseBuilder("fs_unlink", result_fd)
  

def lind_safe_fs_unlink(args):
    file_name = args[0]

    assert isinstance(file_name, str), "filename should be a string"

    result = lind_fs_unlink(args)

    assert isinstance(result, Response), "wrong return type %s"%(str(type(result)))
    if not result.is_error:
      assert (result.return_code == 0), "Must return 0 on success." 
    else:
      print result.message
    return result


#end include fs_unlink.repy

#begin include fs_xstat.repy
def lind_fs_xstat(args):
  type_code = args[0]
  path = args[1]
  try:
    if type_code == 1: 
      stat = stat_syscall(path)    
    elif type_code == 0:
      assert False,"unimplemented."
      py_result = xstat_syscall(handle, size)
    else:
      assert False, "this should never happen!  stat typecode must be 0 or 1"
  except SyscallError, e:
    return ErrorResponseBuilder("fs_xstat", e[1], e[2])

  result = pack_stat_struct(stat)
  return SuccessResponseBuilder("fs_xstat", 0, result)

def lind_safe_fs_xstat(args):
  type_code = args[0]
  path = args[1]
  assert (type_code == 0 or type_code == 1), "xstat type code must be stat or fstat"
    
  result = lind_fs_xstat(args)

  if result.is_error == False:
    assert len(result.data)==112, "result must be exactly the size of struct stat"

  return result

#end include fs_xstat.repy

#begin include fs_getdents.repy
"""

Handlers for the getdents system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Getdents hadler pulls out the arguments, does any manditory checking
then calls the repy posix library getdents system call.  Then packs
the result back up.

"""


def pack_dirent(dir_tuple, my_start):
    """
    Given the python tuple produced by the repy posix library, build the
    corrosponding C struct.  This is tricky because it has offsets from
    the previous entries.

    See man 2 getdnents for the struct format is wrong. See below
    format obtained by testing

    dir_tuple is the tuple with the info (inode, name)

    my_start is the distance from the start of the buffer that this
    entry starts at.
    """
    d_ino = dir_tuple[0]
    d_name = dir_tuple[1]

    # if the system call has the type typle too use it
    if len(dir_tuple) > 2:
        d_type = dir_tuple[2]
    else:
        d_type = DT_UNKNOWN  # TODO: set this
    
    # the format of the dirent struct is:
    #    unsigned long long d_ino
    #    signed long long offset
    #    unsigned short reclen
    #    char type
    #    char[] d_name

    format = "<Q<q<H<B" + str(len(d_name)) + "s<B"
    dirent_len = struct_calcsize(format)
    d_off = my_start + dirent_len
    dirent = struct_pack(format, d_ino, d_off, dirent_len, d_type, d_name, 0)
    return (d_off, dirent)


def lind_fs_getdents(args):
    """ getdents calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the file handle and max_bytes, return
    up to the dirents that fit in that space.

    """

    # the directory handle
    handle = args[0]

    #max bytes
    count = args[1]

    try:
        py_result = getdents_syscall(handle, count)
    except SyscallError, e:
        print "ERROR!", e
        return ErrorResponseBuilder("fs_getdents", e[1], e[2])

    if not py_result:
        return SuccessResponseBuilder("fs_getdents", 0)  # last entry is sent

    offset_cur = 0
    final_structs = []
    for ent in py_result:
        (off_delta, str_ent) = pack_dirent(ent, offset_cur)
        offset_cur = off_delta
        final_structs.append(str_ent)

    result = ''.join(final_structs)
    return SuccessResponseBuilder("fs_getdents", len(result), result)


def lind_safe_fs_getdents(args):
    """ Safely wrap the getdents call.

    See dispatcher.repy for details.

    Check the handle and count for consistancy,
    then call the real getdents dispatcher.

    """
    handle = args[0]
    count = args[1]

    check_valid_fd_handle(handle)
    assert isinstance(count, int)

    result = lind_fs_getdents(args)

    if result.is_error == False:
        assert(len(result.data) <= TX_BUF_MAX), \
            "returning data larger than transmission buffer."

        assert(len(result.data) <= count), \
               "not observing byte count parameter."
    return result

#end include fs_getdents.repy

#begin include fs_dup.repy
"""

Handlers for the dup system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Dup hadler pulls out the arguments, does any manditory checking
then calls the repy posix library dup system call.  Then packs
the result back up.

"""


def lind_fs_dup(args):
    """ dup calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the handle in a list,
    pull it out and make the actual syscall in the
    file system library.

    Pack the single int returned, or error.
    """

    handle = args[0]

    try:
        result = dup_syscall(handle)
    except SyscallError, e:
        return ErrorResponseBuilder("fs_dup", e[1], e[2])
    return SuccessResponseBuilder("fs_dup", result)


def lind_safe_fs_dup(args):
    """ Safely wrap the dup call.

    See dispatcher.repy for details.

    Check the file handle for consistancy, then call the real dup dispatcher.

    """

    handle = args[0]

    # Make sure this is not one of the reserved handles we use for libraries
    if handle <= STARTINGFD:
        log("Warning: low file handles are not supported in Lind dup.")

    return lind_fs_dup(args)

#end include fs_dup.repy

#begin include fs_dup2.repy
"""

Handlers for the dup2 system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Dup2 hadler pulls out the arguments, does any manditory checking
then calls the repy posix library dup2 system call.  Then packs
the result back up.

"""


def lind_fs_dup2(args):
    """ dup2 calls are dispatched to this function.

    See dispatcher.repy for details.

    Given two file handles in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the single int returned, or error.

    For now, low file handles are still used for nacl,
    so if we see them here, that is a problem, so
    print a warning.
    """
    handle = args[0]
    handle2 = args[1]

    if handle <= STARTINGFD or handle2 <= STARTINGFD:
        print "Warning: low file handles are not supported in Lind dup2(", \
              handle, handle2, ")"

    try:
        result = dup2_syscall(handle, handle2)
    except SyscallError, e:
        return ErrorResponseBuilder("fs_dup2", e[1], e[2])
    return SuccessResponseBuilder("fs_dup2", result)


def lind_safe_fs_dup2(args):
    """ Safely wrap the dup2 call.

    See dispatcher.repy for details.

    Check the two file handles for consistancy,
    then call the real dup2 dispatcher.

    """

    handle = args[0]
    handle2 = args[1]
    check_valid_fd_handle(handle)
    check_valid_fd_handle(handle2)

    return lind_fs_dup2(args)

#end include fs_dup2.repy

#begin include fs_fcntl.repy
"""

Handlers for the fcntl system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Fcntl hadler pulls out the arguments, does any manditory checking
then calls the repy posix library fcntl system call.  Then packs
the result back up.

"""


def lind_fs_fcntl(args):
    """ fcntl calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the handle and flag in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the single int returned, or error.
    """

    handle = args[0]
    cmd = args[1]

    if cmd == F_SETFD or cmd == F_SETFL or cmd == F_SETOWN:
        arg = args[2]
        try:
            result = fcntl_syscall(handle, cmd, arg)
        except SyscallError, e:
            return ErrorResponseBuilder("fs_fcntl", e[1], e[2])
    else:
        try:
            result = fcntl_syscall(handle, cmd)
        except SyscallError, e:
            return ErrorResponseBuilder("fs_fcntl", e[1], e[2])

    return SuccessResponseBuilder("fs_fcntl", result)


def lind_safe_fs_fcntl(args):
    """ Safely wrap the fcntl call.

    See dispatcher.repy for details.

    Check handle and flags check for consistancy,
    then call the real fcntl dispatcher.

    """

    handle = args[0]
    cmd = args[1]

    check_valid_fd_handle(handle)

    assert (cmd == F_GETFD or \
            cmd == F_SETFD or \
            cmd == F_GETFL or \
            cmd == F_SETFL or \
            cmd == F_GETOWN or \
            cmd == F_SETOWN), "Invalid or unsupported fcntl command"

    return lind_fs_fcntl(args)

#end include fs_fcntl.repy

#begin include sys_getpid.repy
"""

Handlers for the getepid system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Getepid hadler pulls out the arguments, does any manditory checking
then calls the repy posix library getepid system call.  Then packs
the result back up.

"""


def lind_sys_getpid(args):
    """ getepid calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the paths in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the int returned, or error.

    For now we dont want processes to know they are different than each other

    maybe this could be a lind specific counter in the future?

    what is the impact of doing this?

    @TODO(cmatthew) this should be moved with the other sys calls.
    """
    
    DEFAULT_PID = 1000
    result = struct_pack("<i", DEFAULT_PID)
    return SuccessResponseBuilder("sys_getpid", 0, result)


def lind_safe_sys_getpid(args):
    """ Safely wrap the getepid call.

    See dispatcher.repy for details.

    Check the paths for consistancy,
    then call the real getepid dispatcher.

    """

    result = lind_sys_getpid(args)
    assert len(result.data) == 4, "we return a sinlge int"

    return result

#end include sys_getpid.repy

#begin include net_socket.repy
"""

Handlers for the socket system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Socket hadler pulls out the arguments, does any manditory checking
then calls the repy posix library socket system call.  Then packs
the result back up.

"""


def lind_net_socket(args):
    """ socket calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the socket domain, socket type and protcol in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the single int returned, or error.
    """

    domain = args[0]
    _type = args[1]
    protocol = args[2]
    try:
        result = socket_syscall(domain, _type, protocol)
    except SyscallError, e:
        return ErrorResponseBuilder("net_socket", e[1], e[2])
    except UnimplementedError, e:
        return ErrorResponseBuilder("net_socket", "EACCES", "unimplemented!")

    return SuccessResponseBuilder("net_socket", result)


def lind_safe_net_socket(args):
    """ Safely wrap the socket call.

    See dispatcher.repy for details.

    Check the socket domain, socket type and protcol for consistancy,
    then call the real socket dispatcher.

    """
    domain = args[0]
    _type = args[1]
    protocol = args[2]

    assert (isinstance(domain, int)), "domain must be an int"
    if domain != PF_INET:
        log( "Warning: only internet domain supported right " \
              "now d=%d\n" % (domain))

    result = lind_net_socket(args)

    return result

#end include net_socket.repy

#begin include net_bind.repy
"""

Handlers for the bind system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Bind hadler pulls out the arguments, does any non-manditory checking
then calls the repy posix library bind system call.  Then packs
the result back up.

"""


def lind_net_bind(args):
    """ bind calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the flags, mode and file name in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the single int returned, or error.
    """
    fd = args[0]
    addr = args[2]
    family, port, ip, pad = parse_sockaddr_struct(addr)
    ipaddr = inet_ntoa(struct_pack("<I", ip))

    try:
        result = bind_syscall(fd, ipaddr, port)
    except SyscallError, e:
        return ErrorResponseBuilder("net_bind", e[1], e[2])

    return SuccessResponseBuilder("net_bind", result)


def lind_safe_net_bind(args):
    """ Safely wrap the bind call.

    See dispatcher.repy for details.

    Check the fd and IP consistancy,
    then call the real bind dispatcher.

    """
    fd = args[0]

    check_valid_fd_handle(fd)

    length = args[1]
    addr = args[2]
    assert(len(addr) == length)
    result = lind_net_bind(args)

    return result

#end include net_bind.repy

#begin include net_send.repy
"""

Handlers for the send system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Send hadler pulls out the arguments, does any manditory checking
then calls the repy posix library send system call.  Then packs
the result back up.

"""


def lind_net_send(args):
    """ send calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the descriptor, length, flags and a message in a buffer
    all in a list, pull them out and make the actual syscall in the
    file system library.

    Pack the single int returned, or error.
    """

    fd = args[0]
    length = args[1]
    flags = args[2]
    buf = args[3]
    try:
        result = send_syscall(fd, buf, flags)
    except SyscallError, e:
        return ErrorResponseBuilder("net_send", e[1], e[2])

    return SuccessResponseBuilder("net_send", result)


def lind_safe_net_send(args):
    """ Safely wrap the send call.

    See dispatcher.repy for details.

    Check the descriptor, length, flags and a message in
    a buffer for consistancy, then call the real send dispatcher.

    """

    fd = args[0]
    length = args[1]
    flags = args[2]
    buf = args[3]

    check_valid_fd_handle(fd)

    assert (0 <= length <= TX_BUF_MAX) and \
           (0 <= len(buf) <= TX_BUF_MAX), "Socket send message is too large."

    assert_warning(flags == 0, "no send flags are currently supported")

    result = lind_net_send(args)

    return result

#end include net_send.repy

#begin include net_sendto.repy

def lind_net_sendto(args):
  """
  """

  try:
    raise UnimplementedException("Need to finish this up")
    result = 0
    # result = sendto_syscall(path, mode)
    print result
  except SyscallError,e:
    return ErrorResponseBuilder("net_sendto", e[1], e[2])
  
  return SuccessResponseBuilder("net_sendto", result)


def lind_safe_net_sendto(args):
  """
  """
  result = lind_net_sendto(args)

  return result


#end include net_sendto.repy

#begin include net_recv.repy
"""

Handlers for the recv system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Recv hadler pulls out the arguments, does any manditory checking
then calls the repy posix library recv system call.  Then packs
the result back up.

"""


def lind_net_recv(args):
    """ recv calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the file descriptor length and flags in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the single int returned, or error.
    """

    sockfd = args[0]
    length = args[1]
    flags = args[2]

    try:
        result = recv_syscall(sockfd, length, flags)
    except SyscallError, e:
        return ErrorResponseBuilder("net_recv", e[1], e[2])

    return SuccessResponseBuilder("net_recv", len(result), result)


def lind_safe_net_recv(args):
    """ Safely wrap the recv call.

    See dispatcher.repy for details.

    Check the file descriptor length and flags for consistancy,
    then call the real recv dispatcher.

    """

    sockfd = args[0]
    length = args[1]
    flags = args[2]

    check_valid_fd_handle(sockfd)
    assert 0 < length <= TX_BUF_MAX, "Cannot receive more than transmit buffer"

    assert ((flags & MSG_PEEK) != 0) or flags == 0, "Currently no recv flags are supported."
    result = lind_net_recv(args)

    return result

#end include net_recv.repy

#begin include net_recvfrom.repy
"""

Handlers for the recvfrom system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Recvfrom hadler pulls out the arguments, does any manditory checking
then calls the repy posix library recvfrom system call.  Then packs
the result back up.

"""

def pack_multiarg(*args):
    for x in args:
        assert type(x) == str
        
    nargs = len(args)
    format = "<I" * nargs
    header = struct_pack(format, *map(len, args))
    return header + "".join(args)

def lind_net_recvfrom(args):
    """ recvfrom calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the file descriptor length and flags in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the single int returned, or error.
    """

    sockfd = args[0]
    length = args[1]
    flags = args[2]
    addrlen = args[3]

    # the lind - repy send buffer is 8k, so shrink this request if we have to.
    if length > TX_BUF_MAX:
        length = TX_BUF_MAX
    try:
        result = recvfrom_syscall(sockfd, length, flags)
    except SyscallError, e:
        return ErrorResponseBuilder("net_recvfrom", e[1], e[2])
    sockaddr = pack_struct_sockaddr(AF_INET, result[0], result[1])
    result_str = pack_multiarg(struct_pack("<I",128), result[2], sockaddr)

    return SuccessResponseBuilder("net_recvfrom", len(result[2]), result_str)


def lind_safe_net_recvfrom(args):
    """ Safely wrap the recvfrom call.

    See dispatcher.repy for details.

    Check the file descriptor length and flags for consistancy,
    then call the real recvfrom dispatcher.

    """

    sockfd = args[0]
    length = args[1]
    flags = args[2]

    check_valid_fd_handle(sockfd)
    # assert 0 <= length <= TX_BUF_MAX, "Cannot receive more than transmit buffer: %d"%(length)

    assert ((flags & MSG_PEEK) != 0) or flags == 0, "Currently no recvfrom flags are supported."
    result = lind_net_recvfrom(args)

    return result

#end include net_recvfrom.repy

#begin include net_connect.repy
"""

Handlers for the connect system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Connect hadler pulls out the arguments, does any manditory checking
then calls the repy posix library connect system call.  Then packs
the result back up.

"""


def parse_connect_struct(addr):
    """
    Pull out the information from a addr struct

    ARGS: addr is a buffer (string) containing the struct

    RETURNS: a tuple containing
    - integer family
    - integer port
    - string ip address in dot notation
    - the padding at the back of the struct, which should be null

    """
    format = '<h>H4s<Q'
    connect_struct = struct_unpack(format, addr[0:16])
    connect_struct[2] = inet_ntoa(connect_struct[2])
    return connect_struct


def lind_net_connect(args):
    """ connect calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the file descriptor, length, and address information
    struct in a list, pull them out and make the actual syscall in the
    file system library.

    Pack the single int returned, or error.
    """
    fd = args[0]
    length = args[1]
    family, port, ip, padding = parse_connect_struct(args[2])
    try:
        result = connect_syscall(fd, ip, port)
    except SyscallError, e:
        return ErrorResponseBuilder("net_connect", e[1], e[2])
    return SuccessResponseBuilder("net_connect", result)


def lind_safe_net_connect(args):
    """ Safely wrap the connect call.

    See dispatcher.repy for details.

    Check the file descriptor, length, and address information struct
    for consistancy then call the real connect dispatcher.

    """

    fd = args[0]
    length = args[1]
    addr = args[2]

    family, port, ip, padding = parse_connect_struct(args[2])

    assert padding == 0, "connect struct padding should be null"

    assert length == len(addr), "Passed length must match buffer size"

    assert_warning(family == 0, "Connect currently ignores family")

    assert 1 <= port <= 2 ** 16, "Port must be between 1, 65k"

    assert len("0.0.0.0") <= len(ip) <= len("255.255.255.255"), \
           "IP address too long or short"
    # map(lambda: x assert 0 <= int(x) <= 255, ip.split('.'))
    check_valid_fd_handle(fd)

    assert 0 < length <= TX_BUF_MAX, "Connect length must be with in limits"

    # assert len(addr) == (2 + 2 + 4 + 8), "Connect struct is incorrect size"

    result = lind_net_connect(args)

    return result

#end include net_connect.repy

#begin include net_listen.repy
"""

Handlers for the listen system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

"""


def lind_net_listen(args):
    """
    Pull out the arguments for listen and make real call.
    Args should have a fd, and a number of connections (n).
    """

    fd = args[0]
    n = args[1]
    try:
        result = listen_syscall(fd, n)
    except SyscallError, e:
        return ErrorResponseBuilder("net_listen", e[1], e[2])
    except ResourceForbiddenError, e:
        log(str(e))
        return ErrorResponseBuilder("net_listen", 'EPERM', str(e))
      
    return SuccessResponseBuilder("net_listen", result)


def lind_safe_net_listen(args):
    """ listen calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the file handle and max_connection, return
    0 if connection works, -1 otherwise.
    """

    fd = args[0]
    n = args[1]
    check_valid_fd_handle(fd)
    assert 0 <= n <= 128, "N is not valid! %d" % (n)

    result = lind_net_listen(args)

    return result

#end include net_listen.repy

#begin include net_accept.repy
"""

Handlers for the accpet system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Accept hadler pulls out the arguments, does any manditory checking
then calls the repy posix library accept system call.  Then packs
the result back up.

"""


def lind_net_accept(args):
    """ accept calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the flags, mode and file name in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the single int returned, or error.
    """
    fd = args[0]
    try:
        result = accept_syscall(fd, args[1])
    except SyscallError, e:
        return ErrorResponseBuilder("net_accept", e[1], e[2])
    return SuccessResponseBuilder("net_accept", result[2])


def lind_safe_net_accept(args):
    """ Safely wrap the accept call.

    See dispatcher.repy for details.

    Check the mode flags and file for consistancy,
    then call the real accept dispatcher.

    """
    fd = args[0]
    check_valid_fd_handle(fd)
    
    result = lind_net_accept(args)

    return result

#end include net_accept.repy

#begin include net_getpeername.repy

def lind_net_getpeername(args):
  """
  """

  try:
    print "doing getpeername syscall"
    result = 0
    # result = getpeername_syscall(path, mode)
    print result
  except SyscallError,e:
    return ErrorResponseBuilder("net_getpeername", e[1], e[2])
  
  return SuccessResponseBuilder("net_getpeername", result)


def lind_safe_net_getpeername(args):
  """
  """
  result = lind_net_getpeername(args)

  return result


#end include net_getpeername.repy

#begin include net_getsockname.repy

def lind_net_getsockname(args):
  """
  """

  try:
    print "doing getsockname syscall"
    result = 0
    # result = getsockname_syscall(path, mode)
    print result
  except SyscallError,e:
    return ErrorResponseBuilder("net_getsockname", e[1], e[2])
  
  return SuccessResponseBuilder("net_getsockname", result)


def lind_safe_net_getsockname(args):
  """
  """
  result = lind_net_getsockname(args)

  return result


#end include net_getsockname.repy

#begin include net_getsockopt.repy

def lind_net_getsockopt(args):
  """
  """

  try:
    result = 0
    fd = args[0]
    level = args[1]
    optname = args[2]
    optlen = args[3]

    result = getsockopt_syscall(fd, level, optname)
  except SyscallError,e:
    return ErrorResponseBuilder("net_getsockopt", e[1], e[2])

  data = struct_pack("<I", result)
  return SuccessResponseBuilder("net_getsockopt", 0, data)


def lind_safe_net_getsockopt(args):
  """
  """
  result = lind_net_getsockopt(args)

  return result


#end include net_getsockopt.repy

#begin include net_setsockopt.repy

def lind_net_setsockopt(args):
  """
  """
  fd = args[0]
  level = args[1]
  optname = args[2]
  optlen = args[3]
  opt = args[4]

  try:
    result = setsockopt_syscall(fd, level, optname, opt)
  except SyscallError,e:
    return ErrorResponseBuilder("net_setsockopt", e[1], e[2])
  except UnimplementedError, e:
    return ErrorResponseBuilder("net_setsockopt", 'EINVAL',  str(e))

  return SuccessResponseBuilder("net_setsockopt", result)


def lind_safe_net_setsockopt(args):
  """
  """

  result = lind_net_setsockopt(args)
  return result


#end include net_setsockopt.repy

#begin include net_shutdown.repy
"""

Handlers for the shutdown system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Shutdown hadler pulls out the arguments, does any manditory checking
then calls the repy posix library shutdown system call.  Then packs
the result back up.

"""


def lind_net_shutdown(args):
    """ shutdown calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the flags, mode and file name in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the single int returned, or error.
    """
    sockfd = args[0]
    how = args[1]
    try:
        result = setshutdown_syscall(sockfd, how)

    except SyscallError, e:
        return ErrorResponseBuilder("net_shutdown", e[1], e[2])

    return SuccessResponseBuilder("net_shutdown", result)


def lind_safe_net_shutdown(args):
    """ Safely wrap the shutdown call.

    See dispatcher.repy for details.

    Check the mode flags and file for consistancy,
    then call the real shutdown dispatcher.

    """

    sockfd = args[0]
    how = args[1]

    check_valid_fd_handle(sockfd)
    assert(how == SHUT_RD or how == SHUT_WR or how == SHUT_RDWR),\
               "How must be one of SHUT_RD, SHUT_WR, or SHUT_RDWR"
    result = lind_net_shutdown(args)

    return result

#end include net_shutdown.repy

#begin include net_select.repy
"""

Handlers for the select system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

"""

# how large is our bit vector? 128 bytes
WIDTH_IN_BYTES = 128

# How many bits (and file descriptors can we have then?) 8 per bytes
MAX_FDS = WIDTH_IN_BYTES * 8


def bit_get(n, array):
    """Given a bitlist in ARRAY, get the bit in position N.

    @param n the bit you want to set
    @param array a bit_list, which is an list of character ordinals
    @return True if the bit is set, False otherwise

    """
    byte = array[n / 8]
    return ((byte >> (n % 8)) & 1) == 1


def bit_set(n, array):
    """Set (set to 1) the nth bit of this vector"""
    mask = 1 << (n % 8)
    byte = array[n / 8]
    byte = mask | byte
    array[n / 8] = byte
    return array


def bit_clear(n, array):
    """clear (set to 0) the nth bit in this vector"""
    mask = ~(1 << (n % 8))
    byte = array[n / 8]
    byte = mask & byte
    array[n / 8] = byte
    return array


def bit_string_to_bitlist(strarray):
    """Convert a string into a list of ordinals to do bit operations on."""
    return map(ord, strarray)


def bit_bitlist_to_str(ordlist):
    """Given a list of ordinals, convert them back to a string"""
    return ''.join(map(chr, ordlist))


def bit_test_bitops():
    """Check to make sure that the bitvector operations all work"""

    # make a blank string
    print "Info: Running bitops tests... ",
    test_str = '\x00' * 128
    bits = bit_string_to_bitlist(test_str)
    for i in xrange(0, MAX_FDS):
        bit_set(i, bits)
    for i in xrange(0, MAX_FDS):
        assert bit_get(i, bits), "Bits were not set correclty"
    for i in xrange(0, MAX_FDS):
        bit_clear(i, bits)
    for i in xrange(0, MAX_FDS):
        assert bit_get(i, bits) == False, "Bits were not cleared correclty"
    for i in xrange(0, MAX_FDS, 2):
        bit_set(i, bits)
    for i in xrange(0, MAX_FDS, 2):
        assert bit_get(i, bits), "Stride bits were not set correclty"
    for i in xrange(1, MAX_FDS, 2):
        assert bit_get(i, bits) == False, "stride bits were not set correclty"
    for i in xrange(0, MAX_FDS, 2):
        bit_clear(i, bits)
    assert test_str == bit_bitlist_to_str(bits)
    print "passed."


def get_fds(bit_array, max_fd):
    """Given a bitarray from select, pull out the file handles to monitor.
    Ignore parts of the vector we know are not going to be in use.

    @param bit_array a bit array from the select call.  The nth bit,
    represents the nth file handle

    @param max only check up to max bits (exclusive).

    @return a list of integers, which were the positions which bits were set.
    """
    fds = []
    how_far = min([max_fd, MAX_FDS, len(bit_array)])
    for i in xrange(0, how_far):
        if bit_get(i, bit_array):
            fds.append(i)
    return fds


def set_fds(fd_list, max_fd):
    """Given a file descriptor list from select, tick the handles which were
    found in the bitlist, and return.
    Ignore parts of the vector we know are not going to be in use.

    @param fd_list a list from the select call.  The nth bit,
    represents the nth file handle

    @param max only check up to max bits (exclusive).

    @return a ordinal array, which were the positions which bits were set.
    """
    ordinals = [ord('\x00')] * 128

    for fd in fd_list:
        bit_set(fd, ordinals)

    return ordinals


def lind_net_select(args):
    """
    Pull out the arguments for select and make real call.
    Args should have a nfds, bitvectors for read write and except, and a time.
    """

    nfds = args[0]

    readfds = args[1]
    writefds = args[2]
    exceptfds = args[3]
    timeval = args[4]

    if timeval == None:
        time = -1
    else:
        time, sec, usec = parse_timeval(args[4])

    readfds = [] if readfds == None else get_fds(bit_string_to_bitlist(readfds), nfds)
    writefds = [] if writefds == None else get_fds(bit_string_to_bitlist(writefds), nfds)
    exceptfds = [] if exceptfds == None else get_fds(bit_string_to_bitlist(exceptfds), nfds)
    
    try:
        rc, readfds, writefds, exceptfds, usedtime = select_syscall(nfds, readfds, writefds, exceptfds, time)
    except SyscallError, e:
        return ErrorResponseBuilder("net_select", e[1], e[2])

    used_sec = long((usedtime))
    used_usec = long((usedtime - used_sec) * MICROSEC_PER_SEC)
    used_timeval = pack_struct_timeval(used_sec, used_usec)
    readfds = bit_bitlist_to_str(set_fds(readfds, nfds))
    writefds = bit_bitlist_to_str(set_fds(writefds, nfds))
    exceptfds = bit_bitlist_to_str(set_fds(exceptfds, nfds))

    return SuccessResponseBuilder("net_select", rc, ''.join((used_timeval, readfds, writefds, exceptfds)))


def lind_safe_net_select(args):
    """ select calls are dispatched to this function.

    See dispatcher.repy for details.

    safely call the lind select function and return the results.
    """

    bit_test_bitops()
    result = lind_net_select(args)

    return result

#end include net_select.repy

#begin include net_getifaddrs.repy
"""

Handlers for the getifaddrs ioctl call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

"""

FLAGS='ifa_flags'
ADDR='ifa_addr'
NETMASK='ifa_netmask'
BROADCAST='ifa_broadaddr'
NAME='ifa_name'

def _type_to_name(element):
    _type = type(element)
    if _type == type(1):
        if element < 0:
            return "<i"
        else:
            return "<I"
    if _type == type(1l):
        if element < 0:
            return "<q"
        else:
            return "<Q"
    # if _type == type(chr(0)):
    #     return "<B"

    if _type == type(""):
        return str(len(element))+'s'
    
    print "tpye", _type, "not found for", element
    raise Exception("No format for type")
        

def build_struct_format(*args):
    """Given a list with python elements, make the struct package format string for that list"""
    return ''.join(map(_type_to_name, args))


def build_ifaddrs_struct(iplist):
    """Build the ifaddrs struct.  Since it is a linked list with pointers, we
    will not build the real one, but a packed format which glibc can unpack
    to a usable version.

    The format stuct is:
    struct {
       int flags
       int flags2
       int addr - this is an IPv4 address in network order byte binary format
       int addr2
       int netmask - in network byte order binary format
       int netmask2
       int broadcast
       int broadcast2
       char * name
       char * name2
    }
    """
    elements = [iplist[0][FLAGS],
                iplist[1][FLAGS],
                inet_aton(iplist[0][ADDR]),
                inet_aton(iplist[1][ADDR]),
                inet_aton(iplist[0][NETMASK]),
                inet_aton(iplist[1][NETMASK]),
                inet_aton(iplist[0][BROADCAST]),
                inet_aton(iplist[1][BROADCAST]),
                iplist[0][NAME]+chr(0),   # null terminate the string
                iplist[1][NAME] + chr(0),
                ]
    return struct_pack(build_struct_format(*elements), *elements)
    


def lind_net_getifaddrs(args):
    """
    Pull out the arguments for getifaddrs and make real call.
    """
    size = args[0]
    try:
        rc, iplist = getifaddrs_syscall()
    except SyscallError, e:
        return ErrorResponseBuilder("net_getifaddrs", e[1], e[2])

    packed = build_ifaddrs_struct(iplist)
    assert len(packed) <= size, "getifaddrs data buffer is too small %d into %d"%( len(packed), size)
    return SuccessResponseBuilder("net_getifaddrs", rc, packed)


def lind_safe_net_getifaddrs(args):
    """ getifaddrs calls are dispatched to this function.

    See dispatcher.repy for details.

    safely call the lind getifaddrs function and return the results.
    """

    result = lind_net_getifaddrs(args)

    return result

#end include net_getifaddrs.repy

#begin include net_poll.repy
"""

Handlers for the poll system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Poll hadler pulls out the arguments, does any manditory checking
then calls the repy posix library poll system call.  Then packs
the result back up.

"""


def lind_net_poll(args):
    """ poll calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the file descriptor length and flags in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the single int returned, or error.
    """

    nfds = args[0]
    timeout = args[1]
    fds_str = args[2]
    fds = parse_struct_pollfds(fds_str, nfds)
    result = 0
    try:
        result = poll_syscall(fds, timeout)
    except SyscallError, e:
        return ErrorResponseBuilder("net_poll", e[1], e[2])

    data = pack_struct_pollfds(result[1], nfds)

    return SuccessResponseBuilder("net_poll", result[0], data)


def lind_safe_net_poll(args):
    """ Safely wrap the poll call.

    See dispatcher.repy for details.

    Check the file descriptor length and flags for consistancy,
    then call the real poll dispatcher.

    """

    result = lind_net_poll(args)

    return result

#end include net_poll.repy

#begin include net_socketpair.repy
"""

Handlers for the socketpair system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Socketpair hadler pulls out the arguments, does any manditory checking
then calls the repy posix library socketpair system call.  Then packs
the result back up.

"""


def lind_net_socketpair(args):
    """ socketpair calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the socketpair domain, socketpair type and protcol in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the single int returned, or error.
    """
    domain = args[0]
    _type = args[1]
    protocol = args[2]
    try:
        (result, sv) = socketpair_syscall(domain, _type, protocol)
    except SyscallError, e:
        print str(e)
        return ErrorResponseBuilder("net_socketpair", e[1], e[2])
    except UnimplementedError, e:
        print str(e)
        return ErrorResponseBuilder("net_socketpair", "EACCES", "unimplemented!")

    assert len(sv) == 2, "Socket pair must have two elements"
    assert type(sv[1]) == int and type(sv[0]) == int, "Socketpair results must be socket handles."
    
    data = struct_pack("<i<i", sv[0], sv[1])

    return SuccessResponseBuilder("net_socketpair", result, data)


def lind_safe_net_socketpair(args):
    """ Safely wrap the socketpair call.

    See dispatcher.repy for details.

    Check the socketpair domain, socketpair type and protcol for consistancy,
    then call the real socketpair dispatcher.

    """
    domain = args[0]
    _type = args[1]
    protocol = args[2]

    assert (isinstance(domain, int)), "domain must be an int"
    if domain != PF_INET:
        log( "Warning: only internet domain supported right " \
              "now d=%d" % (domain))

    if not (_type == SOCK_DGRAM or _type == SOCK_STREAM):
        log ("Warning: only only datagram and stream socketpairs " \
              "supported right now")

    result = lind_net_socketpair(args)

    

    return result

#end include net_socketpair.repy

#begin include sys_getuid.repy
"""

Handlers for the geteuid system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Geteuid hadler pulls out the arguments, does any manditory checking
then calls the repy posix library geteuid system call.  Then packs
the result back up.

"""


def lind_sys_getuid(args):
    """ geteuid calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the paths in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the int returned, or error.
    """

    try:
        result = getuid_syscall()
    except SyscallError, e:
        return ErrorResponseBuilder("sys_getuid", e[1], e[2])
    except UnimplementedError, e:
        return ErrorResponseBuilder("sys_getuid", 'EINVAL', str(e))

    data = struct_pack("<i", result)
    return SuccessResponseBuilder("sys_getuid", len(data), data)


def lind_safe_sys_getuid(args):
    """ Safely wrap the geteuid call.

    See dispatcher.repy for details.

    Check the paths for consistancy,
    then call the real geteuid dispatcher.

    """

    result = lind_sys_getuid(args)
    assert len(result.data) == 4, "we return a sinlge int. got %d"%(len(result.data))

    return result

#end include sys_getuid.repy

#begin include sys_geteuid.repy
"""

Handlers for the geteuid system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Geteuid hadler pulls out the arguments, does any manditory checking
then calls the repy posix library geteuid system call.  Then packs
the result back up.

"""


def lind_sys_geteuid(args):
    """ geteuid calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the paths in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the int returned, or error.
    """

    try:
        result = geteuid_syscall()
    except SyscallError, e:
        return ErrorResponseBuilder("sys_geteuid", e[1], e[2])
    except UnimplementedError, e:
        return ErrorResponseBuilder("sys_geteuid", 'EINVAL', str(e))

    data = struct_pack("<i", result)
    return SuccessResponseBuilder("sys_geteuid", len(data), data)


def lind_safe_sys_geteuid(args):
    """ Safely wrap the geteuid call.

    See dispatcher.repy for details.

    Check the paths for consistancy,
    then call the real geteuid dispatcher.

    """

    result = lind_sys_geteuid(args)
    assert len(result.data) == 4, "we return a sinlge int"

    return result

#end include sys_geteuid.repy

#begin include sys_getgid.repy
"""

Handlers for the getgid system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Getgid hadler pulls out the arguments, does any manditory checking
then calls the repy posix library getgid system call.  Then packs
the result back up.

"""


def lind_sys_getgid(args):
    """ getgid calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the paths in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the int returned, or error.
    """
    try:
        result = getgid_syscall()
    except SyscallError, e:
        return ErrorResponseBuilder("sys_getgid", e[1], e[2])
    except UnimplementedError, e:
        return ErrorResponseBuilder("sys_getgid", 'EINVAL', str(e))

    data = struct_pack("<i", result)
    return SuccessResponseBuilder("sys_getgid", len(data), data)

def lind_safe_sys_getgid(args):
    """ Safely wrap the getgid call.

    See dispatcher.repy for details.

    Check the paths for consistancy,
    then call the real getgid dispatcher.

    """
    
    result = lind_sys_getgid(args)
    assert len(result.data) == 4, "we return a sinlge int"

    return result

#end include sys_getgid.repy

#begin include sys_getegid.repy
"""

Handlers for the getegid system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Getegid hadler pulls out the arguments, does any manditory checking
then calls the repy posix library getegid system call.  Then packs
the result back up.

"""


def lind_sys_getegid(args):
    """ getegid calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the paths in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the int returned, or error.
    """


    try:
        result = getegid_syscall()
    except SyscallError, e:
        return ErrorResponseBuilder("sys_getegid", e[1], e[2])
    except UnimplementedError, e:
        return ErrorResponseBuilder("sys_getegid", 'EINVAL', str(e))

    return SuccessResponseBuilder("sys_getegid", result)


def lind_safe_sys_getegid(args):
    """ Safely wrap the getegid call.

    See dispatcher.repy for details.

    Check the paths for consistancy,
    then call the real getegid dispatcher.

    """

    result = lind_sys_getegid(args)
    assert len(result.data) == 4, "we return a sinlge int"

    return result

#end include sys_getegid.repy

#begin include fs_flock.repy
"""

Handlers for the flock system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Flock hadler pulls out the arguments, does any manditory checking
then calls the repy posix library flock system call.  Then packs
the result back up.

"""


def lind_fs_flock(args):
    """ flock calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the flags, mode and file name in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the single int returned, or error.
    """

    fd = args[0]
    operation = args[1]

    try:
        result = flock_syscall(fd, operation)
    except SyscallError, e:
        return ErrorResponseBuilder("fs_flock", e[1], e[2])

    return SuccessResponseBuilder("fs_flock", result)


def lind_safe_fs_flock(args):
    """ Safely wrap the flock call.

    See dispatcher.repy for details.

    Check the mode flags and file for consistancy,
    then call the real flock dispatcher.

    """

    fd = args[0]
    operation = args[1]

    # if we are anything besides the allowed flags, fail
    assert operation & (LOCK_SH | LOCK_EX | LOCK_NB | LOCK_UN), \
           "At least one operation must be passed"
    check_valid_fd_handle(fd)
    assert isinstance(fd, int), "the fd should be an int"
    assert isinstance(operation, int), "the operation should be an int"

    result = lind_fs_flock(args)

    return result

#end include fs_flock.repy

#begin include fs_rename.repy
"""

Handlers for the rename system call.

Called from dispatcher.repy

Safe version checks all parameters, then calls real handler.

Rename hadler pulls out the arguments, does any manditory checking
then calls the repy posix library rename system call.  Then packs
the result back up.

"""


def lind_fs_rename(args):
    """ rename calls are dispatched to this function.

    See dispatcher.repy for details.

    Given the handle and size in a list,
    pull them out and make the actual syscall in the
    file system library.

    Pack the single int returned, or error.
    """

    old = args[0]
    new = args[1]

    try:
        result = rename_syscall(old, new)
    except SyscallError, e:
        return ErrorResponseBuilder("fs_rename", e[1], e[2])

    return SuccessResponseBuilder("fs_rename", result)
        

def lind_safe_fs_rename(args):
    """ Safely wrap the rename call.

    See dispatcher.repy for details.

    Check the handle and size for consistancy,
    then call the real rename dispatcher.

    """
    
    old = args[0]
    new = args[1]

    assert isinstance(old, str)
    assert isinstance(new, str)
    assert len(old) != 0 and len(new) != 0, "Empty string in rename"
    
    result = lind_fs_rename(args)
    
    return result

#end include fs_rename.repy

#begin include debug.repy

def lind_debug_trace(args):
  log("[info][Trace]["+ str(mycontext[COMP])+"] " + args[0] + "\n")
  return SuccessResponseBuilder("debug_trace", 0)


def lind_debug_noop(args):
  return SuccessResponseBuilder("debug_noop", 0)



#end include debug.repy

#begin include unimplemented_syscalls.repy

def lind_fs_ioctl(args):
  log("IOCTL was called with,"+ str(args))
  unimplemented("ioctl")
  return SuccessResponseBuilder("fs_ioctl", SUCCESS)
  
def lind_err_enosys(args):
  return  ErrorResponseBuilder("err_enosys", "ENOSYS", "This system call is not implemented yet or disabled in Lind.")




#end include unimplemented_syscalls.repy

#begin include dispatcher.repy
NOOP_CALL_NUM=1

# MODE="safe"
MODE="fast"

def setup_dispatcher(comp_num):
  # map a systemcall number to a particular function
  if MODE == "safe":
    comp(comp_num)[SYSCALL] = {
    1:lind_debug_noop,
    2:lind_safe_fs_access,
    3:lind_debug_trace,
    4:lind_safe_fs_unlink,
    5:lind_safe_fs_link,
    6:lind_safe_fs_chdir,
    7:lind_safe_fs_mkdir,
    8:lind_safe_fs_rmdir,                      
    9:lind_safe_fs_xstat,                      
    10:lind_safe_fs_open,
    11:lind_safe_fs_close,
    12:lind_safe_fs_read,
    13:lind_safe_fs_write,
    14:lind_safe_fs_lseek,
    15:lind_fs_ioctl,
    17:lind_safe_fs_fxstat,
    19:lind_safe_fs_fstatfs,
    23:lind_safe_fs_getdents,
    24:lind_safe_fs_dup,
    25:lind_safe_fs_dup2,
    26:lind_safe_fs_statfs,
    28:lind_safe_fs_fcntl,

    31:lind_sys_getpid,
      
    32:lind_safe_net_socket,
    33:lind_safe_net_bind,
    34:lind_safe_net_send,
    35:lind_safe_net_sendto,
    36:lind_safe_net_recv,
    37:lind_safe_net_recvfrom,
    38:lind_safe_net_connect,
    39:lind_safe_net_listen,
    40:lind_safe_net_accept,
    41:lind_safe_net_getpeername,
    42:lind_safe_net_getsockname,
    43:lind_safe_net_getsockopt,
    44:lind_safe_net_setsockopt,
    45:lind_safe_net_shutdown,
    46:lind_safe_net_select,
    47:lind_safe_net_getifaddrs,
    48:lind_safe_net_poll,
    49:lind_safe_net_socketpair,
    50:lind_safe_sys_getuid,
    51:lind_safe_sys_geteuid,
    52:lind_safe_sys_getgid,
    53:lind_safe_sys_getegid,
    54:lind_safe_fs_flock,
    55:lind_safe_fs_rename,

    105:lind_comp_cia,
    106:lind_comp_call,
    107:lind_comp_accept,
    108:lind_comp_recv
    }
    
  elif MODE == "fast":
    comp(comp_num)[SYSCALL] = {
    1:lind_debug_noop,
    2:lind_fs_access,
    3:lind_debug_trace,
    4:lind_fs_unlink,
    5:lind_fs_link,
    6:lind_fs_chdir,
    7:lind_fs_mkdir,
    8:lind_fs_rmdir,                      
    9:lind_fs_xstat,                      
    10:lind_fs_open,
    11:lind_fs_close,
    12:lind_fs_read,
    13:lind_fs_write,
    14:lind_fs_lseek,
    15:lind_fs_ioctl,
    17:lind_fs_fxstat,
    19:lind_fs_fstatfs,
    23:lind_fs_getdents,
    24:lind_fs_dup,
    25:lind_fs_dup2,
    26:lind_fs_statfs,
    28:lind_fs_fcntl,

    31:lind_sys_getpid,
      
    32:lind_net_socket,
    33:lind_net_bind,
    34:lind_net_send,
    35:lind_net_sendto,
    36:lind_net_recv,
    37:lind_net_recvfrom,
    38:lind_net_connect,
    39:lind_net_listen,
    40:lind_net_accept,
    41:lind_net_getpeername,
    42:lind_net_getsockname,
    43:lind_net_getsockopt,
    44:lind_net_setsockopt,
    45:lind_net_shutdown,
    46:lind_net_select,
    47:lind_net_getifaddrs,
    48:lind_net_poll,
    49:lind_net_socketpair,
    50:lind_sys_getuid,
    51:lind_sys_geteuid,
    52:lind_sys_getgid,
    53:lind_sys_getegid,
    54:lind_fs_flock,

    105:lind_comp_cia,
    106:lind_comp_call,
    107:lind_comp_accept,
    108:lind_comp_recv

    }
  else:
    assert False, "Invalid mode setting"

  
def dispatch_syscall(call, args):
  """ Given a call number and some arguments in a list call the system call with that call number
  with the provided arguments.
  """

  try:
    call_fun = curr_comp()[SYSCALL][call]

  except KeyError,e:
    log("[ERROR][dispatch] Failed to look up " + str(call) +" with error "+ str(e) + "\n")
    syscall_response =  ErrorResponseBuilder("dispatcher", "ENOSYS", "The system call is not in the system call table. Call="+str(call))

  else:
    syscall_response = call_fun(args)

  assert isinstance(syscall_response, Response), "Returning something that is not a response. Check system calls: " + str(type(syscall_response)) + " form " + str(call)
  
  return syscall_response



#end include dispatcher.repy


def print_times(times):
  print "\nSummary of System Call Execution Times:"
  prefix = ">> "  # prefix which the scripts can use to pull out these numbers
  for eachtime in times:
    each = 0
    call = eachtime[each]
    each += 1
    # using the call number, pull the string name out of the function object
    function_name = str(curr_comp()[SYSCALL][call]).split(" ")[1]
    exec_pre = eachtime[each]
    each += 1
    exec_start = eachtime[each]
    each += 1
    exec_post = eachtime[each]
    each += 1
    exec_stop = eachtime[each]
    each += 1
    exec_before = eachtime[each]
    each += 1
    exec_after = eachtime[each]
    each += 1
    call_args = eachtime[each]
    print prefix, function_name + ", " + "%f" % (exec_pre) + ", " + \
          "%f" % (exec_start) + ", " + "%f" % (exec_post) + ", " + \
          "%f" % (exec_stop) + ", " + "%f" % (exec_before) + ", " + \
          "%f" % (exec_after) + ", \"" + str(call_args) + "\""


def NaclRPCServer(nacl_instance, comp_num):
  #timer =  mycontext["wallclocktime"]
  #times = []
  format = "<i<I<I<I<i<i"
  header_size = struct_calcsize(format)
  max_recv = 16384
  # the expceted message sequence number
  FIRST_SEQ_NUM = -10
  expected_seq_num = FIRST_SEQ_NUM
  booting = True
  while True:
    start = 0
    stop = 0
    response = "Failed with Exception."

    # step 1: pull out the header
    try:
     # pre = timer()
      message = nacl_instance.recv(max_recv)
     # start = timer()
    except exceptions.Exception:
      log("[ERROR][RPC] " + "Exception on receive\n")
      break

    #log("[info][RPC] " +  "Raw Message: "+ message +"\n")
    # assert( len(message) == header_size), "wrong header size"
    if message == "EOT":
      break

    header = message[0:header_size]

    # now parse the header
    magic = 0
    call = 0
    frmt_len = 0
    valid = 0
    payload_size = 0
    seq_num = 0

    try:
      [magic, call, frmt_len, payload_size, seq_num, valid] = struct_unpack(format, header)
    except Exception, err:
      log("[ERROR][RPC] Error unmarshaling header" + str(type(err)) + ":" + str(err) + "\n")
      continue
    # validate the header
    if magic != -2:
      raise Exception("Protocol Error: Magic number not found." + \
                      " Was expecting -2, got " + str(magic))
    # We probably dont need this in the future, but for now:
    checksum = magic + call + frmt_len

    # what happens is that libc overwrites the counter pretty early on
    # for that first, but once that has happened, keep a constat counter.
    if booting:
      if (seq_num != expected_seq_num):
        expected_seq_num = FIRST_SEQ_NUM
        booting = False
        log("Booted")
    elif (seq_num != expected_seq_num):
      pass
#      print "Out of order seq_num %d != %d for call %d" % \
#           (seq_num, expected_seq_num, call)

    expected_seq_num += 1
    if valid != checksum:
      raise Exception("ProtocolError: Validation number not found. We got " + \
                      str(valid) + ", expected " + str(checksum))


    if frmt_len == 0:
      args = []
    else:
      data_start = header_size + frmt_len + 1  # one extra for null char at end of frmt string
      # the part of the string which is the format string
      message_format = message[header_size:data_start-1]
      # print "message format: ", message_format
      try:
        trimmed_string = message[data_start:]
        assert len(trimmed_string) == payload_size, "Reported (%d) payload does not match actual payload (%d)" % (len(trimmed_string), payload_size)
        # print "Args: ",trimmed_string
        args = struct_unpack(message_format, trimmed_string)
        # print "Parsed Args", args
      except ValueError as e:
        log("Unpacking Error: " + str(e) + "\n")
        log("Message was: " + message_format + "\n")
        log("Args len=" + str(len(trimmed_string)) + "\n")
        log("Args String=" + trimmed_string + "\n")
        log("Syscall was=" + str(call) + "\n")
        call = NOOP_CALL_NUM # continue on with eno_sys
    if TRACE:
      strace_msg = [ "[lind_server][trace]", str(str(curr_comp()[SYSCALL][call]).split(" ")[1]), str(args)[:128], " = "]

    # before_call = timer()
    mycontext[LOCK].acquire(True)
    mycontext[COMP] = comp_num
    try:
      response = dispatch_syscall(call, args)
    finally:
      if TRACE:
        strace_msg.append(str(response)[:128])
        log( ''.join(strace_msg))
    mycontext[LOCK].release()
    if response == None:
      raise Exception()

    retcode_buffer = response.make_struct()

    try:
      # post = timer()
      got = nacl_instance.send(retcode_buffer, "")
      # stop = timer()
    except:
      log("[info][RPC] " + "Exception on Send. Stopping\n")
      break
    if got == 0:
      log("[ERROR][RPC] " + "failed to send\n")
      exitall()
  #print "Lind Server ", mycontext[comp_num][PROGRAM], " Shutting Down."
  # print_times(times)


def main():
  code_loc = curr_comp()[PROGRAM]
  nacl = safelyexecutenativecode(code_loc, curr_comp()[CMD_LINE])

  if nacl != None:
    NaclRPCServer(nacl, 1)
  else:
    print "Error: Safe Binary mode must be switched on for this program to work."


def launch_helper(instance, num):
  """save the instance and start the server in a thread."""

  def closure():
    NaclRPCServer(instance, num)
  createthread(closure)


def _check_file(name):
  if name.startswith("/"):
    raise FileNotFoundError("Cannot open files from full path")

  if name.startswith("./"):
    cleanname = name[2:]
  else:
    cleanname = name
  try:
    f = openfile(cleanname, False)
    f.readat(0,100)
    f.close()
  except FileNotFoundError:
    print "File not found:", name
    exitall()
    


def new_compoent():
  """add a new compoent to the system"""
  mycontext[2] = {}
  code_loc = "liblind/com2.nexe"
  mycontext[2][PROGRAM] = code_loc
  
  mycontext[2][CMD_LINE] = []
  setup_dispatcher(2)
  setup_filetable(2)
  setup_component_communication(2)
  nacl = safelyexecutenativecode(code_loc, [])


  if nacl != None:
    launch_helper(nacl, 2)
  else:
    print "Safe Binary mode must be switched on for this program to work."


def setup_filetable(comp_num):
  """Try to open file system. If you can't, then make a new one."""
  log( "Opening file system... ")
  load_fs()
  # load_fs() will check first if the metadata is present, if not
  # present it will create it. I am removing the following call
  # because it duplicates the creation of special files.
  # load_fs_special_files()
  log( "done.")

  # except KeyError, e:


def setup_component_communication(comp_num):
    comp(comp_num)[MBOX] = []


def lind_factory():
  setup_errnos(1)
  setup_dispatcher(1)
  setup_filetable(1)
  setup_component_communication(1)
  mycontext[LOCK] = createlock()
  _check_file(curr_comp()[PROGRAM])
  #if we are running a compoent, launch another one as a test.
  if "com1" in curr_comp()[PROGRAM]:
    log("starting multi-component test mode")
    mycontext[COMP_MODE] = True
    new_compoent()
  else:
    mycontext[COMP_MODE] = False


def parse_commandline():
  mycontext[COMP] = 1
  mycontext[1] = {}
  
  if callargs[0] == "--fast":
    curr_comp()[PROGRAM] = callargs[1]
    curr_comp()[CMD_LINE] = callargs[2:]
    curr_comp()[CMD_LINE].append("--fast")
  else:
    curr_comp()[PROGRAM] = callargs[0]
    curr_comp()[CMD_LINE] = callargs[1:]
  # print curr_comp()[PROGRAM]



if callfunc == "initialize":
  log( "Lind v0." + VERSION[6:-2] + "Last commit:" + "$Date: 2013-03-14 20:42:34 -0400 (Thu, 14 Mar 2013) $"[7:-2])
  parse_commandline()
  lind_factory()

  main()

  log("Persisting metadata: ... ")
  persist_metadata(DEFAULT_METADATA_FILENAME)
  log("Done persisting metadata.")

  

