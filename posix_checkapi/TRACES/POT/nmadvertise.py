""" 
Author: Justin Cappos

Start Date: Sept 1st, 2008

Description:
The advertisement functionality for the node manager

"""

# needed for getruntime
from repyportability import *

# needed to convert keys to strings
#begin include rsa.repy
"""
<Program Name>
  random.repy

<Started>
  2008-04-23

<Author>
  Modified by Anthony Honstain from the following code:
    PyCrypto which is authored by Dwayne C. Litzenberger
    
    Seattle's origional rsa.repy which is Authored by:
      Adapted by Justin Cappos from the version by:
        author = "Sybren Stuvel, Marloes de Boer and Ivo Tamboer"

<Purpose>
  This is the main interface for using the ported RSA implementation.
    
<Notes on port>
  The random function can not be defined with the initial construction of
  the RSAImplementation object, it is hard coded into number_* functions.
    
"""

#begin include random.repy
""" 
<Program Name>
  random.repy

<Author>
  Justin Cappos: random_sample

  Modified by Anthony Honstain
    random_nbit_int and random_long_to_bytes is modified from 
    Python Cryptography Toolkit and was part of pycrypto which 
    is maintained by Dwayne C. Litzenberger
    
    random_range, random_randint, and random_int_below are modified 
    from the Python 2.6.1 random.py module. Which was:
    Translated by Guido van Rossum from C source provided by
    Adrian Baddeley.  Adapted by Raymond Hettinger for use with
    the Mersenne Twister  and os.urandom() core generators.  

<Purpose>
  Random routines (similar to random module in Python)
  
  
<Updates needed when emulmisc.py adds randombytes function>
  TODO-
    random_nbit_int currently uses random_randombytes as a source 
    of random bytes, this is not a permanent fix (the extraction 
    of random bytes from the float is not portable). The change will
    likely be made to random_randombytes (since calls os.urandom will
    likely be restricted to a limited number of bytes).  
  TODO - 
    random_randombytes will remained but serve as a helper function
    to collect the required number of bytes. Calls to randombytes
    will be restricted to a set number of bytes at a time, since
    allowing an arbitrary request to os.urandom would circumvent 
    performance restrictions. 
  TODO - 
    _random_long_to_bytes will no longer be needed.  
      
"""

#begin include math.repy
""" Justin Cappos -- substitute for a few python math routines"""

def math_ceil(x):
  xint = int(x)
  
  # if x is positive and not equal to itself truncated then we should add 1
  if x > 0 and x != xint:
    xint = xint + 1

  # I return a float because math.ceil does
  return float(xint)



def math_floor(x):
  xint = int(x)
  
  # if x is negative and not equal to itself truncated then we should subtract 1
  if x < 0 and x != xint:
    xint = xint - 1

  # I return a float because math.ceil does
  return float(xint)



math_e = 2.7182818284590451
math_pi = 3.1415926535897931

# Algorithm from logN.py on
# http://en.literateprograms.org/Logarithm_Function_(Python)#chunk
# MIT license
#
# hmm, math_log(4.5,4)      == 1.0849625007211561
# Python's math.log(4.5,4)  == 1.0849625007211563
# I'll assume this is okay.
def math_log(X, base=math_e, epsilon=1e-16):
  # JMC: The domain of the log function is {n | n > 0)
  if X <= 0:
    raise ValueError, "log function domain error"

  # log is logarithm function with the default base of e
  integer = 0
  if X < 1 and base < 1:
    # BUG: the cmath implementation can handle smaller numbers...
    raise ValueError, "math domain error"
  while X < 1:
    integer -= 1
    X *= base
  while X >= base:
    integer += 1
    X /= base
  partial = 0.5               # partial = 1/2 
  X *= X                      # We perform a squaring
  decimal = 0.0
  while partial > epsilon:
    if X >= base:             # If X >= base then a_k is 1 
      decimal += partial      # Insert partial to the front of the list
      X = X / base            # Since a_k is 1, we divide the number by the base
    partial *= 0.5            # partial = partial / 2
    X *= X                    # We perform the squaring again
  return (integer + decimal)


#end include math.repy

CACHE = {'bytes': ''}

def randomfloat():
  """
   <Purpose>
     Return a random number in the range [0.0, 1.0) using the
     randombytes() function.
     
   <Arguments>
     None
    
   <Exceptions>
     None

   <Side Effects>
     This function generally results in one or more calls to
     randombytes which uses a OS source of random data which is
     metered.

   <Returns>
     A string of num_bytes random bytes suitable for cryptographic use.
  """
  
  cache = CACHE['bytes']
  num_bytes = 7
  
  # Make sure the cache has enough bytes to give...
  while len(cache) < num_bytes:
    cache += randombytes()
    
  # ...then take what we want.
  randombytes_result = cache[:num_bytes]
  CACHE['bytes'] = cache[num_bytes:]
  
  # Create a random integer.
  randomint = 0L
  for i in range(0, 7):
    randomint = (randomint << 8) 
    randomint = randomint + ord(randombytes_result[i]) 

  # Trim off the excess bits to get 53bits.
  randomint = randomint >> 3
  
  # randomint is a number between 0 and 2**(53) - 1
  return randomint * (2**(-53))



def random_randombytes(num_bytes, random_float=None):
  """
   <Purpose>
     Return a string of length num_bytes, made of random bytes 
     suitable for cryptographic use (because randomfloat draws
     from a os provided random source).
      
     *WARNING* If python implements float as a C single precision
     floating point number instead of a double precision then
     there will not be 53 bits of data in the coefficient.

   <Arguments>
     num_bytes:
               The number of bytes to request from os.urandom. 
               Must be a positive integer value.
     random_float:
                  Should not be used, available only for testing
                  so that predetermined floats can be provided.
    
   <Exceptions>
     None

   <Side Effects>
     This function results in one or more calls to randomfloat 
     which uses a OS source of random data which is metered.

   <Returns>
     A string of num_bytes random bytes suitable for cryptographic use.
  """
  # To ensure accurate testing, this allows the source
  # of random floats to be supplied.
  if random_float is None: 
    random_float = randomfloat()
  
  randombytes = ''
  
  # num_bytes/6 + 1 is used because at most a single float
  # can only result in 6 bytes of random data. So an additional
  # 6 bytes is added and them trimmed to the desired size.
  for byte in range(num_bytes/6 + 1):
    
    # Convert the float back to a integer by multiplying
    # it by 2**53, 53 is used because the expected precision
    # of a python float will be a C type double with a 53 bit 
    # coefficient, this will still depend on the implementation
    # but the standard is to expect 53 bits.
    randomint = int(random_float * (2**53)) 
    # 53 bits trimmed down to 48bits
    # and 48bits is equal to 6 bytes
    randomint = randomint >> 5  
    
    # Transform the randomint into a byte string, 6 bytes were
    # used to create this integer, but several of the leading 
    # bytes could have been trimmed off in the process.
    sixbytes = _random_long_to_bytes(randomint)
    
    # Add on the zeroes that should be there.
    if len(sixbytes) < 6: 
      # pad additions binary zeroes that were lost during 
      # the floats creation.
      sixbytes = '\x00'*(6-len(sixbytes)) + sixbytes 
    randombytes += sixbytes
  
  return randombytes[6 - num_bytes % 6:]


  
def _random_long_to_bytes(long_int):
  """
  <Purpose>
    Convert a long integer to a byte string.   
    Used by random_randombytes to convert integers recovered
    from random floats into its byte representation.
    Used by random_randombytes, random_randombytes is responsible
    for padding any required binary zeroes that are lost in the
    conversion process.     
  """

  long_int = long(long_int)
  byte_string = ''
  temp_int = 0
  
  # Special case to ensure that a non-empty string
  # is always returned.
  if long_int == 0:
    return '\000'
  
  while long_int > 0:
    # Use a bitwise AND to get the last 8 bits from the long.
    #    long_int  -->   1010... 010000001 (base 2)
    #    0xFF      -->            11111111
    #              _______________________
    #  Bitwise AND result -->     10000001
    tmp_int = long_int & 0xFF
    # Place the new character at the front of the string.
    byte_string = "%s%s" % (chr(tmp_int), byte_string)
    # Bitshift the long because the trailing 8 bits have just been read.
    long_int = long_int >> 8
      
  return byte_string



def random_nbit_int(num_bits):  
  """
  <Purpose>
    Returns an random integer that was constructed with
    num_bits many random bits. The result will be an
    integer [0, 2**(num_bits) - 1] inclusive.
     
    For Example:
     If a 10bit number is needed, random_nbit_int(10).
     Min should be greater or equal to 0
     Max should be less than or equal to 1023

    TODO-
      This function currently uses random_randombytes as a source 
      of random bytes, this is not a permanent fix (the extraction 
      of random bytes from the float is not portable). The change will
      likely be made to random_randombytes (since calls os.urandom will
      likely be restricted to a limited number of bytes).

  <Arguments>
    num_bits:
             The number of random bits to be used for construction
             of the random integer to be returned.

  <Exceptions>
    TypeError if non-integer values for num_bits.
      Will accept floats of the type 1.0, 2.0, ...
    
    ValueError if the num_bits is negative or 0.

  <Side Effects>
    This function results in one or more calls to randomfloat 
    which uses a OS source of random data which is metered.

  <Returns>
    Returns a random integer between [0, 2**(num_bits) - 1] inclusive.
  
  <Walkthrough of functions operation>
    This will be a step by step walk through of the key operations
    defined in this function, with the largest possible
    10 bit integer returned.
    
    num_bits = 10
    
    randstring = random_randombytes(10/8)  for our example we
    will suppose that the byte returned was '\xff' (which is the
    same as chr(255)).
    
    odd_bits = 10 % 8 = 2
    Once again we assume that random_randombytes(1) returns the
    maximum possible, which is '\xff'  
    chr = ord('\xff') >> (8 - odd_bits)
    -> chr = 255 >> (8 - 2)
    -> chr = 255 >> 6 = 3   Note 3 is the largest 2 bit number
    chr(3) is appended to randstring resulting in
    randstring = '\x03\xff' 
    
    value = 0
    length = 2
    
    STEP 1 (i = 0):
      value = value << 8 
      -> value = 0
      value = value + ord(randstring[0])
      -> value = 3
    
    STEP 2 (i = 1):
      value = value << 8
      -> value = 768
      value = value + ord(randstring[1])
      -> value = 1023
    
    return 1023
    This is the maximum possible 10 bit integer.
  """
  if num_bits <= 0:
    raise ValueError('number of bits must be greater than zero')
  if num_bits != int(num_bits):
    raise TypeError('number of bits should be an integer')
  
  # The number of bits requested may not be a multiple of
  # 8, then an additional byte will trimmed down.
  randstring = random_randombytes(num_bits/8)

  odd_bits = num_bits % 8
  # A single random byte be converted to an integer (which will
  # be an element of [0,255]) it will then be shifted to the required
  # number of bits.
  # Example: if odd_bits = 3, then the 8 bit retrieved from the 
  # single byte will be shifted right by 5.
  if odd_bits != 0:
    char = ord(random_randombytes(1)) >> (8 - odd_bits)
    randstring = chr(char) + randstring
  
  # the random bytes in randstring will be read from left to right
  result = 0L
  length = len(randstring)
  for i in range(0, length):
    # While result = 0, the bitshift left will still result in 0
    # Since we are dealing with integers, this does not result
    # in the loss of any information.
    result = (result << 8) 
    result = result + ord(randstring[i]) 
  
  assert(result < (2 ** num_bits))
  assert(result >= 0)

  return result



def random_int_below(upper_bound):
  """
  <Purpose>
    Returns an random integer in the range [0,upper_bound)
    
    Handles the case where upper_bound has more bits than returned
    by a single call to the underlying generator.
     
    For Example:
     For a 10bit number, random_int_below(10).
     results would be an element in of the set 0,1,2,..,9.
     
    NOTE: This function is a port from the random.py file in 
    python 2.6.2. For large numbers I have experienced inconsistencies
    when using a naive logarithm function to determine the
    size of a number in bits.  

  <Arguments>
    upper_bound:
           The random integer returned will be in [0, upper_bound).
           Results will be integers less than this argument.

  <Exceptions>
    TypeError if non-integer values for upper_bound.
    ValueError if the upper_bound is negative or 0.

  <Side Effects>
    This function results in one or more calls to randomfloat 
    which uses a OS source of random data which is metered.

  <Returns>
    Returns a random integer between [0, upper_bound).
  
  """
  
  try:
    upper_bound = int(upper_bound)
  except ValueError:
    raise TypeError('number should be an integer')
  
  if upper_bound <= 0:
    raise ValueError('number must be greater than zero')
  
    
  # If upper_bound == 1, the math_log call will loop infinitely.
  # The only int in [0, 1) is 0 anyway, so return 0 here.
  # Resolves bug #927
  if upper_bound == 1:
    return 0
  
  k = int(1.00001 + math_log(upper_bound - 1, 2.0))   # 2**k > n-1 > 2**(k-2)
  r = random_nbit_int(k)
  while r >= upper_bound:
    r = random_nbit_int(k)
  return r

 

def random_randrange(start, stop=None, step=1):
  """
  <Purpose>
    Choose a random item from range(start, stop[, step]).
    
  <Arguments>
    start:
      The random integer returned will be greater than
      or equal to start. 
  
    stop:
      The random integer returned will be less than stop.
      Results will be integers less than this argument.

    step:
      Determines which elements from the range will be considered.
     
  <Exceptions>
    ValueError:
      Non-integer for start or stop argument
      Empty range, if start < 0 and stop is None
      Empty range
      Zero or non-integer step for range

  <Side Effects>
    This function results in one or more calls to randomfloat 
    which uses a OS source of randomdata which is metered.
  
  <Returns>
    Random item from (start, stop[, step]) 'exclusive'
    
  <Notes on port>
    This fixes the problem with randint() which includes the
    endpoint; in Python this is usually not what you want.
    
    Anthony -I removed these since they do not apply
      int=int, default=None, maxwidth=1L<<BPF
      Do not supply the 'int', 'default', and 'maxwidth' arguments.
  """
  maxwidth = 1L<<53

  # This code is a bit messy to make it fast for the
  # common case while still doing adequate error checking.
  istart = int(start)
  if istart != start:
    raise ValueError, "non-integer arg 1 for randrange()"
  if stop is None:
    if istart > 0:
      if istart >= maxwidth:
        return random_int_below(istart)
      return int(randomfloat() * istart)
    raise ValueError, "empty range for randrange()"

  # stop argument supplied.
  istop = int(stop)
  if istop != stop:
    raise ValueError, "non-integer stop for randrange()"
  width = istop - istart
  if step == 1 and width > 0:
    # Note that
    #     int(istart + self.random()*width)
    # instead would be incorrect.  For example, consider istart
    # = -2 and istop = 0.  Then the guts would be in
    # -2.0 to 0.0 exclusive on both ends (ignoring that random()
    # might return 0.0), and because int() truncates toward 0, the
    # final result would be -1 or 0 (instead of -2 or -1).
    #     istart + int(self.random()*width)
    # would also be incorrect, for a subtler reason:  the RHS
    # can return a long, and then randrange() would also return
    # a long, but we're supposed to return an int (for backward
    # compatibility).

    if width >= maxwidth:
      return int(istart + random_int_below(width))
    return int(istart + int(randomfloat()*width))
  if step == 1:
    raise ValueError, "empty range for randrange() (%d,%d, %d)" % (istart, istop, width)

  # Non-unit step argument supplied.
  istep = int(step)
  if istep != step:
    raise ValueError, "non-integer step for randrange()"
  if istep > 0:
    n = (width + istep - 1) // istep
  elif istep < 0:
    n = (width + istep + 1) // istep
  else:
    raise ValueError, "zero step for randrange()"

  if n <= 0:
    raise ValueError, "empty range for randrange()"

  if n >= maxwidth:
    return istart + istep*random_int_below(n)
  return istart + istep*int(randomfloat() * n)



def random_randint(lower_bound, upper_bound):
  """
  <Purpose>
    Return random integer in range [lower_bound, upper_bound], 
    including both end points.
    
  <Arguments>
    upper_bound:
      The random integer returned will be less than upper_bound.
    lower_bound:
      The random integer returned will be greater than
      or equal to the lower_bound.

  <Exceptions>
    None

  <Side Effects>
    This function results in one or more calls to randomfloat 
    which uses a OS source of randomdata which is metered.
  
  <Returns>
    Random integer from [lower_bound, upper_bound] 'inclusive'  
  """
  return random_randrange(lower_bound, upper_bound+1)



def random_sample(population, k):
  """
  <Purpose>
    To return a list containing a random sample from the population.
    
  <Arguments>
    population:
               The elements to be sampled from.
    k: 
      The number of elements to sample
      
  <Exceptions>
    ValueError is sampler larger than population.
    
  <Side Effects>
    This function results in one or more calls to randomfloat 
    which uses a OS source of randomdata which is metered.
    
  <Returns>
    A list of len(k) with random elements from the population.
    
  """
  
  newpopulation = population[:]
  if len(population) < k:
    raise ValueError, "sample larger than population"

  retlist = []
  populationsize = len(population)-1

  for num in range(k):
    pos = random_randint(0,populationsize-num)
    retlist.append(newpopulation[pos])
    del newpopulation[pos]

  return retlist

#end include random.repy
#begin include pycryptorsa.repy
"""
<Program Name>
  pycrypto.repy

<Started>
  2009-01

<Author>
  Modified by Anthony Honstain from the following code:
    PyCrypto which is authored by Dwayne C. Litzenberger
    
<Purpose>
  This file provides the encryption functionality for rsa.repy. 
  This code has been left as close to origional as possible with
  the notes about changes made to enable for easier modification
  if pycrypto is updated. 
  
  It contains:
    pubkey.py
    RSA.py 
    _RSA.py
    _slowmath.py
    number.py

"""

#begin include random.repy
#already included random.repy
#end include random.repy

#
#   pubkey.py : Internal functions for public key operations
#
#  Part of the Python Cryptography Toolkit
#
# Distribute and use freely; there are no restrictions on further
# dissemination and usage except those imposed by the laws of your
# country of residence.  This software is provided "as is" without
# warranty of fitness for use or suitability for any purpose, express
# or implied. Use at your own risk or not at all.
#

"""
<Modified>
  Anthony
  
  Apr 7:
    Modified behavior of _verify to maintain backwards compatibility.
  Apr 18:
    Adjusted sign to return a long instead of bytes.
    Adjusted verify to accept a long instead of bytes.
  Apr 27:
    Modified encrypt to return a long.
    Modified decrypt to accept a long as its cipher text argument.
    Large change, dropped out behavior for taking tuples, since
    it will never be used in this way for RSA, pubkey has that 
    behavior because of DSA and ElGamal.
    
  NEW ARGUEMENT TYPE AND RETURN TYPE OF
  ENCRYPT DECRYPT SIGN and VERIFY:
  
           Argument Type        Return Type
  --------------------------------------------
  encrypt  |  byte                (long,)
  decrypt  |  long                byte
  sign     |  byte                (long,)
  verify   |  long                byte  

"""

# Anthony stage1
#__revision__ = "$Id$"

# Anthony stage 2, allusage of types.StringType or types.TupleType
# were replaced with type("") and type((1,1))
#import types

# Anthony stage 2, removed the warning completely
#import warnings

# Anthony stage1
#from number import *
#import number  #stage 2

# Basic public key class
class pubkey_pubkey:
    def __init__(self):
        pass

    # Anthony - removed because we are not using pickle
    #def __getstate__(self):
    #    """To keep key objects platform-independent, the key data is
    #    converted to standard Python long integers before being
    #    written out.  It will then be reconverted as necessary on
    #    restoration."""
    #    d=self.__dict__
    #    for key in self.keydata:
    #        if d.has_key(key): d[key]=long(d[key])
    #    return d
    #
    #def __setstate__(self, d):
    #    """On unpickling a key object, the key data is converted to the big
    #    number representation being used, whether that is Python long
    #    integers, MPZ objects, or whatever."""
    #    for key in self.keydata:
    #        if d.has_key(key): self.__dict__[key]=bignum(d[key])

    def encrypt(self, plaintext, K):
        """encrypt(plaintext:string|long, K:string|long) : tuple
        Encrypt the string or integer plaintext.  K is a random
        parameter required by some algorithms.
        """
        # Anthony - encrypt now simply returns the ciphertext
        # as a long.
        wasString=0
        if isinstance(plaintext, type("")):
            # Anthony stage1 added number.bytes_to_long(
            plaintext=number_bytes_to_long(plaintext) ; wasString=1
        #if isinstance(K, type("")):
        #    # Anthony stage1 added number.bytes_to_long(
        #    K=number_bytes_to_long(K)
        ciphertext=self._encrypt(plaintext, K)
        # Anthony stage1 added number.long_to_bytes(
        #if wasString: return tuple(map(number_long_to_bytes, ciphertext))
        #else: return ciphertext
        return ciphertext

    def decrypt(self, ciphertext):
        """decrypt(ciphertext:tuple|string|long): string
        Decrypt 'ciphertext' using this key.
        """
        # Anthony - decrypt now accepts the arguement ciphertext
        # as a long.
        #wasString=0
        #if not isinstance(ciphertext, type((1,1))):
        #    ciphertext=(ciphertext,)
        #if isinstance(ciphertext[0], type("")):
        #    # Anthony stage1 added number.bytes_to_long
        #    ciphertext=tuple(map(number_bytes_to_long, ciphertext)) ; wasString=1
        plaintext=self._decrypt(ciphertext)
        ## Anthony stage1 added number.long_to_bytes(
        #if wasString: return number_long_to_bytes(plaintext)
        #else: return plaintext
        return number_long_to_bytes(plaintext)

    def sign(self, M, K):
        """sign(M : string|long, K:string|long) : tuple
        Return a tuple containing the signature for the message M.
        K is a random parameter required by some algorithms.
        """
        if (not self.has_private()):
            raise error, 'Private key not available in this object'
        # Anthony stage1 added number.bytes_to_long(
        if isinstance(M, type("")): M=number_bytes_to_long(M)
        if isinstance(K, type("")): K=number_bytes_to_long(K)
        # Anthony - modified to provide backwards compatability - required for
        # pycrypto unittest.
        #return self._sign(M, K)
        # Anthony - Apr18 adjusted to return a long instead of bytes
        #return (number_long_to_bytes(self._sign(M, K)[0]),)
        return (self._sign(M, K)[0], )

    def verify(self, signature):    
    # Anthony - modified to provide backwards compatability - required for 
    # pycrypto unittest.
    #def verify (self, M, signature):
    #    """verify(M:string|long, signature:tuple) : bool
    #    Verify that the signature is valid for the message M;
    #    returns true if the signature checks out.
    #    """
    #    ## Anthony stage1 added number.bytes_to_long(
    #    if isinstance(M, type("")): M=number_bytes_to_long(M)
    #    return self._verify(M, signature)
    
        # Anthony - Apr18 adjusted to return a long instead of bytes    
        #return number_long_to_bytes(self._verify(number_bytes_to_long(signature)))
        return number_long_to_bytes(self._verify(signature))
        
    # Anthony stage 2, removing warnings import.
    # alias to compensate for the old validate() name
    #def validate (self, M, signature):
    #    warnings.warn("validate() method name is obsolete; use verify()",
    #                  DeprecationWarning)

    def blind(self, M, B):
        """blind(M : string|long, B : string|long) : string|long
        Blind message M using blinding factor B.
        """
        wasString=0
        if isinstance(M, type("")):
            # Anthony stage1 added number.bytes_to_long(
            M=number_bytes_to_long(M) ; wasString=1
        # Anthony stage1 added number.bytes_to_long(
        if isinstance(B, type("")): B=number_bytes_to_long(B)
        blindedmessage=self._blind(M, B)
        # Anthony stage1 added number.long_to_bytes(
        if wasString: return number_long_to_bytes(blindedmessage)
        else: return blindedmessage

    def unblind(self, M, B):
        """unblind(M : string|long, B : string|long) : string|long
        Unblind message M using blinding factor B.
        """
        wasString=0
        if isinstance(M, type("")):
            # Anthony stage1 added number.bytes_to_long(
            M=number_bytes_to_long(M) ; wasString=1
        # Anthony stage1 added number.bytes_to_long(
        if isinstance(B, type("")): B=number_bytes_to_long(B)
        unblindedmessage=self._unblind(M, B)
        # Anthony stage1 added number.long_to_bytes(
        if wasString: return number_long_to_bytes(unblindedmessage)
        else: return unblindedmessage


    # The following methods will usually be left alone, except for
    # signature-only algorithms.  They both return Boolean values
    # recording whether this key's algorithm can sign and encrypt.
    def can_sign (self):
        """can_sign() : bool
        Return a Boolean value recording whether this algorithm can
        generate signatures.  (This does not imply that this
        particular key object has the private information required to
        to generate a signature.)
        """
        return 1

    def can_encrypt (self):
        """can_encrypt() : bool
        Return a Boolean value recording whether this algorithm can
        encrypt data.  (This does not imply that this
        particular key object has the private information required to
        to decrypt a message.)
        """
        return 1

    def can_blind (self):
        """can_blind() : bool
        Return a Boolean value recording whether this algorithm can
        blind data.  (This does not imply that this
        particular key object has the private information required to
        to blind a message.)
        """
        return 0

    # The following methods will certainly be overridden by
    # subclasses.

    def size (self):
        """size() : int
        Return the maximum number of bits that can be handled by this key.
        """
        return 0

    def has_private (self):
        """has_private() : bool
        Return a Boolean denoting whether the object contains
        private components.
        """
        return 0

    def publickey (self):
        """publickey(): object
        Return a new key object containing only the public information.
        """
        return self
    
    # Anthony - removed, not using pickle
    #def __eq__ (self, other):
    #    """__eq__(other): 0, 1
    #    Compare us to other for equality.
    #    """
    #    return self.__getstate__() == other.__getstate__()
        # -*- coding: utf-8 -*-
#
#  PublicKey/RSA.py : RSA public key primitive
#
# Copyright (C) 2008  Dwayne C. Litzenberger <dlitz@dlitz.net>
#
# =======================================================================
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# =======================================================================

"""RSA public-key cryptography algorithm."""

"""
<Modified>  
  Anthony 
  Feb 9:
    removed the import of Crypto.Util.python_compat, dont need 
    to support python 2.1 ..
  
    Removed _fastmath import and Crypto Random
  
  Feb 15:
    removed code that set a Random function.
    
  Apr 7:
    Modified behavior of _verify to maintain backwars compatibility.
  Apr 27:
    Modified decrypt to accept a long as its cipher text argument.
    Large change, dropped out behavior for taking tuples, since
    it will never be used in this way for RSA, pubkey has that 
    behavior because of DSA and ElGamal.
  Oct 5 2009:
    Modified RSA-RSAobj.__init__ to correctly reload the required
    key values, the code was using getattr but this is no longer
    allowed by repy.
  
"""
# Anthony stage 1
#__revision__ = "$Id$"

# Anthony stage 2
#__all__ = ['generate', 'construct', 'error']

# Anthony
#from Crypto.Util.python_compat import *

# Anthony removing all imports for stage 2
#import _RSA    
#import _slowmath
#import pubkey

# Anthony - not porting Random package yet.
#from Crypto import Random

# Anthony
#try:
#    from Crypto.PublicKey import _fastmath
#except ImportError:
#    _fastmath = None

class RSA_RSAobj(pubkey_pubkey):
    keydata = ['n', 'e', 'd', 'p', 'q', 'u']

    def __init__(self, implementation, key):        
        self.implementation = implementation
        self.key = key
    
    # Anthony - these were assigned in place of the behavior provided
    # by the __getattr__ function which is not supported in repy. 
    # Anthony Oct 5 2009: Modified again because getattr was no
    # longer allowed by repy.   
        try:
            self.n = self.key.n
        except AttributeError:
            pass
        try:
            self.e = self.key.e
        except AttributeError:
            pass
        try:
            self.d = self.key.d
        except AttributeError:
            pass
        try:
            self.p = self.key.p
        except AttributeError:
            pass
        try:
            self.q = self.key.q
        except AttributeError:
            pass
        try:
            self.u = self.key.u
        except AttributeError:
            pass
        
          
    # Anthony - not allowed in repy 
    #def __getattr__(self, attrname):
    #    if attrname in self.keydata:
    #        # For backward compatibility, allow the user to get (not set) the
    #        # RSA key parameters directly from this object.
    #        return getattr(self.key, attrname)
    #    else:
    #        raise AttributeError("%s object has no %r attribute" % (self.__class__.__name__, attrname,))

    def _encrypt(self, c, K):
        return (self.key._encrypt(c),)

    def _decrypt(self, c):
        #(ciphertext,) = c
        #(ciphertext,) = c[:1]  # HACK - We should use the previous line
                               # instead, but this is more compatible and we're
                               # going to replace the Crypto.PublicKey API soon
                               # anyway.
        #return self.key._decrypt(ciphertext)
        return self.key._decrypt(c)

    def _blind(self, m, r):
        return self.key._blind(m, r)

    def _unblind(self, m, r):
        return self.key._unblind(m, r)

    def _sign(self, m, K=None):
        return (self.key._sign(m),)
        
    def _verify(self, sig):
    # Anthony - modified to provide backwards compatability
    #def _verify(self, m, sig):
    #    #(s,) = sig
    #    (s,) = sig[:1]  # HACK - We should use the previous line instead, but
    #                    # this is more compatible and we're going to replace
    #                    # the Crypto.PublicKey API soon anyway.
    #    # Anthony - modified to provide backwars compatability
    #    return self.key._verify(m, s)
        return self.key._verify(sig)

    def has_private(self):
        return self.key.has_private()

    def size(self):
        return self.key.size()

    def can_blind(self):
        return True

    def can_encrypt(self):
        return True

    def can_sign(self):
        return True

    def publickey(self):
        return self.implementation.construct((self.key.n, self.key.e))

    # Anthony - removing this functionality, not allowed in repy
    """
    def __getstate__(self):
        d = {}
        for k in self.keydata:
            try:
                d[k] = getattr(self.key, k)
            except AttributeError:
                pass
        return d

    def __setstate__(self, d):
        if not hasattr(self, 'implementation'):
            self.implementation = RSAImplementation()
        t = []
        for k in self.keydata:
            if not d.has_key(k):
                break
            t.append(d[k])
        self.key = self.implementation._math.rsa_construct(*tuple(t))

    def __repr__(self):
        attrs = []
        for k in self.keydata:
            if k == 'n':
                attrs.append("n(%d)" % (self.size()+1,))
            elif hasattr(self.key, k):
                attrs.append(k)
        if self.has_private():
            attrs.append("private")
        return "<%s @0x%x %s>" % (self.__class__.__name__, id(self), ",".join(attrs))
    """
class RSA_RSAImplementation(object):
    def __init__(self, **kwargs):
        
      
        #Anthony - removed this code, never going to use fast_math
        # 
        ## 'use_fast_math' parameter:
        ##   None (default) - Use fast math if available; Use slow math if not.
        ##   True - Use fast math, and raise RuntimeError if it's not available.
        ##   False - Use slow math.
        #use_fast_math = kwargs.get('use_fast_math', None)
        #if use_fast_math is None:   # Automatic
        #    if _fastmath is not None:
        #        self._math = _fastmath
        #    else:
        #        self._math = _slowmath
        #
        #elif use_fast_math:     # Explicitly select fast math
        #    if _fastmath is not None:
        #        self._math = _fastmath
        #    else:
        #        raise RuntimeError("fast math module not available")
        #
        #else:   # Explicitly select slow math
        #    self._math = _slowmath
        
        #Anthony - added to set _slowmath by default.
        # stage 2, there is no add _slowmath module to the object
        # since we no longer can choose _fastmath
        #self._math = _slowmath
        
        # Anthony stage 2
        #self.error = self._math.error
        self.error = _slowmath_error

        # 'default_randfunc' parameter:
        #   None (default) - use Random.new().read
        #   not None       - use the specified function
        self._default_randfunc = kwargs.get('default_randfunc', None)
        self._current_randfunc = None

    def _get_randfunc(self, randfunc):
        # Anthony - Adjusting to get a random function working
        #if randfunc is not None:
        #    return randfunc
        #elif self._current_randfunc is None:
        #    self._current_randfunc = Random.new().read
        return self._current_randfunc

    def generate(self, bits, randfunc=None, progress_func=None):
        rf = self._get_randfunc(randfunc)
        obj = _RSA_generate_py(bits, rf, progress_func)    # TODO: Don't use legacy _RSA module
        key = _slowmath_rsa_construct(obj.n, obj.e, obj.d, obj.p, obj.q, obj.u)
        return RSA_RSAobj(self, key)

    def construct(self, tup):
        key = _slowmath_rsa_construct(*tup)
        return RSA_RSAobj(self, key)

# Anthony these will not be used in repy.
#_impl = RSAImplementation()
#generate = _impl.generate
#construct = _impl.construct
#error = _impl.error




#
#   RSA.py : RSA encryption/decryption
#
#  Part of the Python Cryptography Toolkit
#
# Distribute and use freely; there are no restrictions on further
# dissemination and usage except those imposed by the laws of your
# country of residence.  This software is provided "as is" without
# warranty of fitness for use or suitability for any purpose, express
# or implied. Use at your own risk or not at all.
#


# Anthony, not allowed for REPY
#__revision__ = "$Id$"

"""
<Modified> 
  Anthony - Feb 24 
  full conversion to stage2 repy port
  
  Anthony - Jun 1
  _RSA_generate_py will no longer generate a p and q such that 
  GCD( e, (p-1)(q-1)) != 1. The old behavior resulted in an invalid
  key when d was computed (it resulted in d = 1).

"""

# Anthony stage2
#import pubkey
#import number

def _RSA_generate_py(bits, randfunc, progress_func=None):
    """generate(bits:int, randfunc:callable, progress_func:callable)

    Generate an RSA key of length 'bits', using 'randfunc' to get
    random data and 'progress_func', if present, to display
    the progress of the key generation.
    
    <Modified>
      Anthony - Because e is fixed, it is possible that a p or q
      is generated such that (p-1)(q-1) is not relatively prime to e.
      A check after p and q are generated will result in p and q
      discarded if either (p-1) or (q-1) is congruent to 0 modulo e.
      
    """
    obj=_RSA_RSAobj()

    # Generate the prime factors of n
    if progress_func:
        progress_func('p,q\n')
        
    p = q = 1L
    while number_size(p*q) < bits:
        # Note that q might be one bit longer than p if somebody specifies an odd
        # number of bits for the key. (Why would anyone do that?  You don't get
        # more security.)
        
        # Anthony stage1 - because pubkey is not using a 
        # 'from number import *' we will call getPrime from
        # number instead
        #p = pubkey.getPrime(bits/2, randfunc)
        #q = pubkey.getPrime(bits - (bits/2), randfunc)
        p = number_getPrime(bits/2, randfunc)
        q = number_getPrime(bits - (bits/2), randfunc)
        
        # Anthony - This is an new modification to the scheme, it is
        # very unlikely that p-1 or q-1 will be a multiple of 65537.
        if ((p - 1) % 65537 == 0) or ((q - 1) % 65537 == 0):
          p = q = 1L


    # p shall be smaller than q (for calc of u)
    if p > q:
        (p, q)=(q, p)
    obj.p = p
    obj.q = q

    if progress_func:
        progress_func('u\n')
        
    # Anthony stage1 - pubkey no longer imports inverse()   
    obj.u = number_inverse(obj.p, obj.q)
    obj.n = obj.p*obj.q

    obj.e = 65537L
    if progress_func:
        progress_func('d\n')
    # Anthony stage1 - pubkey no longer imports inverse()    
    obj.d=number_inverse(obj.e, (obj.p-1)*(obj.q-1))

    assert bits <= 1+obj.size(), "Generated key is too small"
    
    return obj

class _RSA_RSAobj(pubkey_pubkey):

    def size(self):
        """size() : int
        Return the maximum number of bits that can be handled by this key.
        """
        return number_size(self.n) - 1

#
#   number.py : Number-theoretic functions
#
#  Part of the Python Cryptography Toolkit
#
# Distribute and use freely; there are no restrictions on further
# dissemination and usage except those imposed by the laws of your
# country of residence.  This software is provided "as is" without
# warranty of fitness for use or suitability for any purpose, express
# or implied. Use at your own risk or not at all.
#

# Anthony
#__revision__ = "$Id$"

# Anthony - no globals
#bignum = long

# New functions
# Anthony stage 1 - since its not called locally might as well remove it
#from _number_new import *

# Anthony stage2 random will be the repy package we use for random
# number untill we are able complete the port. For stage1 I will
# be using python's random.random(). Now stage2 using repy's random

# Commented out and replaced with faster versions below
## def long2str(n):
##     s=''
##     while n>0:
##         s=chr(n & 255)+s
##         n=n>>8
##     return s

## import types
## def str2long(s):
##     if type(s)!=types.StringType: return s   # Integers will be left alone
##     return reduce(lambda x,y : x*256+ord(y), s, 0L)

def number_size (N):
    """size(N:long) : int
    Returns the size of the number N in bits.
    """
    bits, power = 0,1L
    while N >= power:
        bits += 1
        power = power << 1
    return bits

#def number_getRandomNumber(N, randfunc=None):
#    """getRandomNumber(N:int, randfunc:callable):long
#    Return an N-bit random number.
#
#    If randfunc is omitted, then Random.new().read is used.
#    
#    Anthony - This function is not called by anything.
#    """
#    
#    # Anthony stage1 - This code has been removed because we
#    # are not using the pycrypto PRNG
#    """
#    if randfunc is None:
#        _import_Random()
#        randfunc = Random.new().read
#
#    S = randfunc(N/8)
#    odd_bits = N % 8
#    if odd_bits != 0:
#        char = ord(randfunc(1)) >> (8-odd_bits)
#        S = chr(char) + S
#    value = bytes_to_long(S)
#    value |= 2L ** (N-1)                # Ensure high bit is set
#    assert size(value) >= N
#    return value
#    """
#    # Anthony stage2 repy random is included
#    return random_randint(2**(N-1), 2**N - 1)
  

def number_GCD(x,y):
    """GCD(x:long, y:long): long
    Return the GCD of x and y.
    """
    x = abs(x) ; y = abs(y)
    while x > 0:
        x, y = y % x, x
    return y

def number_inverse(u, v):
    """inverse(u:long, u:long):long
    Return the inverse of u mod v.
    """
    u3, v3 = long(u), long(v)
    u1, v1 = 1L, 0L
    while v3 > 0:
        q=u3 / v3
        u1, v1 = v1, u1 - v1*q
        u3, v3 = v3, u3 - v3*q
    while u1<0:
        u1 = u1 + v
    return u1

# Given a number of bits to generate and a random generation function,
# find a prime number of the appropriate size.

def number_getPrime(N, randfunc=None):
    """getPrime(N:int, randfunc:callable):long
    Return a random N-bit prime number.

    If randfunc is omitted, then Random.new().read is used.
    """
    # Anthony stage1 removing existing random package
    #if randfunc is None:
    #    _import_Random()
    #    randfunc = Random.new().read

    # Anthony stage2 - using repy random for now
    # for N-bit number, max will be (2^N) - 1
    # and min will be 2^(N-1)
    # This will use a bitwise OR to ensure the number is odd
    #origional: number=getRandomNumber(N, randfunc) | 1
    
    # Anthony - changed this again, now that random.repy
    # includes a function to get a random N bit number
    # that can be used instead.
    #number = random_randint(2**(N-1), 2**N - 1) | 1
    number = random_nbit_int(N) | 1
    
    number |= 2L ** (N-1) # ensure high bit is set 
    
    while (not number_isPrime(number, randfunc=randfunc)):
        number=number+2
    return number

def number_isPrime(N, randfunc=None):
    """isPrime(N:long, randfunc:callable):bool
    Return true if N is prime.

    If randfunc is omitted, then Random.new().read is used.
    """
    
    # Anthony stage1 removing the existing random package
    # does not appear that this code is even used in this method.
    """
    _import_Random()
    if randfunc is None:
        randfunc = Random.new().read

    randint = StrongRandom(randfunc=randfunc).randint
    """
    
    sieve = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59,
       61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127,
       131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193,
       197, 199, 211, 223, 227, 229, 233, 239, 241, 251]
 
    if N == 1:
        return 0
    if N in sieve:
        return 1
    for i in sieve:
        if (N % i)==0:
            return 0
    
    # Anthony - not going to use _fastmath ever
    # Use the accelerator if available
    #if _fastmath is not None:
    #    return _fastmath.isPrime(N)

    # Compute the highest bit that's set in N
    N1 = N - 1L
    n = 1L
    while (n<N):
        n=n<<1L
    n = n >> 1L

    # Rabin-Miller test
    for c in sieve[:7]:
        a=long(c) ; d=1L ; t=n
        while (t):  # Iterate over the bits in N1
            x=(d*d) % N
            if x==1L and d!=1L and d!=N1:
                return 0  # Square root of 1 found
            if N1 & t:
                d=(x*a) % N
            else:
                d=x
            t = t >> 1L
        if d!=1L:
            return 0
    return 1

# Small primes used for checking primality; these are all the primes
# less than 256.  This should be enough to eliminate most of the odd
# numbers before needing to do a Rabin-Miller test at all.


# Improved conversion functions contributed by Barry Warsaw, after
# careful benchmarking



def number_long_to_bytes(n, blocksize=0):
    """long_to_bytes(n:long, blocksize:int) : string
    Convert a long integer to a byte string.

    If optional blocksize is given and greater than zero, pad the front of the
    byte string with binary zeros so that the length is a multiple of
    blocksize.
    
    Anthony - THIS WILL STRIP OFF LEADING '\000' of a string!
           comes in '\000\xe8\...' and will come out of
           long_to_bytes as '\xe8\..'   
    
    """
    s = ''
    n = long(n)
    tmp = 0
    #pack = struct.pack
    while n > 0:
        # Anthony removed the use of struct module
        #s = pack('>I', n & 0xff ff ff ffL) + s
        s = "%s%s" % (chr(n & 0xFF), s)
        n = n >> 8
    # strip off leading zeros
    for i in range(len(s)):
        if s[i] != '\000':
            break
    else:
        # only happens when n == 0
        s = '\000'
        i = 0
        
    s = s[i:]    
    # add back some pad bytes.  this could be done more efficiently w.r.t. the
    # de-padding being done above, but sigh...    
    if blocksize > 0 and len(s) % blocksize:
        s = (blocksize - len(s) % blocksize) * '\000' + s
    return s

def number_bytes_to_long(s):
    """bytes_to_long(string) : long
    Convert a byte string to a long integer.

    This is (essentially) the inverse of long_to_bytes().
    """
    
    acc = 0L
    length = len(s)
    if length % 4:
        extra = (4 - length % 4)
        s = '\000' * extra + s
        length = length + extra
    
    for i in range(0, length):
        # Anthony - replaced struct module functionality.
        #acc = (acc << 32) + unpack('>I', s[i:i+4])[0]
        acc = (acc << 8) 
        acc = acc + ord(s[i])
    return acc


# For backwards compatibility...
# Anthony Feb 14 
# removed long2str str2long and _import_Random()
"""
import warnings
def long2str(n, blocksize=0):
    warnings.warn("long2str() has been replaced by long_to_bytes()")
    return long_to_bytes(n, blocksize)
def str2long(s):
    warnings.warn("str2long() has been replaced by bytes_to_long()")
    return bytes_to_long(s)

def _import_Random():
    # This is called in a function instead of at the module level in order to avoid problems with recursive imports
    global Random, StrongRandom
    from Crypto import Random
    from Crypto.Random.random import StrongRandom
"""# -*- coding: utf-8 -*-
#
#  PubKey/RSA/_slowmath.py : Pure Python implementation of the RSA portions of _fastmath
#
# Copyright (C) 2008  Dwayne C. Litzenberger <dlitz@dlitz.net>
#
# =======================================================================
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# =======================================================================

"""Pure Python implementation of the RSA-related portions of Crypto.PublicKey._fastmath."""

"""
<Modified> 
  Anthony - Feb 9 2009
    removed the import of Crypto.Util.python_compat, dont need 
    to support python 2.1 ..
  Anthony - April 7 2009
    Changed return of _verify to coincide with seattle's origional rsa behavior.
  Anthony - April 30 2009
    Changed _slowmath_rsa_construct to allow user to create
    a _slowmath_RSAKey without a public key
  Anthony - May 9 2009
    Modified _slowmath_rsa_construct to allow type int in 
    addition to long.
  Anthony - Oct 5 2009
    Modified _slowmath_RSAKey.has_private and  _slowmath_RSAKey.has_public
    to no longer use hasattr because repy no longer allows hasattr.
    The code was borrowed from the fix for RSA.py (Note: RSA.py is
    lumped together with the other modules to get pycryptorsa.repy
    before distribution.
"""

# Anthony removing globals, looks like this one can go.
#__revision__ = "$Id$"

# Anthony stage 2
#__all__ = ['rsa_construct']

# Anthony - see above for reason
#from Crypto.Util.python_compat import *

# Anthony Stage 1
#from number import size, inverse

# Anthony stage 2
#import number

class _slowmath_error(Exception):
    pass

class _slowmath_RSAKey(object):
    def _blind(self, m, r):
        # compute r**e * m (mod n)
        return m * pow(r, self.e, self.n)

    def _unblind(self, m, r):
        # compute m / r (mod n)
        
        # Anthony stage 1
        return number_inverse(r, self.n) * m % self.n

    def _decrypt(self, c):
        # compute c**d (mod n)
        if not self.has_private():
            raise _slowmath_error("No private key")
        return pow(c, self.d, self.n) # TODO: CRT exponentiation

    def _encrypt(self, m):
        # compute m**d (mod n)
        if not self.has_public():
            raise _slowmath_error("No public key")
        return pow(m, self.e, self.n)

    def _sign(self, m):   # alias for _decrypt
        if not self.has_private():
            raise _slowmath_error("No private key")
        return self._decrypt(m)

    # Anthony - modified to provide backwards compatability with
    # existing procedure. Pycrypto returned a boolean, and the
    # existing repy code requires the encryped signature.
    def _verify(self, sig):
        if not self.has_public():
            raise _slowmath_error("No public key")
    #def _verify(self, m, sig):       
    #    return self._encrypt(sig) == m
        return self._encrypt(sig)

    def has_private(self):
        # Anthony because repy builds private keys that
        # do no have public key data, an additional requirement
        # was added.
        #return hasattr(self, 'd')
        
        # Anthony Oct 5 2009: This is no longer supported under repy
        #return hasattr(self, 'd') and hasattr(self, 'n')
        has_n = False
        has_d = False
        try:
            self.n
            has_n = True
        except AttributeError:
            pass
          
        try:
            self.d
            has_d = True
        except AttributeError:
            pass
        
        return has_d and has_n
      
    def has_public(self):
        # Anthony because repy builds private keys that
        # do no have public key data, an additional requirement
        # was added.
        
        # Anthony Oct 5 2009: This is no longer supported under repy
        #return hasattr(self, 'n') and hasattr(self, 'e') 
        has_n = False
        has_e = False
        try:
            self.n
            has_n = True
        except AttributeError:
            pass
          
        try:
            self.e
            has_e = True
        except AttributeError:
            pass
          
        return has_e and has_n
 

    def size(self):
        """Return the maximum number of bits that can be encrypted"""
        # Anthony stage 2
        return number_size(self.n) - 1

# Anthony - changed to allow user to create a private key
# without the public keys
def _slowmath_rsa_construct(n=None, e=None, d=None, p=None, q=None, u=None):
#def _slowmath_rsa_construct(n, e, d=None, p=None, q=None, u=None):
    """Construct an RSAKey object"""
    # Anthony - changed to allow user to create a private key
    # without the public keys
    #assert isinstance(n, long)
    #assert isinstance(e, long)
    # Anthony - modified May 9 to allow type int for each arguement.
    assert isinstance(n, (int, long, type(None)))
    assert isinstance(e, (int, long, type(None)))
    assert isinstance(d, (int, long, type(None)))
    assert isinstance(p, (int, long, type(None)))
    assert isinstance(q, (int, long, type(None)))
    assert isinstance(u, (int, long, type(None)))
    obj = _slowmath_RSAKey()
    # Anthony - changed to allow user to create a private key
    # without the public keys
    #obj.n = n
    #obj.e = e
    if n is not None: obj.n = n
    if e is not None: obj.e = e
    if d is not None: obj.d = d
    if p is not None: obj.p = p
    if q is not None: obj.q = q
    if u is not None: obj.u = u
    return obj

#end include pycryptorsa.repy
    
     
        
def rsa_gen_pubpriv_keys(bitsize):
  """
  <Purpose>
    Will generate a new key object with a key size of the argument
    bitsize and return it. A recommended value would be 1024.
   
  <Arguments>
    bitsize:
           The number of bits that the key should have. This
           means the modulus (publickey - n) will be in the range
           [2**(bitsize - 1), 2**(bitsize) - 1]           

  <Exceptions>
    None

  <Side Effects>
    Key generation will result in call to metered function for
    random data.

  <Return>
    Will return a key object that rsa_encrypt, rsa_decrypt, rsa_sign,
    rsa_validate can use to preform their tasts.
  """

  rsa_implementation = RSA_RSAImplementation()
  
  # The key returned is of type RSA_RSAobj which is derived 
  # from pubkey_pubkey, and wraps a _slowmath_RSAKey object
  rsa_key = rsa_implementation.generate(bitsize)
  
  return ({'e':rsa_key.e, 'n':rsa_key.n },
          {'d':rsa_key.d, 'p':rsa_key.p, 'q':rsa_key.q })
  


def _rsa_keydict_to_keyobj(publickey = None, privatekey = None):
  """
  <Purpose>
    Will generate a new key object using the data from the dictionary
    passed. This is used because the pycrypto scheme uses
    a key object but we want backwards compatibility which
    requires a dictionary. 
  
  <Arguments>
    publickey:
              Must be a valid publickey dictionary of 
              the form {'n': 1.., 'e': 6..} with the keys
              'n' and 'e'.
    privatekey:
               Must be a valid privatekey dictionary of 
               the form {'d':1.., 'p':1.. 'q': 1..} with
               the keys 'd', 'p', and 'q'
  <Exceptions>
    TypeError if neither argument is provided.
    ValueError if public or private key is invalid.
    
  <Side Effects>
    None  
    
  <Return>
    Will return a key object that rsa_encrypt, rsa_decrypt, rsa_sign,
    rsa_validate will use.
  """
  if publickey is not None:
    if not rsa_is_valid_publickey(publickey):
      raise ValueError, "Invalid public key"
  
  if privatekey is not None:    
    if not rsa_is_valid_privatekey(privatekey):
      raise ValueError, "Invalid private key"
    
  if publickey is None and privatekey is None:
    raise TypeError("Must provide either private or public key dictionary")

  if publickey is None: 
    publickey = {}
  if privatekey is None: 
    privatekey = {}
  
  n = None 
  e = None
  d = None
  p = None
  q = None
  
  if 'd' in privatekey: 
    d = long(privatekey['d'])
  if 'p' in privatekey: 
    p = long(privatekey['p'])
  if 'q' in privatekey: 
    q = long(privatekey['q'])  
  
  if 'n' in publickey: 
    n = long(publickey['n'])
  # n is needed for a private key even thought it is not
  # part of the standard public key dictionary.
  else: n = p*q  
  if 'e' in publickey: 
    e = long(publickey['e'])
  
  rsa_implementation = RSA_RSAImplementation()
  rsa_key = rsa_implementation.construct((n,e,d,p,q))
  
  return rsa_key


def rsa_encrypt(message, publickey):
  """
  <Purpose>
    Will use the key to encrypt the message string.
    
    If the string is to large to be encrypted it will be broken 
    into chunks that are suitable for the keys modulus, 
    by the _rsa_chopstring function.
  
  <Arguments>
    message:
            A string to be encrypted, there is no restriction on size.
      
    publickey:
              Must be a valid publickey dictionary of 
              the form {'n': 1.., 'e': 6..} with the keys
              'n' and 'e'.
      
  <Exceptions>
    ValueError if public key is invalid.
    
    _slowmath_error if the key object lacks a public key 
    (elements 'e' and 'n').
  

  <Side Effects>
    None
    
  <Return>
    Will return a string with the cypher text broken up and stored 
    in the seperate integer representation. For example it might
    be similar to the string " 1422470 3031373 65044827" but with
    much larger integers.
  """
  
  # A key object is created to interact with the PyCrypto
  # encryption suite. The object contains key data and
  # the necessary rsa functions.
  temp_key_obj = _rsa_keydict_to_keyobj(publickey)
  
  return _rsa_chopstring(message, temp_key_obj, temp_key_obj.encrypt)



def rsa_decrypt(cypher, privatekey):
  """
  <Purpose>
    Will use the private key to decrypt the cypher string.
    
    
    If the plaintext string was to large to be encrypted it will 
    use _rsa_gluechops and _rsa_unpicklechops to reassemble the
    origional plaintext after the individual peices are decrypted. 
  
  <Arguments>
    cypher:
           The encrypted string that was returned by rsa_encrypt.
           Example:
             Should have the form " 142247030 31373650 44827705"
    
    privatekey:
               Must be a valid privatekey dictionary of 
               the form {'d':1.., 'p':1.. 'q': 1..} with
               the keys 'd', 'p', and 'q'
    
  <Exceptions>
    ValueError if private key is invalid.
    
    _slowmath_error if the key object lacks a private key 
    (elements 'd' and 'n').
      
  <Return>
    This will return the plaintext string that was encrypted
    with rsa_encrypt.
  
  """
    
  # A key object is created to interact with the PyCrypto
  # encryption suite. The object contains key data and
  # the necessary rsa functions.
  temp_key_obj = _rsa_keydict_to_keyobj(privatekey = privatekey)  
  
  return _rsa_gluechops(cypher, temp_key_obj, temp_key_obj.decrypt)
  


def rsa_sign(message, privatekey):
  """
  <Purpose>
    Will use the key to sign the plaintext string.
        
  <None>
    If the string is to large to be encrypted it will be broken 
    into chunks that are suitable for the keys modulus, 
    by the _rsa_chopstring function. 
  
  <Arguments>
    message:
            A string to be signed, there is no restriction on size.
      
    privatekey:
               Must be a valid privatekey dictionary of 
               the form {'d':1.., 'p':1.. 'q': 1..} with
               the keys 'd', 'p', and 'q'
      
  <Exceptions>
    ValueError if private key is invalid.
    
    _slowmath_error if the key object lacks a private key 
    (elements 'd' and 'n').

  <Side Effects>
    None
    
  <Return>
    Will return a string with the cypher text broken up and stored 
    in the seperate integer representation. For example it might
    be similar to the string " 1422470 3031373 65044827" but with
    much larger integers.
    
  """
  
  # A key object is created to interact with the PyCrypto
  # encryption suite. The object contains key data and
  # the necessary rsa functions.
  temp_key_obj = _rsa_keydict_to_keyobj(privatekey = privatekey) 
  
  return _rsa_chopstring(message, temp_key_obj, temp_key_obj.sign)



def rsa_verify(cypher, publickey):
  """
  <Purpose>
    Will use the private key to decrypt the cypher string.
    
    
    If the plaintext string was to large to be encrypted it will 
    use _rsa_gluechops and _rsa_unpicklechops to reassemble the
    origional plaintext after the individual peices are decrypted. 
  
  <Arguments>
    cypher:
           The signed string that was returned by rsa_sign.
           
           Example:
             Should have the form " 1422470 3031373 65044827"
    
    publickey:
              Must be a valid publickey dictionary of 
              the form {'n': 1.., 'e': 6..} with the keys
              'n' and 'e'.
    
  <Exceptions>
    ValueError if public key is invalid.
    
    _slowmath_error if the key object lacks a public key 
    (elements 'e' and 'n').    
    
  <Side Effects>
    None
    
  <Return>
    This will return the plaintext string that was signed by
    rsa_sign.
    
  """
  
  # A key object is created to interact with the PyCrypto
  # encryption suite. The object contains key data and
  # the necessary rsa functions.  
  temp_key_obj = _rsa_keydict_to_keyobj(publickey)
  
  return _rsa_gluechops(cypher, temp_key_obj, temp_key_obj.verify)  
  


def _rsa_chopstring(message, key, function):
  """
  <Purpose>
    Splits 'message' into chops that are at most as long as 
    (key.size() / 8 - 1 )bytes. 
    
    Used by 'encrypt' and 'sign'.
    
  <Notes on chopping>
    If a 1024 bit key was used, then the message would be
    broken into length x, where 1<= x <= 126.
    (1023 / 8) - 1 = 126
    After being converted to a long, the result would
    be at most 1009 bits and at least 9 bits.
    
      maxstring = chr(1) + chr(255)*126
      minstring = chr(1) + chr(0)
      number_bytes_to_long(maxstring) 
      => 2**1009 - 1
      number_bytes_to_long(minstring)
      => 256
    
    Given the large exponent used by default (65537)
    this will ensure that small message are okay and that
    large messages do not overflow and cause pycrypto to 
    silently fail (since its behavior is undefined for a 
    message greater then n-1 (where n in the key modulus).   
    
    WARNING: key.encrypt could have undefined behavior
    in the event a larger message is encrypted.
  
  """
  
  msglen = len(message)
  
  # the size of the key in bits, minus one
  # so if the key was a 1024 bits, key.size() returns 1023
  nbits = key.size() 
  
  # JAC: subtract a byte because we're going to add an extra char on the front
  # to properly handle leading \000 bytes and ensure no loss of information.
  nbytes = int(nbits / 8) - 1
  blocks = int(msglen / nbytes)
  
  if msglen % nbytes > 0:
    blocks += 1

  # cypher will contain the integers returned from either
  # sign or encrypt.
  cypher = []
    
  for bindex in range(blocks):
    offset = bindex * nbytes
    block = message[offset:offset+nbytes]
    # key.encrypt will return a bytestring
    # IMPORTANT: The block is padded with a '\x01' to ensure
    # that no information is lost when the key transforms the block
    # into its long representation prior to encryption. It is striped
    # off in _rsa_gluechops.
    # IMPORTANT: both rsa_encrypt and rsa_sign which use _rsa_chopstring
    # will pass the argument 'function' a reference to encrypt or
    # sign from the baseclass publickey.publickey, they will return
    # the cypher as a tuple, with the first element being the desired
    # integer result.  
    # Example result :   ( 1023422341232124123212 , )
    # IMPORTANT: the second arguement to function is ignored
    # by PyCrypto but required for different algorithms.
    cypher.append( function(chr(1) + block, '0')[0])

  return _rsa_picklechops(cypher)



def _rsa_gluechops(chops, key, function):
  """
  Glues chops back together into a string. Uses _rsa_unpicklechops to
  get a list of cipher text blocks in byte form, then key.decrypt
  is used and the '\x01' pad is striped.
  
  Example 
    chops=" 126864321546531240600979768267740190820"
    after _rsa_unpicklechops(chops)
    chops=['\x0b\xed\xf5\x0b;G\x80\xf4\x06+\xff\xd3\xf8\x1b\x8f\x9f']
  
  Used by 'decrypt' and 'verify'.
  """
  message = ""

  # _rsa_unpicklechops returns a list of the choped encrypted text
  # Will be a list with elements of type long
  chops = _rsa_unpicklechops(chops)    
  for cpart in chops:
    # decrypt will return the plaintext message as a bytestring   
    message += function(cpart)[1:] # Remove the '\x01'
        
  return message



def _rsa_picklechops(chops):
  """previously used to pickles and base64encodes it's argument chops"""
  
  retstring = ''
  for item in chops:  
    # the elements of chops will be of type long
    retstring = retstring + ' ' + str(item)
  return retstring



def _rsa_unpicklechops(string):
  """previously used to base64decode and unpickle it's argument string"""
  
  retchops = []
  for item in string.split():
    retchops.append(long(item))
  return retchops



def rsa_is_valid_privatekey(key):
  """
  <Purpose>
     This tries to determine if a key is valid.   If it returns False, the
     key is definitely invalid.   If True, the key is almost certainly valid
  
  <Arguments>
    key:
        A dictionary of the form {'d':1.., 'p':1.. 'q': 1..} 
        with the keys 'd', 'p', and 'q'    
                  
  <Exceptions>
    None

  <Side Effects>
    None
    
  <Return>
    If the key is valid, True will be returned. Otherwise False will
    be returned.
     
  """
  # must be a dict
  if type(key) is not dict:
    return False

  # missing the right keys
  if 'd' not in key or 'p' not in key or 'q' not in key:
    return False

  # has extra data in the key
  if len(key) != 3:
    return False

  for item in ['d', 'p', 'q']:
    # must have integer or long types for the key components...
    if type(key[item]) is not int and type(key[item]) is not long:
      return False

  if number_isPrime(key['p']) and number_isPrime(key['q']):
    # Seems valid...
    return True
  else:
    return False



def rsa_is_valid_publickey(key):
  """
  <Purpose>
    This tries to determine if a key is valid.   If it returns False, the
    key is definitely invalid.   If True, the key is almost certainly valid
  
  <Arguments>
    key:
        A dictionary of the form {'n': 1.., 'e': 6..} with the 
        keys 'n' and 'e'.  
                  
  <Exceptions>
    None

  <Side Effects>
    None
    
  <Return>
    If the key is valid, True will be returned. Otherwise False will
    be returned.
    
  """
  # must be a dict
  if type(key) is not dict:
    return False

  # missing the right keys
  if 'e' not in key or 'n' not in key:
    return False

  # has extra data in the key
  if len(key) != 2:
    return False

  for item in ['e', 'n']:
    # must have integer or long types for the key components...
    if type(key[item]) is not int and type(key[item]) is not long:
      return False

  if key['e'] < key['n']:
    # Seems valid...
    return True
  else:
    return False
  
  

def rsa_publickey_to_string(publickey):
  """
  <Purpose>
    To convert a publickey to a string. It will read the
    publickey which should a dictionary, and return it in
    the appropriate string format.
  
  <Arguments>
    publickey:
              Must be a valid publickey dictionary of 
              the form {'n': 1.., 'e': 6..} with the keys
              'n' and 'e'.
    
  <Exceptions>
    ValueError if the publickey is invalid.

  <Side Effects>
    None
    
  <Return>
    A string containing the publickey. 
    Example: if the publickey was {'n':21, 'e':3} then returned
    string would be "3 21"
  
  """
  if not rsa_is_valid_publickey(publickey):
    raise ValueError, "Invalid public key"

  return str(publickey['e'])+" "+str(publickey['n'])


def rsa_string_to_publickey(mystr):
  """
  <Purpose>
    To read a private key string and return a dictionary in 
    the appropriate format: {'n': 1.., 'e': 6..} 
    with the keys 'n' and 'e'.
  
  <Arguments>
    mystr:
          A string containing the publickey, should be in the format
          created by the function rsa_publickey_to_string.
          Example if e=3 and n=21, mystr = "3 21"
          
  <Exceptions>
    ValueError if the string containing the privateky is 
    in a invalid format.

  <Side Effects>
    None
    
  <Return>
    Returns a publickey dictionary of the form 
    {'n': 1.., 'e': 6..} with the keys 'n' and 'e'.
  
  """
  if len(mystr.split()) != 2:
    raise ValueError, "Invalid public key string"
  
  return {'e':long(mystr.split()[0]), 'n':long(mystr.split()[1])}



def rsa_privatekey_to_string(privatekey):
  """
  <Purpose>
    To convert a privatekey to a string. It will read the
    privatekey which should a dictionary, and return it in
    the appropriate string format.
  
  <Arguments>
    privatekey:
               Must be a valid privatekey dictionary of 
               the form {'d':1.., 'p':1.. 'q': 1..} with
               the keys 'd', 'p', and 'q'    
                  
  <Exceptions>
    ValueError if the privatekey is invalid.

  <Side Effects>
    None
    
  <Return>
    A string containing the privatekey. 
    Example: if the privatekey was {'d':21, 'p':3, 'q':7} then returned
    string would be "21 3 7"
  
  """
  if not rsa_is_valid_privatekey(privatekey):
    raise ValueError, "Invalid private key"

  return str(privatekey['d'])+" "+str(privatekey['p'])+" "+str(privatekey['q'])



def rsa_string_to_privatekey(mystr):
  """
  <Purpose>
    To read a private key string and return a dictionary in 
    the appropriate format: {'d':1.., 'p':1.. 'q': 1..} 
    with the keys 'd', 'p', and 'q' 
  
  <Arguments>
    mystr:
          A string containing the privatekey, should be in the format
          created by the function rsa_privatekey_to_string.
          Example mystr = "21 7 3"
             
  <Exceptions>
    ValueError if the string containing the privateky is 
    in a invalid format.

  <Side Effects>
    None
    
  <Return>
    Returns a privatekey dictionary of the form 
    {'d':1.., 'p':1.. 'q': 1..} with the keys 'd', 'p', and 'q'.
  
  """
  if len(mystr.split()) != 3:
    raise ValueError, "Invalid private key string"
  
  return {'d':long(mystr.split()[0]), 'p':long(mystr.split()[1]), 'q':long(mystr.split()[2])}



def rsa_privatekey_to_file(key,filename):
  """
  <Purpose>
    To write a privatekey to a file. It will convert the
    privatekey which should a dictionary, to the appropriate format
    and write it to a file, so that it can be read by
    rsa_file_to_privatekey.
  
  <Arguments>
    privatekey:
               Must be a valid privatekey dictionary of 
               the form {'d':1.., 'p':1.. 'q': 1..} with
               the keys 'd', 'p', and 'q'
    filename:
             The string containing the name for the desired
             publickey file.
                  
  <Exceptions>
    ValueError if the privatekey is invalid.

    IOError if the file cannot be opened.

  <Side Effects>
    file(filename, "w") will be written to.
    
  <Return>
    None
  
  """
  
  if not rsa_is_valid_privatekey(key):
    raise ValueError, "Invalid private key"

  fileobject = openfile(filename, True)
  fileobject.writeat(rsa_privatekey_to_string(key), 0)
  fileobject.close()



def rsa_file_to_privatekey(filename):
  """
  <Purpose>
    To read a file containing a key that was created with 
    rsa_privatekey_to_file and return it in the appropriate 
    format: {'d':1.., 'p':1.. 'q': 1..} with the keys 'd', 'p', and 'q' 
  
  <Arguments>
    filename:
             The name of the file containing the privatekey.
             
  <Exceptions>
    ValueError if the file contains an invalid private key string.
    
    IOError if the file cannot be opened.

  <Side Effects>
    None
    
  <Return>
    Returns a privatekey dictionary of the form 
    {'d':1.., 'p':1.. 'q': 1..} with the keys 'd', 'p', and 'q'.
  
  """
  fileobject = openfile(filename, False)
  privatekeystring = fileobject.readat(None, 0)
  fileobject.close()

  return rsa_string_to_privatekey(privatekeystring)



def rsa_publickey_to_file(publickey, filename):
  """
  <Purpose>
    To write a publickey to a file. It will convert the
    publickey which should a dictionary, to the appropriate format
    and write it to a file, so that it can be read by
    rsa_file_to_publickey.
  
  <Arguments>
    publickey:
              Must be a valid publickey dictionary of 
              the form {'n': 1.., 'e': 6..} with the keys
              'n' and 'e'.
    filename:
             The string containing the name for the desired
             publickey file.
         
  <Exceptions>
    ValueError if the publickey is invalid.
    
    IOError if the file cannot be opened.

  <Side Effects>
    file(filename, "w") will be written to.
    
  <Return>
    None
  
  """
  
  if not rsa_is_valid_publickey(publickey):
    raise ValueError, "Invalid public key"

  fileobject = openfile(filename, True)
  fileobject.writeat(rsa_publickey_to_string(publickey), 0)
  fileobject.close()



def rsa_file_to_publickey(filename):
  """
  <Purpose>
    To read a file containing a key that was created with 
    rsa_publickey_to_file and return it in the appropriate 
    format:  {'n': 1.., 'e': 6..} with the keys 'n' and 'e'.
  
  <Arguments>
    filename:
             The name of the file containing the publickey.
             
  <Exceptions>
    ValueError if the file contains an invalid public key string.
    
    IOError if the file cannot be opened.

  <Side Effects>
    None
    
  <Return>
    Returns a publickey dictionary of the form 
    {'n': 1.., 'e': 6..} with the keys 'n' and 'e'.
  
  """
  fileobject = openfile(filename, False)
  publickeystring = fileobject.readat(None, 0)
  fileobject.close()

  return rsa_string_to_publickey(publickeystring)


def rsa_matching_keys(privatekey, publickey):
  """
  <Purpose>
    Determines if a pair of public and private keys match and allow 
    for encryption/decryption.
  
  <Arguments>
    privatekey: The private key*
    publickey:  The public key*
    
    * The dictionary structure, not the string or file name
  <Returns>
    True, if they can be used. False otherwise.
  """
  # We will attempt to encrypt then decrypt and check that the message matches
  testmessage = "A quick brown fox."
  
  # Encrypt with the public key
  encryptedmessage = rsa_encrypt(testmessage, publickey)

  # Decrypt with the private key
  try:
    decryptedmessage = rsa_decrypt(encryptedmessage, privatekey)
  except TypeError:
    # If there was an exception, assume the keys are to blame
    return False
  except OverflowError:
    # There was an overflow while decrypting, blame the keys
    return False  
  
  # Test for a match
  return (testmessage == decryptedmessage)

#end include rsa.repy

#begin include advertise.repy
"""
Author: Justin Cappos

Start Date: October 14, 2008

Description:
A stub that allows different announcement types.   I'd make this smarter, but
the user won't configure it, right?


Raises an AdvertiseError exception if there is a problem advertising with either service

"""

#begin include listops.repy
""" 
Author: Justin Cappos

Module: A simple library of list commands that allow the programmer
        to do list composition operations

Start date: November 11th, 2008

This is a really simple module, only broken out to avoid duplicating 
functionality.

This was adopted from previous code in seash.   

I really should be using sets instead I think.   These are merely for 
convenience when you already have lists.

"""


def listops_difference(list_a,list_b):
  """
   <Purpose>
      Return a list that has all of the items in list_a that are not in list_b
      Duplicates are removed from the output list

   <Arguments>
      list_a, list_b:
        The lists to operate on

   <Exceptions>
      TypeError if list_a or list_b is not a list.

   <Side Effects>
      None.

   <Returns>
      A list containing list_a - list_b
  """

  retlist = []
  for item in list_a:
    if item not in list_b:
      retlist.append(item)

  # ensure that a duplicated item in list_a is only listed once
  return listops_uniq(retlist)


def listops_union(list_a,list_b):
  """
   <Purpose>
      Return a list that has all of the items in list_a or in list_b.   
      Duplicates are removed from the output list

   <Arguments>
      list_a, list_b:
        The lists to operate on

   <Exceptions>
      TypeError if list_a or list_b is not a list.

   <Side Effects>
      None.

   <Returns>
      A list containing list_a union list_b
  """

  retlist = list_a[:]
  for item in list_b: 
    if item not in list_a:
      retlist.append(item)

  # ensure that a duplicated item in list_a is only listed once
  return listops_uniq(retlist)


def listops_intersect(list_a,list_b):
  """
   <Purpose>
      Return a list that has all of the items in both list_a and list_b.   
      Duplicates are removed from the output list

   <Arguments>
      list_a, list_b:
        The lists to operate on

   <Exceptions>
      TypeError if list_a or list_b is not a list.

   <Side Effects>
      None.

   <Returns>
      A list containing list_a intersect list_b
  """

  retlist = []
  for item in list_a:
    if item in list_b:
      retlist.append(item)

  # ensure that a duplicated item in list_a is only listed once
  return listops_uniq(retlist)
      

def listops_uniq(list_a):
  """
   <Purpose>
      Return a list that has no duplicate items

   <Arguments>
      list_a
        The list to operate on

   <Exceptions>
      TypeError if list_a is not a list.

   <Side Effects>
      None.

   <Returns>
      A list containing the unique items in list_a
  """
  retlist = []
  for item in list_a:
    if item not in retlist:
      retlist.append(item)

  return retlist



#end include listops.repy
#begin include openDHTadvertise.repy
"""
Author: Justin Cappos

Start Date: July 8, 2008

Description:
Advertises availability to openDHT...

This code is partially adapted from the example openDHT code.

"""

#begin include random.repy
#already included random.repy
#end include random.repy
#begin include sha.repy
#!/usr/bin/env python
# -*- coding: iso-8859-1

"""A sample implementation of SHA-1 in pure Python.

   Adapted by Justin Cappos from the version at: http://codespeak.net/pypy/dist/pypy/lib/sha.py

   Framework adapted from Dinu Gherman's MD5 implementation by
   J. Hall`en and L. Creighton. SHA-1 implementation based directly on
   the text of the NIST standard FIPS PUB 180-1.

date    = '2004-11-17'
version = 0.91 # Modernised by J. Hall`en and L. Creighton for Pypy
"""



# ======================================================================
# Bit-Manipulation helpers
#
#   _long2bytes() was contributed by Barry Warsaw
#   and is reused here with tiny modifications.
# ======================================================================

def _sha_long2bytesBigEndian(n, thisblocksize=0):
    """Convert a long integer to a byte string.

    If optional blocksize is given and greater than zero, pad the front
    of the byte string with binary zeros so that the length is a multiple
    of blocksize.
    """

    # Justin: I changed this to avoid using pack. I didn't test performance, etc
    s = ''
    while n > 0:
        #original: 
        # s = struct.pack('>I', n & 0xffffffffL) + s
        # n = n >> 32
        s = chr(n & 0xff) + s
        n = n >> 8

    # Strip off leading zeros.
    for i in range(len(s)):
        if s[i] <> '\000':
            break
    else:
        # Only happens when n == 0.
        s = '\000'
        i = 0

    s = s[i:]

    # Add back some pad bytes. This could be done more efficiently
    # w.r.t. the de-padding being done above, but sigh...
    if thisblocksize > 0 and len(s) % thisblocksize:
        s = (thisblocksize - len(s) % thisblocksize) * '\000' + s

    return s


def _sha_bytelist2longBigEndian(list):
    "Transform a list of characters into a list of longs."

    imax = len(list)/4
    hl = [0L] * imax

    j = 0
    i = 0
    while i < imax:
        b0 = long(ord(list[j])) << 24
        b1 = long(ord(list[j+1])) << 16
        b2 = long(ord(list[j+2])) << 8
        b3 = long(ord(list[j+3]))
        hl[i] = b0 | b1 | b2 | b3
        i = i+1
        j = j+4

    return hl


def _sha_rotateLeft(x, n):
    "Rotate x (32 bit) left n bits circularly."

    return (x << n) | (x >> (32-n))


# ======================================================================
# The SHA transformation functions
#
# ======================================================================

# Constants to be used
sha_K = [
    0x5A827999L, # ( 0 <= t <= 19)
    0x6ED9EBA1L, # (20 <= t <= 39)
    0x8F1BBCDCL, # (40 <= t <= 59)
    0xCA62C1D6L  # (60 <= t <= 79)
    ]

class sha:
    "An implementation of the MD5 hash function in pure Python."

    def __init__(self):
        "Initialisation."
        
        # Initial message length in bits(!).
        self.length = 0L
        self.count = [0, 0]

        # Initial empty message as a sequence of bytes (8 bit characters).
        self.inputdata = []

        # Call a separate init function, that can be used repeatedly
        # to start from scratch on the same object.
        self.init()


    def init(self):
        "Initialize the message-digest and set all fields to zero."

        self.length = 0L
        self.inputdata = []

        # Initial 160 bit message digest (5 times 32 bit).
        self.H0 = 0x67452301L
        self.H1 = 0xEFCDAB89L
        self.H2 = 0x98BADCFEL
        self.H3 = 0x10325476L
        self.H4 = 0xC3D2E1F0L

    def _transform(self, W):

        for t in range(16, 80):
            W.append(_sha_rotateLeft(
                W[t-3] ^ W[t-8] ^ W[t-14] ^ W[t-16], 1) & 0xffffffffL)

        A = self.H0
        B = self.H1
        C = self.H2
        D = self.H3
        E = self.H4

        """
        This loop was unrolled to gain about 10% in speed
        for t in range(0, 80):
            TEMP = _sha_rotateLeft(A, 5) + sha_f[t/20] + E + W[t] + sha_K[t/20]
            E = D
            D = C
            C = _sha_rotateLeft(B, 30) & 0xffffffffL
            B = A
            A = TEMP & 0xffffffffL
        """

        for t in range(0, 20):
            TEMP = _sha_rotateLeft(A, 5) + ((B & C) | ((~ B) & D)) + E + W[t] + sha_K[0]
            E = D
            D = C
            C = _sha_rotateLeft(B, 30) & 0xffffffffL
            B = A
            A = TEMP & 0xffffffffL

        for t in range(20, 40):
            TEMP = _sha_rotateLeft(A, 5) + (B ^ C ^ D) + E + W[t] + sha_K[1]
            E = D
            D = C
            C = _sha_rotateLeft(B, 30) & 0xffffffffL
            B = A
            A = TEMP & 0xffffffffL

        for t in range(40, 60):
            TEMP = _sha_rotateLeft(A, 5) + ((B & C) | (B & D) | (C & D)) + E + W[t] + sha_K[2]
            E = D
            D = C
            C = _sha_rotateLeft(B, 30) & 0xffffffffL
            B = A
            A = TEMP & 0xffffffffL

        for t in range(60, 80):
            TEMP = _sha_rotateLeft(A, 5) + (B ^ C ^ D)  + E + W[t] + sha_K[3]
            E = D
            D = C
            C = _sha_rotateLeft(B, 30) & 0xffffffffL
            B = A
            A = TEMP & 0xffffffffL


        self.H0 = (self.H0 + A) & 0xffffffffL
        self.H1 = (self.H1 + B) & 0xffffffffL
        self.H2 = (self.H2 + C) & 0xffffffffL
        self.H3 = (self.H3 + D) & 0xffffffffL
        self.H4 = (self.H4 + E) & 0xffffffffL
    

    # Down from here all methods follow the Python Standard Library
    # API of the sha module.

    def update(self, inBuf):
        """Add to the current message.

        Update the md5 object with the string arg. Repeated calls
        are equivalent to a single call with the concatenation of all
        the arguments, i.e. m.update(a); m.update(b) is equivalent
        to m.update(a+b).

        The hash is immediately calculated for all full blocks. The final
        calculation is made in digest(). It will calculate 1-2 blocks,
        depending on how much padding we have to add. This allows us to
        keep an intermediate value for the hash, so that we only need to
        make minimal recalculation if we call update() to add more data
        to the hashed string.
        """

        leninBuf = long(len(inBuf))

        # Compute number of bytes mod 64.
        index = (self.count[1] >> 3) & 0x3FL

        # Update number of bits.
        self.count[1] = self.count[1] + (leninBuf << 3)
        if self.count[1] < (leninBuf << 3):
            self.count[0] = self.count[0] + 1
        self.count[0] = self.count[0] + (leninBuf >> 29)

        partLen = 64 - index

        if leninBuf >= partLen:
            self.inputdata[index:] = list(inBuf[:partLen])
            self._transform(_sha_bytelist2longBigEndian(self.inputdata))
            i = partLen
            while i + 63 < leninBuf:
                self._transform(_sha_bytelist2longBigEndian(list(inBuf[i:i+64])))
                i = i + 64
            else:
                self.inputdata = list(inBuf[i:leninBuf])
        else:
            i = 0
            self.inputdata = self.inputdata + list(inBuf)


    def digest(self):
        """Terminate the message-digest computation and return digest.

        Return the digest of the strings passed to the update()
        method so far. This is a 16-byte string which may contain
        non-ASCII characters, including null bytes.
        """

        H0 = self.H0
        H1 = self.H1
        H2 = self.H2
        H3 = self.H3
        H4 = self.H4
        inputdata = [] + self.inputdata
        count = [] + self.count

        index = (self.count[1] >> 3) & 0x3fL

        if index < 56:
            padLen = 56 - index
        else:
            padLen = 120 - index

        padding = ['\200'] + ['\000'] * 63
        self.update(padding[:padLen])

        # Append length (before padding).
        bits = _sha_bytelist2longBigEndian(self.inputdata[:56]) + count

        self._transform(bits)

        # Store state in digest.
        digest = _sha_long2bytesBigEndian(self.H0, 4) + \
                 _sha_long2bytesBigEndian(self.H1, 4) + \
                 _sha_long2bytesBigEndian(self.H2, 4) + \
                 _sha_long2bytesBigEndian(self.H3, 4) + \
                 _sha_long2bytesBigEndian(self.H4, 4)

        self.H0 = H0 
        self.H1 = H1 
        self.H2 = H2
        self.H3 = H3
        self.H4 = H4
        self.inputdata = inputdata 
        self.count = count 

        return digest


    def hexdigest(self):
        """Terminate and return digest in HEX form.

        Like digest() except the digest is returned as a string of
        length 32, containing only hexadecimal digits. This may be
        used to exchange the value safely in email or other non-
        binary environments.
        """
        return ''.join(['%02x' % ord(c) for c in self.digest()])

    def copy(self):
        """Return a clone object. (not implemented)

        Return a copy ('clone') of the md5 object. This can be used
        to efficiently compute the digests of strings that share
        a common initial substring.
        """
        raise Exception, "not implemented"


# ======================================================================
# Mimic Python top-level functions from standard library API
# for consistency with the md5 module of the standard library.
# ======================================================================

# These are mandatory variables in the module. They have constant values
# in the SHA standard.

sha_digest_size = sha_digestsize = 20
sha_blocksize = 1

def sha_new(arg=None):
    """Return a new sha crypto object.

    If arg is present, the method call update(arg) is made.
    """

    crypto = sha()
    if arg:
        crypto.update(arg)

    return crypto


# gives the hash of a string
def sha_hash(string):
    crypto = sha()
    crypto.update(string)
    return crypto.digest()


# gives the hash of a string
def sha_hexhash(string):
    crypto = sha()
    crypto.update(string)
    return crypto.hexdigest()

#end include sha.repy
#begin include xmlrpc_client.repy
"""
<Program Name>
  xmlrpc_client.py

<Started>
  May 3, 2009

<Author>
  Michael Phan-Ba

<Purpose>
  Implements the client-side XML-RPC protocol.

"""


#begin include urlparse.repy
"""
<Program Name>
  urlparse.repy

<Started>
  May 15, 2009

<Author>
  Michael Phan-Ba

<Purpose>
  Provides utilities for parsing URLs, based on the Python 2.6.1 module urlparse.

"""


def urlparse_urlsplit(urlstring, default_scheme="", allow_fragments=True):
  """
  <Purpose>
    Parse a URL into five components, returning a dictionary.  This corresponds
    to the general structure of a URL:
    scheme://netloc/path;parameters?query#fragment.  The parameters are not
    split from the URL and individual componenets are not separated.

    Only absolute server-based URIs are currently supported (all URLs will be
    parsed into the components listed, regardless of the scheme).

  <Arguments>
    default_scheme:
      Optional: defaults to the empty string.  If specified, gives the default
      addressing scheme, to be used only if the URL does not specify one.

    allow_fragments:
      Optional: defaults to True.  If False, fragment identifiers are not
      allowed, even if the URL's addressing scheme normally does support them.

  <Exceptions>
    ValueError on parsing a non-numeric port value.

  <Side Effects>
    None.

  <Returns>
    A dictionary containing:

    Key         Value                               Value if not present
    ============================================================================
    scheme      URL scheme specifier                empty string
    netloc      Network location part               empty string
    path        Hierarchical path                   empty string
    query       Query component                     empty string
    fragment    Fragment identifier                 empty string
    username    User name                           None
    password    Password                            None
    hostname    Host name (lower case)              None
    port        Port number as integer, if present  None

  """

  components = {"scheme": default_scheme, "netloc": "", "path": "", "query": "",
    "fragment": "", "username": None, "password": None, "hostname": None,
    "port": None }

  # Extract the scheme, if present.
  (lpart, rpart) = _urlparse_splitscheme(urlstring)
  if lpart:
    components["scheme"] = lpart

  # Extract the server information, if present.
  if rpart.startswith("//"):
    (lpart, rpart) = _urlparse_splitnetloc(rpart, 2)
    components["netloc"] = lpart

    (components["username"], components["password"], components["hostname"],
      components["port"]) = _urlparse_splitauthority(lpart)

  # Extract the fragment.
  if allow_fragments:
    (rpart, components["fragment"]) = _urlparse_splitfragment(rpart)


  # Extract the query.
  (components["path"], components["query"]) = _urlparse_splitquery(rpart)

  return components


def _urlparse_splitscheme(url):
  """Parse the scheme portion of the URL"""
  # The scheme is valid only if it contains these characters.
  scheme_chars = \
    "abcdefghijklmnopqrstuvwxyz0123456789+-."

  scheme = ""
  rest = url

  spart = url.split(":", 1)
  if len(spart) == 2:

    # Normalize the scheme.
    spart[0] = spart[0].lower()

    # A scheme is valid only if it starts with an alpha character.
    if spart[0] and spart[0][0].isalpha():
      for char in spart[0]:
        if char not in scheme_chars:
          break
      (scheme, rest) = spart

  return scheme, rest


def _urlparse_splitnetloc(url, start=0):
  """Parse the netloc portion of the URL"""

  # By default, the netloc is delimited by the end of the URL.
  delim = len(url)

  # Find the left-most delimiter.
  for char in "/?#":
    xdelim = url.find(char, start)
    if xdelim >= 0:
      delim = min(delim, xdelim)

  # Return the netloc and the rest of the URL.
  return url[start:delim], url[delim:]


def _urlparse_splitauthority(netloc):
  """Parse the authority portion of the netloc"""

  # The authority can have a userinfo portion delimited by "@".
  authority = netloc.split("@", 1)

  # Default values.
  username = None
  password = None
  hostname = None
  port = None

  # Is there a userinfo portion?
  if len(authority) == 2:

    # userinfo can be split into username:password
    userinfo = authority[0].split(":", 1)

    # hostport can be split into hostname:port
    hostport = authority[1].split(":", 1)

    if userinfo[0]:
      username = userinfo[0]
    if len(userinfo) == 2:
      password = userinfo[1]

  # No userinfo portion found.
  else:

    # hostport can be split into hostname:port
    hostport = netloc.split(":", 1)

  # Is there a port value?
  if hostport[0]:
    hostname = hostport[0]
  if len(hostport) == 2:
    port = int(hostport[1], 10)

  # Return the values.
  return username, password, hostname, port


def _urlparse_splitquery(url):
  """Parse the query portion of the url"""

  qpart = url.split("?", 1)
  if len(qpart) == 2:
    query = qpart[1]
  else:
    query = ""

  return qpart[0], query


def _urlparse_splitfragment(url):
  """Parse the query portion of the url"""

  fpart = url.split("#", 1)
  if len(fpart) == 2:
    fragment = fpart[1]
  else:
    fragment = ""

  return fpart[0], fragment

#end include urlparse.repy
#begin include httpretrieve.repy
"""
<Program Name>
  httpretrieve.repy

<Started>
  August 19, 2009

<Author>
  Yafete Yemuru

<Purpose>
  Provides a method for retrieving content from web servers using the HTTP
  protocol. The content can be accessed as a file like object, or saved to
  a file or returned as a string.
"""



#begin include urlparse.repy
#already included urlparse.repy
#end include urlparse.repy
#begin include sockettimeout.repy
"""
<Author>
  Justin Cappos, Armon Dadgar
  This is a rewrite of the previous version by Richard Jordan

<Start Date>
  26 Aug 2009

<Description>
  A library that causes sockets to timeout if a recv / send call would
  block for more than an allotted amount of time.

"""

dy_import_module_symbols("librepysocket")

class SocketTimeoutError(Exception):
  """The socket timed out before receiving a response"""


class _timeout_socket():
  """
  <Purpose>
    Provides a socket like object which supports custom timeouts
    for send() and recv().
  """

  # Initialize with the socket object and a default timeout
  def __init__(self,socket,timeout=10, checkintv=0.1):
    """
    <Purpose>
      Initializes a timeout socket object.

    <Arguments>
      socket:
              A socket like object to wrap. Must support send,recv,close, and willblock.

      timeout:
              The default timeout for send() and recv().

      checkintv:
              How often socket operations (send,recv) should check if
              they can run. The smaller the interval the more time is
              spent busy waiting.
    """
    # Store the socket, timeout and check interval
    self.socket = socket
    self.timeout = timeout
    self.checkintv = checkintv


  # Allow changing the default timeout
  def settimeout(self,timeout=10):
    """
    <Purpose>
      Allows changing the default timeout interval.

    <Arguments>
      timeout:
              The new default timeout interval. Defaults to 10.
              Use 0 for no timeout. Given in seconds.

    """
    # Update
    self.timeout = timeout
  
  
  # Wrap willblock
  def willblock(self):
    """
    See socket.willblock()
    """
    return self.socket.willblock()


  # Wrap close
  def close(self):
    """
    See socket.close()
    """
    return self.socket.close()


  # Provide a recv() implementation
  def recv(self,bytes,timeout=None):
    """
    <Purpose>
      Allows receiving data from the socket object with a custom timeout.

    <Arguments>
      bytes:
          The maximum amount of bytes to read

      timeout:
          (Optional) Defaults to the value given at initialization, or by settimeout.
          If provided, the socket operation will timeout after this amount of time (sec).
          Use 0 for no timeout.

    <Exceptions>
      As with socket.recv(), socket.willblock(). Additionally, SocketTimeoutError is
      raised if the operation times out.

    <Returns>
      The data received from the socket.
    """
    # Set the timeout if None
    if timeout is None:
      timeout = self.timeout

    # Get the start time
    starttime = getruntime()

    # Block until we can read
    rblock, wblock = self.socket.willblock()
    while rblock:
      # Check if we should break
      if timeout > 0:
        # Get the elapsed time
        diff = getruntime() - starttime

        # Raise an exception
        if diff > timeout:
          raise SocketTimeoutError,"recv() timed out!"

      # Sleep
      sleep(self.checkintv)

      # Update rblock
      rblock, wblock = self.socket.willblock()

    # Do the recv
    return self.socket.recv(bytes)


  # Provide a send() implementation
  def send(self,data,timeout=None):
    """
    <Purpose>
      Allows sending data with the socket object with a custom timeout.

    <Arguments>
      data:
          The data to send

      timeout:
          (Optional) Defaults to the value given at initialization, or by settimeout.
          If provided, the socket operation will timeout after this amount of time (sec).
          Use 0 for no timeout.

    <Exceptions>
      As with socket.send(), socket.willblock(). Additionally, SocketTimeoutError is
      raised if the operation times out.

    <Returns>
      The number of bytes sent.
    """
    # Set the timeout if None
    if timeout is None:
      timeout = self.timeout

    # Get the start time
    starttime = getruntime()

    # Block until we can write
    rblock, wblock = self.socket.willblock()
    while wblock:
      # Check if we should break
      if timeout > 0:
        # Get the elapsed time
        diff = getruntime() - starttime

        # Raise an exception
        if diff > timeout:
          raise SocketTimeoutError,"send() timed out!"

      # Sleep
      sleep(self.checkintv)

      # Update rblock
      rblock, wblock = self.socket.willblock()

    # Do the recv
    return self.socket.send(data) 




def timeout_openconn(desthost, destport, localip=None, localport=None, timeout=5):
  """
  <Purpose> 
    Wrapper for openconn.   Very, very similar

  <Args>
    Same as Repy openconn

  <Exception>
    Raises the same exceptions as openconn.

  <Side Effects>
    Creates a socket object for the user

  <Returns>
    socket obj on success
  """

  realsocketlikeobject = openconn(desthost, destport, localip, localport, timeout)

  thissocketlikeobject = _timeout_socket(realsocketlikeobject, timeout)
  return thissocketlikeobject





def timeout_waitforconn(localip, localport, function, timeout=5):
  """
  <Purpose> 
    Wrapper for waitforconn.   Essentially does the same thing...

  <Args>
    Same as Repy waitforconn with the addition of a timeout argument.

  <Exceptions> 
    Same as Repy waitforconn

  <Side Effects>
    Sets up event listener which calls function on messages.

  <Returns>
    Handle to listener.
  """

  # We use a closure for the callback we pass to waitforconn so that we don't
  # have to map mainch's to callback functions or deal with potential race
  # conditions if we did maintain such a mapping. 
  def _timeout_waitforconn_callback(localip, localport, sockobj, ch, mainch):
    # 'timeout' is the free variable 'timeout' that was the argument to
    #  timeout_waitforconn.
    thissocketlikeobject = _timeout_socket(sockobj, timeout)

    # 'function' is the free variable 'function' that was the argument to
    #  timeout_waitforconn.
    return function(localip, localport, thissocketlikeobject, ch, mainch)

  return waitforconn(localip, localport, _timeout_waitforconn_callback)

  
  


# a wrapper for stopcomm
def timeout_stopcomm(commhandle):
  """
    Wrapper for stopcomm.   Does the same thing...
  """

  return stopcomm(commhandle)
  
    


#end include sockettimeout.repy
#begin include urllib.repy
def urllib_quote(string, safe="/"):
  """
  <Purpose>
    Encode a string such that it can be used safely in a URL or XML
    document.

  <Arguments>
    string:
           The string to urlencode.

    safe (optional):
           Specifies additional characters that should not be quoted --
           defaults to "/".

  <Exceptions>
    TypeError if the safe parameter isn't an enumerable.

  <Side Effects>
    None.

  <Returns>
    Urlencoded version of the passed string.
  """

  resultstr = ""

  # We go through each character in the string; if it's not in [0-9a-zA-Z]
  # we wrap it.

  safeset = set(safe)

  for char in string:
    asciicode = ord(char)
    if (asciicode >= ord("0") and asciicode <= ord("9")) or \
        (asciicode >= ord("A") and asciicode <= ord("Z")) or \
        (asciicode >= ord("a") and asciicode <= ord("z")) or \
        asciicode == ord("_") or asciicode == ord(".") or \
        asciicode == ord("-") or char in safeset:
      resultstr += char
    else:
      resultstr += "%%%02X" % asciicode

  return resultstr




def urllib_quote_plus(string, safe=""):
  """
  <Purpose>
    Encode a string to go in the query fragment of a URL.

  <Arguments>
    string:
           The string to urlencode.

    safe (optional):
           Specifies additional characters that should not be quoted --
           defaults to the empty string.

  <Exceptions>
    TypeError if the safe parameter isn't a string.

  <Side Effects>
    None.

  <Returns>
    Urlencoded version of the passed string.
  """

  return urllib_quote(string, safe + " ").replace(" ", "+")




def urllib_unquote(string):
  """
  <Purpose>
    Unquote a urlencoded string.

  <Arguments>
    string:
           The string to unquote.

  <Exceptions>
    ValueError thrown if the last wrapped octet isn't a valid wrapped octet
    (i.e. if the string ends in "%" or "%x" rather than "%xx". Also throws
    ValueError if the nibbles aren't valid hex digits.

  <Side Effects>
    None.

  <Returns>
    The decoded string.
  """

  resultstr = ""

  # We go through the string from end to beginning, looking for wrapped
  # octets. When one is found we add it (unwrapped) and the following
  # string to the resultant string, and shorten the original string.

  while True:
    lastpercentlocation = string.rfind("%")
    if lastpercentlocation < 0:
      break

    wrappedoctetstr = string[lastpercentlocation+1:lastpercentlocation+3]
    if len(wrappedoctetstr) != 2:
      raise ValueError("Quoted string is poorly formed")

    resultstr = \
        chr(int(wrappedoctetstr, 16)) + \
        string[lastpercentlocation+3:] + \
        resultstr
    string = string[:lastpercentlocation]

  resultstr = string + resultstr
  return resultstr




def urllib_unquote_plus(string):
  """
  <Purpose>
    Unquote the urlencoded query fragment of a URL.

  <Arguments>
    string:
           The string to unquote.

  <Exceptions>
    ValueError thrown if the last wrapped octet isn't a valid wrapped octet
    (i.e. if the string ends in "%" or "%x" rather than "%xx". Also throws
    ValueError if the nibbles aren't valid hex digits.

  <Side Effects>
    None.

  <Returns>
    The decoded string.
  """

  return urllib_unquote(string.replace("+", " "))




def urllib_quote_parameters(dictionary):
  """
  <Purpose>
    Encode a dictionary of (key, value) pairs into an HTTP query string or
    POST body (same form).

  <Arguments>
    dictionary:
           The dictionary to quote.

  <Exceptions>
    None.

  <Side Effects>
    None.

  <Returns>
    The quoted dictionary.
  """

  quoted_keyvals = []
  for key, val in dictionary.items():
    quoted_keyvals.append("%s=%s" % (urllib_quote(key), urllib_quote(val)))

  return "&".join(quoted_keyvals)




def urllib_unquote_parameters(string):
  """
  <Purpose>
    Decode a urlencoded query string or POST body.

  <Arguments>
    string:
           The string to decode.

  <Exceptions>
    ValueError if the string is poorly formed.

  <Side Effects>
    None.

  <Returns>
    A dictionary mapping keys to values.
  """

  keyvalpairs = string.split("&")
  res = {}

  for quotedkeyval in keyvalpairs:
    # Throw ValueError if there is more or less than one '='.
    quotedkey, quotedval = quotedkeyval.split("=")
    key = urllib_unquote_plus(quotedkey)
    val = urllib_unquote_plus(quotedval)
    res[key] = val

  return res

#end include urllib.repy



class HttpConnectionError(Exception):
  """
  Error indicating that the web server has unexpectedly dropped the
  connection.
  """




class HttpBrokenServerError(Exception):
  """
  Error indicating that the web server has sent us complete garbage instead
  of something resembling HTTP.
  """




def httpretrieve_open(url, postdata=None, querydata=None, \
    httpheaders=None, timeout=None):
  """
  <Purpose>
     Returns a file-like object that can be used to read the content from
     an HTTP server. Follows 3xx redirects.

  <Arguments>
    url:
           The URL to perform a GET or POST request on.
    postdata (optional):
           A dictionary of form data or a string to POST to the server.
           Passing a non-None value results in a POST request being sent
           to the server.
    querydata (optional):
           A dictionary of form data or a string to send as the query
           string to the server.

           If postdata is omitted, the URL is retrieved with GET. If
           both postdata and querydata are omitted, there is no query
           string sent in the request.

           For both querydata and postdata, strings are sent *unmodified*.
           This means you probably should encode them first, with
           urllib_quote().
    httpheaders (optional):
           A dictionary of supplemental HTTP request headers to add to the
           request.
    timeout (optional):
           A timeout for establishing a connection to the web server,
           sending headers, and reading the response headers.

           If excluded or None, never times out.

  <Exceptions>
    ValueError if given an invalid URL, or malformed limit or timeout
      values. This is also raised if the user attempts to call a method
      on the file-like object after closing it.

    HttpConnectionError if opening the connection fails, or if the
      connection is closed by the server before we expect.

    SocketTimeoutError if the timeout is exceeded.

    HttpBrokenServerError if the response or the Location response header
      is malformed.

  <Side Effects>
    None

  <Returns>
    Returns a file-like object which can be used to read the body of
    the response from the web server. The protocol version spoken by the
    server, status code, and response headers are available as members of
    the object.
  """

  # TODO: Make sure the timeout actually works correctly everywhere it
  # should. I'm 99% sure it's broken somewhere.

  starttime = getruntime()

  # Check if the URL is valid and get host, path, port and query
  parsedurl = urlparse_urlsplit(url)
  host = parsedurl['hostname']
  path = parsedurl['path']
  port = parsedurl.get('port')
  port = port or 80

  if parsedurl['scheme'] != 'http':
    raise ValueError("URL doesn't seem to be for the HTTP protocol.")
  if host is None:
    raise ValueError("Missing hostname.")
  if parsedurl['query'] is not None and parsedurl['query'] != "":
    raise ValueError("URL cannot include a query string.")

  # Open connection to the web server
  try:
    sock = timeout_openconn(host, port)

  except Exception, e:
    if repr(e).startswith("timeout("):
      raise HttpConnectionError("Socket timed out connecting to host/port.")
    raise

  # build an HTTP request using the given port, host, path and query
  method = "GET"
  if postdata is not None:
    method = "POST"
    if type(postdata) is dict:
      postdata = urllib_quote_parameters(postdata)
    if type(postdata) is not str:
      raise TypeError("postdata should be a dict of form data or string")
  else:
    postdata = ""

  if path == "":
    raise ValueError("Invalid path -- empty string.")
  if type(querydata) is dict:
    querydata = urllib_quote_parameters(querydata)
  if type(querydata) is str and querydata != "":
    encquerydata = "?" + querydata
  else:
    encquerydata = ""

  httpheader = method + ' ' + path + encquerydata + ' HTTP/1.0\r\n'
  if httpheaders is not None:
    if type(httpheaders) is not dict:
      raise TypeError("Expected HTTP headers as a dictionary.")
    else:
      if "Host" not in httpheaders:
        httpheader += "Host: " + host + ':' + str(port) + "\r\n"
      for key, val in httpheaders.items():
        httpheader += key + ": " + val + '\r\n'

  if method == "POST":
    httpheader += 'Content-Length: ' + str(len(postdata)) + '\r\n'
  httpheader += '\r\n'
  if method == "POST":
    httpheader += postdata

  # send HTTP request to the web server
  sock.send(httpheader)

  # receive the header lines from the web server
  if timeout is None:
    sock.settimeout(0)
  elif getruntime() - starttime >= timeout:
    raise SocketTimeoutError("Timed out")
  else:
    sock.settimeout(timeout - (getruntime() - starttime))

  headers_str = ""
  while True:
    try:
      headers_str += sock.recv(1)
      if headers_str.endswith("\r\n\r\n"):
        break
    except Exception, e:
      if str(e) == "Socket closed":
        break
      else:
        raise

  httpheaderlines = headers_str.split("\r\n")
  while httpheaderlines[-1] == "":
    httpheaderlines = httpheaderlines[:-1]

  # get the status code and status message from the HTTP response
  statusline, httpheaderlines = httpheaderlines[0], httpheaderlines[1:]
  headersplit = statusline.split(' ', 2)
  if len(headersplit) < 3:
    raise HttpBrokenServerError("Server returned garbage for HTTP response.")
  if not headersplit[0].startswith('HTTP'):
    raise HttpBrokenServerError("Server returned garbage for HTTP response.")
  statusmsg = headersplit[2]
  try:
    statusnum = int(headersplit[1])
  except ValueError, e:
    raise HttpBrokenServerError("Server returned garbage for HTTP response.")

  responseheaders = _httpretrieve_parse_responseheaders(httpheaderlines)

  if statusnum == 301 or statusnum == 302:
    # redirect to the new location via recursion
    sock.close()
    try:
      redirect_location = responseheaders["Location"][0]
    except (KeyError, IndexError), ke:
      raise HttpBrokenServerError("Server returned garbage for HTTP" + \
          " response. Redirect response missing Location header.")
    else:
      return httpretrieve_open(redirect_location)

  else:
    return _httpretrieve_filelikeobject(sock, responseheaders, \
        (headersplit[0], statusnum, statusmsg))




def httpretrieve_save_file(url, filename, querydata=None, postdata=None, \
    httpheaders=None, timeout=None):
  """
  <Purpose>
    Perform an HTTP request, and save the content of the response to a
    file.

  <Arguments>
    filename:
           The file name to save the response to.
    Other arguments:
           See documentation for httpretrieve_open().

  <Exceptions>
    This function will raise any exception raised by Repy file objects
    in opening, writing to, and closing the file.

    This function will all also raise any exception raised by
    httpretrieve_open(), for the same reasons.

  <Side Effects>
    Writes the body of the response to 'filename'.

  <Returns>
    None
  """

  httpcontent = ''
  newfile = open(filename, 'w')

  http_obj = httpretrieve_open(url, querydata=querydata, postdata=postdata, \
      httpheaders=httpheaders, timeout=timeout)

  # Read from the file-like HTTP object into our file.
  while True:
    httpcontent = http_obj.read(4096)
    if httpcontent == '':
      # we're done reading
      newfile.close()
      http_obj.close()
      break
    newfile.write(httpcontent)




def httpretrieve_get_string(url, querydata=None, postdata=None, \
    httpheaders=None, timeout=30):
  """
  <Purpose>
    Performs an HTTP request on the given URL, using POST or GET,
    returning the content of the response as a string. Uses
    httpretrieve_open.

  <Arguments>
    See httpretrieve_open.

  <Exceptions>
    See httpretrieve_open.

  <Side Effects>
    None.

  <Returns>
    Returns the body of the HTTP response (no headers).
  """

  http_obj = httpretrieve_open(url, querydata=querydata, postdata=postdata, \
      httpheaders=httpheaders, timeout=timeout)
  httpcontent = http_obj.read()
  http_obj.close()
  return httpcontent




class _httpretrieve_filelikeobject:
  # This class implements a file-like object used for performing HTTP
  # requests and retrieving responses.

  def __init__(self, sock, headers, httpstatus):
    self._sock = sock
    self._fileobjclosed = False
    self._totalcontentisreceived = False
    self._totalread = 0
    self.headers = headers
    self.httpstatus = httpstatus



  def read(self, limit=None, timeout=None):
    """
    <Purpose>
      Behaves like Python's file.read(), with the potential to raise
      additional informative exceptions.

    <Arguments>
      limit (optional):
            The maximum amount of data to read. If omitted or None, this
            reads all available data.

    <Exceptions>
      See file.read()'s documentation, as well as that of
      httpretrieve_open().

    <Side Effects>
      None.

    <Returns>
      See file.read().
    """

    if self._fileobjclosed == True:
      raise ValueError("I/O operation on closed file")

    if self._totalcontentisreceived:
      return ''

    if limit is not None:
      # Sanity check type/value of limit
      if type(limit) is not int:
        raise TypeError("Expected an integer or None for limit")
      elif limit < 0:
        raise ValueError("Expected a non-negative integer for limit")

      lefttoread = limit
    else:
      lefttoread = None

    if timeout is None:
      self._sock.settimeout(0)
    else:
      self._sock.settimeout(timeout)

    # Try to read up to limit, or until there is nothing left.
    httpcontent = ''
    while True:
      try:
        content = self._sock.recv(lefttoread or 4096)
      except Exception, e:
        if str(e) == "Socket closed":
          self._totalcontentisreceived = True
          break
        else:
          raise
      
      httpcontent += content
      self._totalread += len(content)
      if limit is not None:
        if len(content) == lefttoread:
          break
        else:
          lefttoread -= len(content)
      if content == "":
        self._totalcontentisreceived = True
        break

    return httpcontent



  def close(self):
    """
    <Purpose>
      Close the file-like object.

    <Arguments>
      None

    <Exceptions>
      None

    <Side Effects>
      Disconnects from the HTTP server.

    <Returns>
      Nothing
    """
    self._fileobjclosed = True
    try:
      self._sock.close()
    except Exception, e:
      pass # don't care




def _httpretrieve_parse_responseheaders(headerlines):
  # Parse rfc822-style headers (this could be abstracted out to an rfc822
  # library that would be quite useful for internet protocols). Returns
  # a dictionary mapping headers to arrays of values. E.g.:
  #
  # Foo: a
  # Bar:
  #   b
  # Bar: c
  #
  # Becomes: {"Foo": ["a"], "Bar": ["b", "c"]}

  i = 0
  lastheader = None
  lastheader_str = ""
  res = {}
  try:
    while True:
      # non-CRLF whitespace characters
      if headerlines[i][0] in (" ", "\t") and lastheader is not None:
        lastheader_str += headerlines[i]
      else:
        if lastheader is not None:
          if lastheader not in res:
            res[lastheader] = []
          res[lastheader].append(lastheader_str.strip())
        lastheader, lastheader_str = headerlines[i].split(":", 1)
      i += 1
      if i >= len(headerlines):
        if lastheader is not None:
          if lastheader not in res:
            res[lastheader] = []
          res[lastheader].append(lastheader_str.strip())
        break
    return res
  except IndexError, idx:
    raise HttpBrokenServerError("Server returned garbage for HTTP" + \
        " response. Bad header.")

#end include httpretrieve.repy
#begin include xmlrpc_common.repy
"""
<Program Name>
  $Id: xmlrpc_common.repy 3260 2009-12-09 18:26:31Z cemeyer $

<Started>
  April 26, 2009

<Author>
  Michael Phan-Ba

<Purpose>
  Provides common methods related to XML-RPC.

  Encoding dateTime.iso8601 are not currently supported.

<Changes>

  2009-04-26  Michael Phan-Ba  <mdphanba@gmail.com>

  * Initial release

  2009-05-24  Michael Phan-Ba  <mdphanba@gmail.com>

  * Added change log
  * Fixed base64 name error
  * Set property svn:keyword to "Id" 

"""


#begin include base64.repy
"""
<Program Name>
  $Id: base64.repy 2527 2009-07-26 22:48:38Z cemeyer $

<Started>
  April 12, 2009

<Author>
  Michael Phan-Ba

<Purpose>
  Provides data encoding and decoding as specified in RFC 3548. This
  module implements a subset of the Python module base64 interface.

  b32encode(), b32decode(), b16encode(), b16decode(), decode(),
  decodestring(), encode(), and encodestring() are not currently
  implemented.

<Changes>

  2009-04-12  Michael Phan-Ba  <mdphanba@gmail.com>

  * Initial release

  2009-05-23  Michael Phan-Ba  <mdphanba@gmail.com>

  * (b64encode, b64decode, standard_b64encode, standard_b64decode,
    urlsafe_encode, urlsafe_decode): Renamed functions with base64 prefix

  2009-05-24  Michael Phan-Ba  <mdphanba@gmail.com>

  * Set property svn:keyword to "Id" 

"""

# The Base64 for use in encoding
BASE64_ALPHABET = \
  "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

def base64_b64encode(s, altchars=None):
  """
  <Purpose>
    Encode a string using Base64.

  <Arguments>
    s:
      The string to encode.

    altchars:
      An optional string of at least length 2 (additional characters are
      ignored) which specifies an alternative alphabet for the + and /
      characters.  The default is None, for which the standard Base64
      alphabet is used.

  <Exceptions>
    None.

  <Side Effects>
    None.

  <Returns>
    The encoded string.

  """
  # Build the local alphabet.
  if altchars is None:
    base64_alphabet = BASE64_ALPHABET
  else:
    base64_alphabet = BASE64_ALPHABET[:62] + altchars

  # Change from characters to integers for binary operations.
  bytes = []
  for x in s:
    bytes.append(ord(x))

  # Encode the 8-bit words into 6-bit words.
  x6bit_words = []
  index = 0
  while True:

    # Encode the first 6 bits from three 8-bit values.
    try:
      x8bits = bytes[index]
    except IndexError:
      break
    else:
      x6bits = x8bits >> 2
      leftover_bits = x8bits & 3
      x6bit_words.append(base64_alphabet[x6bits])

    # Encode the next 8 bits.
    try:
      x8bits = bytes[index + 1]
    except IndexError:
      x6bits = leftover_bits << 4
      x6bit_words.extend([base64_alphabet[x6bits], "=="])
      break
    else:
      x6bits = (leftover_bits << 4) | (x8bits >> 4)
      leftover_bits = x8bits & 15
      x6bit_words.append(base64_alphabet[x6bits])

    # Encode the final 8 bits.
    try:
      x8bits = bytes[index + 2]
    except IndexError:
      x6bits = leftover_bits << 2
      x6bit_words.extend([base64_alphabet[x6bits], "="])
      break
    else:
      x6bits = (leftover_bits << 2) | (x8bits >> 6)
      x6bit_words.append(base64_alphabet[x6bits])
      x6bits = x8bits & 63
      x6bit_words.append(base64_alphabet[x6bits])

    index += 3

  return "".join(x6bit_words)

def base64_b64decode(s, altchars=None):
  """
  <Purpose>
    Decode a Base64 encoded string.  The decoder ignores all non
    characters not in the Base64 alphabet for compatibility with the
    Python library.  However, this introduces a security loophole in
    which covert or malicious data may be passed.

  <Arguments>
    s:
      The string to decode.

    altchars:
      An optional string of at least length 2 (additional characters are
      ignored) which specifies an alternative alphabet for the + and /
      characters.  The default is None, for which the standard Base64
      alphabet is used.

  <Exceptions>
    None.

  <Side Effects>
    TypeError on decoding error.

  <Returns>
    The decoded string.

  """
  # Build the local alphabet.
  if altchars is None:
    base64_alphabet = BASE64_ALPHABET
  else:
    base64_alphabet = BASE64_ALPHABET[:62] + altchars

  # Generate the translation maps for decoding a Base64 string.
  translate_chars = []
  for x in xrange(256):
    char = chr(x)
    translate_chars.append(char)

  # Build the strings of characters to delete.
  delete_chars = []
  for x in translate_chars:
    if x not in base64_alphabet:
      delete_chars.append(x)
  delete_chars = "".join(delete_chars)

  # Insert the 6-bit Base64 values into the translation string.
  k = 0
  for v in base64_alphabet:
    translate_chars[ord(v)] = chr(k)
    k += 1
  translate_chars = "".join(translate_chars)

  # Count the number of padding characters at the end of the string.
  num_pad = 0
  i = len(s) - 1
  while i >= 0:
    if s[i] == "=":
      num_pad += 1
    else:
      break
    i -= 1

  # Translate the string into 6-bit characters and delete extraneous
  # characters.
  s = s.translate(translate_chars, delete_chars)

  # Determine correct alignment by calculating the number of padding
  # characters needed for compliance to the specification.
  align = (4 - (len(s) & 3)) & 3
  if align == 3:
    raise TypeError("Incorrectly encoded base64 data (has 6 bits of trailing garbage)")
  if align > num_pad:
    # Technically, this isn't correctly padded. But it's recoverable, so let's
    # not care.
    pass

  # Change from characters to integers for binary operations.
  x6bit_words = []
  for x in s:
    x6bit_words.append(ord(x))
  for x in xrange(align):
    x6bit_words.append(-1)

  # Decode the 6-bit words into 8-bit words.
  bytes = []
  index = 0
  while True:

    # Work on four 6-bit quantities at a time.  End when no more data is
    # available.
    try:
      (x6bits1, x6bits2, x6bits3, x6bits4) = x6bit_words[index:index + 4]
    except ValueError:
      break

    # Save an 8-bit quantity.
    bytes.append((x6bits1 << 2) | (x6bits2 >> 4))

    # End of valid data.
    if x6bits3 < 0:
      break

    # Save an 8-bit quantity.
    bytes.append(((x6bits2 & 15) << 4) | (x6bits3 >> 2))

    # End of valid data.
    if x6bits4 < 0:
      break

    # Save an 8-bit quantity.
    bytes.append(((x6bits3 & 3) << 6) | x6bits4)

    # Next four 6-bit quantities.
    index += 4

  return "".join([chr(x) for x in bytes])

def base64_standard_b64encode(s):
  """
  <Purpose>
    Encode a string using the standard Base64 alphabet.

  <Arguments>
    s:
      The string to encode.

  <Exceptions>
    None.

  <Side Effects>
    None.

  <Returns>
    The encoded string.

  """
  return base64_b64encode(s)

def base64_standard_b64decode(s):
  """
  <Purpose>
    Decode a Base64 encoded string using the standard Base64 alphabet.

  <Arguments>
    s:
      The string to decode.

  <Exceptions>
    None.

  <Side Effects>
    TypeError on decoding error.

  <Returns>
    The decoded string.

  """
  return base64_b64decode(s)


def base64_urlsafe_b64encode(s):
  """
  <Purpose>
    Encode a string using a URL-safe alphabet, which substitutes -
    instead of + and _ instead of / in the standard Base64 alphabet.

  <Arguments>
    s:
      The string to encode.

  <Exceptions>
    None.

  <Side Effects>
    None.

  <Returns>
    The encoded string.

  """
  return base64_b64encode(s, "-_")


def base64_urlsafe_b64decode(s):
  """
  <Purpose>
    Decode a Base64 encoded string using a URL-safe alphabet, which
    substitutes - instead of + and _ instead of / in the standard Base64
    alphabet.

  <Arguments>
    s:
      The string to decode.

  <Exceptions>
    None.

  <Side Effects>
    TypeError on decoding error.

  <Returns>
    The decoded string.

  """
  return base64_b64decode(s, "-_")

#end include base64.repy
#begin include xmlparse.repy
"""
<Program Name>
  xmlparse.repy

<Started>
  April 2009

<Author>
  Conrad Meyer <cemeyer@u.washington.edu>

<Purpose>
  Provide a relatively simplistic but usable xml parsing library for
  RePy.
"""

class xmlparse_XMLParseError(Exception):
  """Exception raised when an error is encountered parsing the XML."""
  pass




class xmlparse_XMLTreeNode:
  """
  <Purpose>
    Provide a simple tree structure for XML data.

  <Exceptions>
    None.

  <Example Use>
    node = xmlparse_parse("<Some><xml><data></data></xml></Some>")
  """   


  def __init__(self, tag_name):
    self.tag_name = tag_name
    self.children = None
    self.content = None
    self.attributes = {}


  def __repr__(self):
    """Provide a pretty representation of an XML tree."""

    if self.content is not None:
      return "%s:\"%s\"" % (self.tag_name, self.content)
    else:
      return "%s:%s" % (self.tag_name, str(self.children))


  def to_string(self):
    result = "<" + self.tag_name
    for attribute_name in self.attributes.keys():
      attribute_value_escaped = \
          self.attributes[attribute_name].replace("\"", "\\\"")
      result += " " + attribute_name + "=\"" + attribute_value_escaped + "\""
    
    if self.content is None:
      result += ">"
      for childnode in self.children:
        result += childnode.to_string()
      result += "</" + self.tag_name + ">"
    else:
      if len(self.content) == 0:
        result += "/>"
      else:
        result += ">" + self.content + "</" + self.tag_name + ">"

    return result




def xmlparse_parse(data):
  """
  <Purpose>
    Parses an XML string into an xmlparse_XMLTreeNode containing the root
    item.

  <Arguments>
    data:
           The data to parse.

  <Exceptions>
    xmlparse_XMLParseError if parsing fails.

  <Side Effects>
    None.

  <Returns>
    An xmlparse_XMLTreeNode tree.
  """

  data = data.lstrip()
  if data.startswith("<?xml"):
    data = data[data.find("?>")+2:]
  
  # Well-formed XML Documents have exactly one root node
  parsed_elements = _xmlparse_parse(data)
  if len(parsed_elements) != 1:
    raise xmlparse_XMLParseError("XML response from server contained more than one root node")

  return parsed_elements[0]




def _xmlparse_read_attributes(string):
  # Returns a pair containing the dictionary of attributes and remainder
  # of the string on success; excepts on failure.

  # Q_n corresponds to the state_* constant of the same value. The starting
  # node is Q_1.
  #
  #  [ Done ]
  #     ^
  #     |
  #     | (>, /)
  #     |
  #     \--------\ 
  #              |
  #        ,-.   | v-----------------------------------\
  # space (   [ Q_1 ]                                  |
  #        `->   | ^-----------------------\ (')       |
  #              |                         |           |
  #              |                (')      |   <-.     | (")
  #              | non-space   /------->[ Q_4 ]   )    |
  #              |             |               `-'     |
  #  (space)     v     (=)     |             (other)   |
  #     /-----[ Q_2 ]------>[ Q_3 ]-------->[ Q_5 ]----/
  #     |      ^   )           |      (")    ^   )
  #     |       `-'            |              `-'
  #     |     (other)   (other)|             (other)
  #     |                      |
  #     v                      |
  #[Exception]<----------------/

  # Basically the state machine is used to read a list of attribute-pairs,
  # terminated by a '/' or '>'. Attribute pairs either look like:
  #   name='value'
  # or:
  #   name="value"
  # Single-quoted attributes can contain double-quotes, and vice-versa, but
  # single-quotes in single-quoted attributes must be escaped.
  # 
  # To do this we start in Q_1, which consumes input until we arrive at
  # something that looks like an attribute name. In Q_2 we consume characters
  # for the attribute name until it looks like the attribute name is finished.
  # In Q_3 we read a single character to determine what type of quoting is
  # used for the attribute value. In Q_4 or Q_5, we read the attribute's value
  # until the string is closed, then go back to Q_1 (saving the attribute name
  # and value into the dictionary). We decide we are done when we encounter a
  # '>' or '/' in Q_1.

  # Constant states:
  state_EXPECTING_ATTRNAME = 1
  state_READING_ATTRNAME = 2
  state_EXPECTING_ATTRVALUE = 3
  state_READING_ATTRVALUE_SINGLEQUOTE = 4
  state_READING_ATTRVALUE_DOUBLEQUOTE = 5

  current_position = 0
  current_state = 1
  current_attrname = ""
  current_attrvalue = ""
  attributes = {}

  while True:
    if current_position >= len(string):
      raise xmlparse_XMLParseError(
          "Failed to parse element attribute list -- input ran out " + \
              "before we found a closing '>' or '/'")

    current_character = string[current_position]

    if current_state == state_EXPECTING_ATTRNAME:
      if current_character.isspace():
        pass    # We stay in this state
      elif current_character == '>' or current_character == '/':
        # We're finished reading attributes
        return (attributes, string[current_position:])
      else:
        current_attrname += current_character
        current_state = state_READING_ATTRNAME

    elif current_state == state_READING_ATTRNAME:
      if current_character.isspace():
        raise xmlparse_XMLParseError(
            "Failed to parse element attribute list -- attribute " + \
                "ended unexpectedly with a space")
      elif current_character == "=":
        current_state = state_EXPECTING_ATTRVALUE
      else:
        current_attrname += current_character

    elif current_state == state_EXPECTING_ATTRVALUE:
      if current_character == '\'':
        current_state = state_READING_ATTRVALUE_SINGLEQUOTE
      elif current_character == '"':
        current_state = state_READING_ATTRVALUE_DOUBLEQUOTE
      else:
        raise xmlparse_XMLParseError(
            "Failed to parse element attribute list -- attribute " + \
                "values must be quoted")

    elif current_state == state_READING_ATTRVALUE_SINGLEQUOTE:
      if current_character == '\'':
        attributes[current_attrname] = current_attrvalue
        current_state = state_EXPECTING_ATTRNAME
        current_attrname = ""
        current_attrvalue = ""
      else:
        current_attrvalue += current_character

    elif current_state == state_READING_ATTRVALUE_DOUBLEQUOTE:
      if current_character == '"':
        attributes[current_attrname] = current_attrvalue
        current_state = state_EXPECTING_ATTRNAME
        current_attrname = ""
        current_attrvalue = ""
      else:
        current_attrvalue += current_character

    current_position += 1




def _xmlparse_node_from_string(string):
  # string:
  #   <tag attr1="value" attr2='value'>content</tag>
  # Content may be a string or a list of children nodes depending on if the
  # first non-space character is a '<' or not.

  string = string.lstrip()
  if not string.startswith("<"):
    raise xmlparse_XMLParseError("Error parsing XML -- doesn't " + \
        "start with '<'")

  string = string[1:]

  read_pos = 0
  while True:
    if read_pos >= len(string):
      raise xmlparse_XMLParseError("Error parsing XML -- parser " + \
          "ran out of input trying to read a tag")

    # The tag name is ended with a space or a closing angle-brace or
    # a "/".
    curchar = string[read_pos]
    if curchar.isspace() or curchar == ">" or curchar == "/":
      break

    read_pos += 1

  tag = string[0:read_pos]
  string = string[read_pos:]

  # Get the attribute dictionary and remaining string (which will be
  # "> ... [ inner stuff ] </[tag_name]>" or "/>" for well-formed XML).
  attributes, string = _xmlparse_read_attributes(string)

  # "Empty" elements look like: "<[tag_name] [... maybe attributes] />" and
  # not "Empty" elements look like:
  # "<[tag_name] [... maybe attributes]> [inner content] </[tag_name]>".
  empty_element = False
  if string.startswith(">"):
    string = string[1:]
  elif string.startswith("/>"):
    string = string[2:]
    empty_element = True

  xmlnode = xmlparse_XMLTreeNode(tag)
  xmlnode.attributes = attributes

  if empty_element:
    xmlnode.content = ""

  else:
    # Locate the end-boundary of the inner content of this element.
    ending_tag_position = string.rfind("</")
    if ending_tag_position < 0:
      raise xmlparse_XMLParseError("XML parse error -- could not " + \
          "locate closing tag")

    # If this elements starting and closing tag names do not match, this XML
    # is not well-formed.
    if not string.startswith("</" + tag, ending_tag_position):
      raise xmlparse_XMLParseError("XML parse error -- different " + \
          "opening / closing tags at the same nesting level")

    # If the inner content starts with another element, this element has
    # children.  Otherwise, it has content, which is just a string containing
    # the inner content.
    tag_body = string[:ending_tag_position]
    if tag_body.lstrip().startswith("<"):
      xmlnode.children = _xmlparse_parse(tag_body.lstrip())
    else:
      xmlnode.content = tag_body

  return xmlnode




def _xmlparse_find_next_tag(xmldata):
  # Finds the position of the start of the next same-level tag in this XML
  # document.

  read_position = 0
  nested_depth = 0

  original_length = len(xmldata)
  xmldata = xmldata.lstrip()
  length_difference = original_length - len(xmldata)

  # Seek to another XML tag at the same depth.
  while True:
    if xmldata.startswith("</", read_position) or \
        xmldata.startswith("/>", read_position):
      nested_depth -= 1
    elif xmldata.startswith("<", read_position):
      nested_depth += 1

    read_position += 1

    if read_position >= len(xmldata):
      return read_position + length_difference

    if nested_depth == 0:
      nexttagposition = xmldata.find("<", read_position)

      if nexttagposition < 0:
        return original_length
      else:
        return nexttagposition + length_difference




def _xmlparse_parse(xmldata):
  # Takes a raw XML stream and returns a list of XMLTreeNodes.

  nodelist = []

  while True:
    # Whitespace between tags isn't important to the content of
    # an XML document.
    xmldata = xmldata.strip()

    # Strip out XML comments.
    if xmldata.startswith("<!--"):
      commentendloc = xmldata.find("-->", 4)
      if commentendloc < 0:
        raise xmlparse_XMLParseError("XML parse error -- comment " + \
            "missing close tag ('-->')")
      xmldata = xmldata[commentendloc+3:]
      continue

    # Find the end of the current tag.
    nexttagend = _xmlparse_find_next_tag(xmldata)

    thisnode_str = xmldata[0:nexttagend]
    xmldata = xmldata[nexttagend:]

    # Parse a tag out of the string we just found.
    thisnode = _xmlparse_node_from_string(thisnode_str)
    nodelist.append(thisnode)

    if not xmldata.strip().startswith("<"):
      break

  return nodelist

#end include xmlparse.repy





class xmlrpc_common_Binary(object):
  """
  <Purpose>
    Wrapper class for base64-encoded binary data in XML-RPC requests and
    responses.  This class is used when sending and receiving binary
    data through XML-RPC.

  <Side Effects>
    None.

  <Example Use>
    blob = xmlrpc_common_Binary("\x00\x01\x00")

  """

  def __init__(self, data=""):
    """
    <Purpose>
      Create a new Binary wrapper object for use with the XML-RPC
      libraries.

    <Arguments>
      data:
        The unencoded binary data.

    <Exceptions>
      None.

    """
    self.data = data





class xmlrpc_common_Fault(ValueError):
  """
  <Purpose>
    Exception representing a XML-RPC Fault.  The exception is returned
    by the parsing functions when a XML-RPC server returns a fault.

  <Side Effects>
    None.

  <Example Use>
    raise xmlrpc_common_Fault("An error occurred", -1)

  """

  def __init__(self, message, code):
    """
    <Purpose>
      Create a new Fault exception.

    <Arguments>
      message:
        A string describing the fault.

      code:
        The integer code associated with the fault.

    <Exceptions>
      None.

    """
    self.strerror = message
    self.code = code
    ValueError.__init__(self, message)





class xmlrpc_common_Timeout(Exception):
  """
  <Purpose>
    Exception representing a normal timeout occuring.

  <Side Effects>
    None.

  <Example Use>
    raise xmlrpc_common_Timeout()

  """





class xmlrpc_common_XMLParseError(ValueError):
  """
  <Purpose>
    Exception representing an error in parsing XML-RPC data.  The
    exception is thrown when bad XML data is encountered.

  <Side Effects>
    None.

  <Example Use>
    raise xmlrpc_common_XMLParseError()

  """





class xmlrpc_common_ConnectionError(ValueError):
  """
  <Purpose>
    Exception representing an error in the connection to an XMLRPC server.
    Thrown when the server closes the connection unexpectedly.

  <Side Effects>
    None.

  <Example Use>
    raise xmlrpc_common_ConnectionError()

  """





def xmlrpc_common_call2xml(method_name, params):
  """
  <Purpose>
    Build a XML-RPC method call to send to a XML-RPC server.

  <Arguments>
    method_name:
      The method name.

    params:
      A sequence type of XML-RPC parameters.  A dictionary may also be
      passed, but the keys are ignored.

  <Exceptions>
    None.

  <Side Effects>
    None.

  <Returns>
    The XML-RPC method call string.

  """
  xml_string = ['<?xml version="1.0"?>',
    "<methodCall><methodName>%s</methodName>" % method_name,
    _xmlrpc_common_params2xml(params),
    "</methodCall>"]

  return "".join(xml_string)


def xmlrpc_common_response2xml(param):
  """
  <Purpose>
    Build a XML-RPC method response to send to a XML-RPC client.  This
    is the XML document that represents the return values or fault from
    a XML-RPC call.

  <Arguments>
    param:
      The value to be returned.

  <Exceptions>
    None.

  <Side Effects>
    None.

  <Returns>
    The XML-RPC method response string.

  """
  xml_string = ['<?xml version="1.0"?><methodResponse>',
    _xmlrpc_common_params2xml((param,)),
    "</methodResponse>"]

  return "".join(xml_string)


def xmlrpc_common_fault2xml(message, code):
  """
  <Purpose>
    Build a XML-RPC fault response to send to a XML-RPC client.  A fault
    response can occur from a server failure, an incorrectly generated
    XML request, or bad program arguments.

  <Arguments>
    message:
      A string describing the fault.

    code:
      The integer code associated with the fault.

  <Exceptions>
    None.

  <Side Effects>
    None.

  <Returns>
    The XML-RPC fault response string.

  """
  struct = {"faultCode": code, "faultString": message}
  xml_string = ['<?xml version="1.0"?><methodResponse><fault>',
    _xmlrpc_common_value2xml(struct),
    "</fault></methodResponse>"]

  return "".join(xml_string)


def _xmlrpc_common_params2xml(params):
  """
  <Purpose>
    Translate Python parameter values to XML-RPC for use in building a
    XML-RPC request or response.

  <Arguments>
    params:
      A sequence type of XML-RPC parameters.  A dictionary may also be
      passed, but the keys are ignored.

  <Exceptions>
    None.

  <Side Effects>
    None.

  <Returns>
    The XML-RPC parameters string.

  """
  if params is None or params is ():
    return ""

  xml_string = ["<params>"]

  for param in params:
    xml_string.append("<param>%s</param>" % _xmlrpc_common_value2xml(param))

  xml_string.append("</params>")

  return "".join(xml_string)


def _xmlrpc_common_value2xml(obj):
  """
  <Purpose>
    Translate a Python value to XML-RPC for use in building the params
    portion of a request or response.

  <Arguments>
    obj:
      The Python object to convert.

  <Exceptions>
    None.

  <Side Effects>
    None.

  <Returns>
    The XML-RPC value string.

  """
  object_type = type(obj)

  xml_string = ["<value>"]

  if obj is None:
    xml_string.append("<nil/>")

  elif object_type is bool:
    xml_string.append("<boolean>%d</boolean>" % int(obj))

  elif object_type in (int, long):
    xml_string.append("<int>%d</int>" % obj)

  elif object_type is float:
    xml_string.append("<double>%f</double>" % obj)

  elif object_type in (str, unicode, basestring):
    xml_string.append("<string>%s</string>" % obj)

  elif object_type in (list, tuple, xrange, set, frozenset):
    xml_string.append("<array><data>")
    for value in obj:
      xml_string.append(_xmlrpc_common_value2xml(value))
    xml_string.append("</data></array>")

  elif object_type is dict:
    xml_string.append("<struct>")
    for key, value in obj.iteritems():
      xml_string.append("<member><name>%s</name>" % key)
      xml_string.append(_xmlrpc_common_value2xml(value))
      xml_string.append("</member>")
    xml_string.append("</struct>")

  # This requires the new object inheritance model to be used. e.g. do
  #   class Foo(object): pass
  # rather than
  #   class Foo: pass
  elif object_type is xmlrpc_common_Binary:
    xml_string.append("<base64>%s</base64>" % base64_standard_b64encode(obj.data))

  else:
    raise ValueError("Marshaller: Unsupported type '%s'" % type(obj))

  xml_string.append("</value>")

  return "".join(xml_string)


def xmlrpc_common_call2python(xml):
  """
  <Purpose>
    Convert a XML-RPC method call to its Python equivalent.

    The request from a XML-RPC client is parsed into native Python
    types so that the server may use the data to execute a method, as
    appropriate.

  <Arguments>
    xml:
      The XML-RPC string to convert.

  <Exceptions>
    xmlrpc_common_XMLParseError on a XML-RPC structural parse error.
    xmlparse_XMLParseError on a general XML parse error.

  <Side Effects>
    None.

  <Returns>
    A tuple containing (1) the method name and (2) a list of the
    parameters.

  """
  xml_node = xmlparse_parse(xml)

  if xml_node.tag_name != "methodCall":
    message = "Unexpected root node: %s" % xml_node.tag_name
    raise xmlrpc_common_XMLParseError(message)
  elif xml_node.children is None:
    raise xmlrpc_common_XMLParseError("No parameters found")
  elif len(xml_node.children) > 2:
    raise xmlrpc_common_XMLParseError("Too many children for 'methodCall'")

  try:
    method_name_node = xml_node.children[0]
    if method_name_node.tag_name != "methodName":
      message = "Unexpected XML node: %s" % method_name_node.tag_name
      raise xmlrpc_common_XMLParseError(message)
    method_name = method_name_node.content
  except IndexError:
    raise xmlrpc_common_XMLParseError("No method name found")

  try:
    params = _xmlrpc_common_params2python(xml_node.children[1])
  except IndexError:
    return (method_name, ())

  if not params:
    raise xmlrpc_common_XMLParseError("No parameters found")

  return (method_name, params)


def xmlrpc_common_response2python(xml):
  """
  <Purpose>
    Convert a XML-RPC method response to its Python equivalent.

    The response from a XML-RPC server is parsed into native Python
    types so that the client may use the data as appropriate.

  <Arguments>
    xml:
      The XML-RPC string to convert.

  <Exceptions>
    xmlrpc_common_XMLParseError on a XML-RPC structural parse error.
    xmlparse_XMLParseError on a general XML parse error.

  <Side Effects>
    None.

  <Returns>
    The method results or a xmlrpc_common_Fault on reading a fault.

  """
  xml_node = xmlparse_parse(xml)

  if xml_node.tag_name != "methodResponse":
    message = "Unexpected root node: %s" % xml_node.tag_name
    raise xmlrpc_common_XMLParseError(message)
  elif xml_node.children is None:
    raise xmlrpc_common_XMLParseError("No parameters found")
  elif len(xml_node.children) > 1:
    raise xmlrpc_common_XMLParseError("Too many children for 'methodCall'")

  fault_node = xml_node.children[0]
  if fault_node.tag_name == "fault":
    if fault_node.children is None:
      raise xmlrpc_common_XMLParseError("No children found for 'fault'")
    elif len(fault_node.children) != 1:
      raise xmlrpc_common_XMLParseError("Too many children for 'fault'")
    params = _xmlrpc_common_value2python(fault_node.children[0])
    try:
      return xmlrpc_common_Fault(params["faultString"], params["faultCode"])
    except KeyError:
      raise xmlrpc_common_XMLParseError("Invalid fault object")

  try:
    params = _xmlrpc_common_params2python(xml_node.children[0])
  except KeyError:
    raise xmlrpc_common_XMLParseError("No parameters found")

  if len(params) != 1:
    raise xmlrpc_common_XMLParseError("Too many children for 'params'")

  return params[0]


def _xmlrpc_common_params2python(xml_node):
  """
  <Purpose>
    Convert XML-RPC params the Python equivalent.

    The parameters portion of a XML-RPC request or response is parsed
    into Python equivalents so that the method request and response
    parsing functions can return the relevant data.

  <Arguments>
    xml_node:
      The XML node to consider.

  <Exceptions>
    xmlrpc_common_XMLParseError on a XML-RPC structural parse error.

  <Side Effects>
    None.

  <Returns>
    The method results.

  """
  if xml_node.tag_name != "params":
    message = "Unexpected XML node: %s" % xml_node.tag_name
    raise xmlrpc_common_XMLParseError(message)

  if xml_node.children is None or len(xml_node.children) < 1:
    return []

  params = []

  for param_node in xml_node.children:
    if param_node.tag_name != "param":
      message = "Unexpected XML node: %s" % param_node.tag_name
      raise xmlrpc_common_XMLParseError(message)
    elif param_node.children is None:
      raise xmlrpc_common_XMLParseError("Unexpected empty param node")
    elif len(param_node.children) > 1:
      raise xmlrpc_common_XMLParseError("Too many children for 'param'")
    params.append(_xmlrpc_common_value2python(param_node.children[0]))

  return params


def _xmlrpc_common_value2python(xml_node):
  """
  <Purpose>
    Convert a XML-RPC value the Python equivalent.

    A XML-RPC value is converted to its Python equivalent for use in the
    parameters parser.

  <Arguments>
    xml_node:
      The XML node to consider.

  <Exceptions>
    xmlrpc_common_XMLParseError on a XML-RPC structural parse error.

  <Side Effects>
    None.

  <Returns>
    The method results.

  """

  if xml_node.tag_name not in ("value",):
    message = "Unexpected XML node: %s" % xml_node.tag_name
    raise xmlrpc_common_XMLParseError(message)

  # The values that XMLRPC can encode have an optional type-specifier.
  # If the type-specifier is not included, the data is simply a string
  # and doesn't need any other special interpretation. Additionally, there
  # is an optional <string> type specifier, but e.g. openDHT doesn't use
  # it. If xml_node.children is None here, the data lacks a type-specifying
  # tag, so it is to be interpreted as a string.
  elif xml_node.children is not None and len(xml_node.children) > 1:
    raise xmlrpc_common_XMLParseError("Too many children for 'value'")

  value_node = xml_node

  # Assume string by default, as explained earlier.
  tag = "string"
  if xml_node.children is not None:
    # If the xml specifies a type, override the default.
    value_node = xml_node.children[0]
    tag = value_node.tag_name

  # The string contents of the <value> tag (or of the type-specifying tag
  # inside <value>, if one exists).
  value = value_node.content

  if tag == "nil":
    return None

  elif tag == "boolean":
    return bool(int(value))

  elif tag in ("i4", "int"):
    return int(value)

  elif tag == "double":
    return float(value)

  elif tag == "string":
    return value

  elif tag == "array":
    if len(value_node.children) > 1:
      raise xmlrpc_common_XMLParseError("Too many children for 'array'")
    # Arrays are encoded as:  <array><data>
    #                           <value>...</value>
    #                           ...
    #                         </data></array>
    data_node = value_node.children[0]
    result = []
    if data_node.children:
      for item_node in data_node.children:
        result.append(_xmlrpc_common_value2python(item_node))
    return result

  elif tag == "struct":
    result = {}

    # Structs are encoded as: <struct>
    #                           <member><name>...</name><value>...</value></member>
    #                           ...
    #                         </struct>
    # Keys (<name>) do not contain type information, so they are strings
    # as far as XMLRPC is concerned.
    for member_node in value_node.children:
      if len(member_node.children) != 2:
        message = "Incorrect number of children for 'member'"
        raise xmlrpc_common_XMLParseError(message)

      key = member_node.children[0].content
      value = _xmlrpc_common_value2python(member_node.children[1])

      result[key] = value

    return result

  elif tag == "base64":
    return xmlrpc_common_Binary(base64_standard_b64decode(value_node.content))

  else:
    message = "Demarshaller: Unsupported value type: %s" % value_node.tag_name
    raise xmlrpc_common_XMLParseError(message)

#end include xmlrpc_common.repy


class xmlrpc_client_Client(object):
  """
  <Purpose>
    XML-RPC client implementation.

  <Side Effects>
    None.

  <Example Use>
    client = xmlrpc_client_Client("http://phpxmlrpc.sourceforge.net/server.php")
    log(client.send_request("examples.getStateName", (1,)),'\n')

  """


  USER_AGENT = "seattlelib/1.0.0"


  def __init__(self, url):
    """
    <Purpose>
      Create a new XML-RPC Client object to do RPC calls to the given
      server.

    <Arguments>
      url:
        A url containing the hostname, port, and path of the xmlrpc
        server. For example, "http://phpxmlrpc.soureforge.net/server.php".

    <Exceptions>
      None.

    """

    if not isinstance(url, (str, unicode)):
      raise ValueError("Invalid argument: url must be a URL string")

    urlcomponents = urlparse_urlsplit(url, "http", False)

    self.server_host = urlcomponents["hostname"]
    self.server_port = urlcomponents["port"] or 80
    self.server_path = urlcomponents["path"] or "/"
    if urlcomponents["query"]:
      self.server_path += "?" + urlcomponents["query"]

    if not self.server_host:
      raise ValueError("Invalid argument: url must have a valid host")


  def send_request(self, method_name, params, timeout=None):
    """
    <Purpose>
      Send a XML-RPC request to a XML-RPC server to do a RPC call.

    <Arguments>
      method_name:
        The method name.

      params:
        The method parameters.

    <Exceptions>
      socket.error on socket errors, including server timeouts.
      xmlrpc_common_Fault on a XML-RPC response fault.
      xmlrpc_common_XMLParseError on a XML-RPC structural parse error.
      xmlparse_XMLParseError on a general XML parse error.
      xmlrpc_common_ConnectionError on unexpected disconnects.
      xmlrpc_common_Timeout if the time limit is exceeded.

    <Side Effects>
      None.

    <Returns>
      The XML-RPC method return values.

    """

    starttime = getruntime()

    # Prepare the XML request.
    request_xml = xmlrpc_common_call2xml(method_name, params)

    response = httpretrieve_get_string("http://%s:%s%s" % (self.server_host, \
        self.server_port, self.server_path), postdata=request_xml, \
        timeout=timeout, httpheaders={\
        "User-Agent": self.USER_AGENT, "Content-Type": "text/xml"})

    # Timeout if the POST took too long.
    if timeout is not None and getruntime() - starttime > timeout:
      raise xmlrpc_common_Timeout()

    # Parse the XML response body into Python values.
    response_value = xmlrpc_common_response2python(response)

    # If a fault was decoded, raise the exception.
    if isinstance(response_value, xmlrpc_common_Fault):
      raise response_value

    # Otherwise, return the results.
    return response_value

#end include xmlrpc_client.repy
#begin include parallelize.repy
""" 
Author: Justin Cappos

Module: A parallelization module.   It performs actions in parallel to make it
        easy for a user to call a function with a list of tasks.

Start date: November 11th, 2008

This module is adapted from code in seash which had similar functionality.

NOTE (for the programmer using this module).   It's really important to 
write concurrency safe code for the functions they provide us.  It will not 
work to write:

def foo(...):
  mycontext['count'] = mycontext['count'] + 1

YOU MUST PUT A LOCK AROUND SUCH ACCESSES.

"""


# I use this to get unique identifiers. 
#begin include uniqueid.repy
""" 
Author: Justin Cappos

Module: A simple library that provides a unique ID for each call

Start date: November 11th, 2008

This is a really, really simple module, only broken out to avoid duplicating 
functionality.

NOTE: This will give unique ids PER FILE.   If you have multiple python 
modules that include this, they will have the potential to generate the
same ID.

"""

# This is a list to prevent using part of the user's mycontext dict
uniqueid_idlist = [0]
uniqueid_idlock = createlock()

def uniqueid_getid():
  """
   <Purpose>
      Return a unique ID in a threadsafe way

   <Arguments>
      None

   <Exceptions>
      None

   <Side Effects>
      None.

   <Returns>
      The ID (an integer)
  """

  uniqueid_idlock.acquire(True)

  # I'm using a list because I need a global, but don't want to use the 
  # programmer's dict
  myid = uniqueid_idlist[0]
  uniqueid_idlist[0] = uniqueid_idlist[0] + 1

  uniqueid_idlock.release()

  return myid



#end include uniqueid.repy



class ParallelizeError(Exception):
  """An error occurred when operating on a parallelized task"""


# This has information about all of the different parallel functions.
# The keys are unique integers and the entries look like this:
# {'abort':False, 'callfunc':callfunc, 'callargs':callargs,
# 'targetlist':targetlist, 'availabletargetpositions':positionlist,
# 'runninglist':runninglist, 'result':result}
#
# abort is used to determine if future events should be aborted.
# callfunc is the function to call
# callargs are extra arguments to pass to the function
# targetlist is the list of items to call the function with
# runninglist is used to track which events are executing
# result is a dictionary that contains information about completed function.
#    The format of result is:
#      {'exception':list of tuples with (target, exception string), 
#       'aborted':list of targets,
#       'returned':list of tuples with (target, return value)}
# 
parallelize_info_dict = {}



def parallelize_closefunction(parallelizehandle):
  """
   <Purpose>
      Clean up the state created after calling parallelize_initfunction.

   <Arguments>
      parallelizehandle:
         The handle returned by parallelize_initfunction
          

   <Exceptions>
      None

   <Side Effects>
      Will try to abort future functions if possible

   <Returns>
      True if the parallelizehandle was recognized or False if the handle is
      invalid or already closed.
  """

  # There is no sense trying to check then delete, since there may be a race 
  # with multiple calls to this function.
  try:
    del parallelize_info_dict[parallelizehandle]
  except KeyError:
    return False
  else:
    return True

    



def parallelize_abortfunction(parallelizehandle):
  """
   <Purpose>
      Cause pending events for a function to abort.   Events will finish 
      processing their current event.

   <Arguments>
      parallelizehandle:
         The handle returned by parallelize_initfunction
          

   <Exceptions>
      ParallelizeError is raised if the handle is unrecognized

   <Side Effects>
      None

   <Returns>
      True if the function was not previously aborting and is now, or False if 
      the function was already set to abort before the call.
  """

  
  try:
    if parallelize_info_dict[parallelizehandle]['abort'] == False:
      parallelize_info_dict[parallelizehandle]['abort'] = True
      return True
    else:
      return False
  except KeyError:
    raise ParallelizeError("Cannot abort the parallel execution of a non-existent handle:"+str(parallelizehandle))



def parallelize_isfunctionfinished(parallelizehandle):
  """
   <Purpose>
      Indicate if a function is finished

   <Arguments>
      parallelizehandle:
         The handle returned by parallelize_initfunction
          

   <Exceptions>
      ParallelizeError is raised if the handle is unrecognized

   <Side Effects>
      None

   <Returns>
      True if the function has finished, False if it is still has events running
  """

  
  try:
    if parallelize_info_dict[parallelizehandle]['runninglist']:
      return False
    else:
      return True
  except KeyError:
    raise ParallelizeError("Cannot get status for the parallel execution of a non-existent handle:"+str(parallelizehandle))





def parallelize_getresults(parallelizehandle):
  """
   <Purpose>
      Get information about a parallelized function

   <Arguments>
      parallelizehandle:
         The handle returned by parallelize_initfunction
          
   <Exceptions>
      ParallelizeError is raised if the handle is unrecognized

   <Side Effects>
      None

   <Returns>
      A dictionary with the results.   The format is
        {'exception':list of tuples with (target, exception string), 
         'aborted':list of targets, 'returned':list of tuples with (target, 
         return value)}
  """

  
  try:
    # I copy so that the user doesn't have to deal with the fact I may still
    # be modifying it
    return parallelize_info_dict[parallelizehandle]['result'].copy()
  except KeyError:
    raise ParallelizeError("Cannot get results for the parallel execution of a non-existent handle:"+str(parallelizehandle))



      



      


def parallelize_initfunction(targetlist, callerfunc,concurrentevents=5, *extrafuncargs):
  """
   <Purpose>
      Call a function with each argument in a list in parallel

   <Arguments>
      targetlist:
          The list of arguments the function should be called with.   Each
          argument is passed once to the function.   Items may appear in the
          list multiple times

      callerfunc:
          The function to call
 
      concurrentevents:
          The number of events to issue concurrently (default 5).   No more 
          than len(targetlist) events will be concurrently started.

      extrafuncargs:
          Extra arguments the function should be called with (every function
          is passed the same extra args).

   <Exceptions>
      ParallelizeError is raised if there isn't at least one free event.   
      However, if there aren't at least concurrentevents number of free events,
      this is not an error (instead this is reflected in parallelize_getstatus)
      in the status information.

   <Side Effects>
      Starts events, etc.

   <Returns>
      A handle used for status information, etc.
  """

  parallelizehandle = uniqueid_getid()

  # set up the dict locally one line at a time to avoid a ginormous line
  handleinfo = {}
  handleinfo['abort'] = False
  handleinfo['callfunc'] = callerfunc
  handleinfo['callargs'] = extrafuncargs
  # make a copy of target list because 
  handleinfo['targetlist'] = targetlist[:]
  handleinfo['availabletargetpositions'] = range(len(handleinfo['targetlist']))
  handleinfo['result'] = {'exception':[],'returned':[],'aborted':[]}
  handleinfo['runninglist'] = []

  
  parallelize_info_dict[parallelizehandle] = handleinfo

  # don't start more threads than there are targets (duh!)
  threads_to_start = min(concurrentevents, len(handleinfo['targetlist']))

  for workercount in range(threads_to_start):
    # we need to append the workercount here because we can't return until 
    # this is scheduled without having race conditions
    parallelize_info_dict[parallelizehandle]['runninglist'].append(workercount)
    try:
      
      def function_to_run():
        parallelize_execute_function(parallelizehandle, workercount)
        
      createthread(function_to_run)
      
    except:
      # If I'm out of resources, stop
      # remove this worker (they didn't start)
      parallelize_info_dict[parallelizehandle]['runninglist'].remove(workercount)
      if not parallelize_info_dict[parallelizehandle]['runninglist']:
        parallelize_closefunction(parallelizehandle)
        raise Exception, "No events available!"
      break
  
  return parallelizehandle
    


def parallelize_execute_function(handle, myid):
  # This is internal only.   It's used to execute the user function...

  # No matter what, an exception in me should not propagate up!   Otherwise,
  # we might result in the program's termination!
  try:

    while True:
      # separate this from below functionality to minimize scope of try block
      thetargetlist = parallelize_info_dict[handle]['targetlist']
      try:
        mytarget = thetargetlist.pop()
      except IndexError:
        # all items are gone, let's return
        return

      # if they want us to abort, put this in the aborted list
      if parallelize_info_dict[handle]['abort']:
        parallelize_info_dict[handle]['result']['aborted'].append(mytarget)

      else:
        # otherwise process this normally

        # limit the scope of the below try block...
        callfunc = parallelize_info_dict[handle]['callfunc']
        callargs = parallelize_info_dict[handle]['callargs']

        try:
          retvalue = callfunc(mytarget,*callargs)
        except Exception, e:
          # always log on error.   We need to report what happened
          parallelize_info_dict[handle]['result']['exception'].append((mytarget,str(e)))
        else:
          # success, add it to the dict...
          parallelize_info_dict[handle]['result']['returned'].append((mytarget,retvalue))


  except KeyError:
    # A KeyError is normal if they've closed the handle
    return

  except Exception, e:
    log('Internal Error: Exception in parallelize_execute_function', e, '\n')

  finally:
    # remove my entry from the list of running worker threads...
    try:
      parallelize_info_dict[handle]['runninglist'].remove(myid)
    except (ValueError, KeyError):
      pass
    

    


#end include parallelize.repy


openDHTadvertise_context = {}
openDHTadvertise_context["proxylist"] = []
openDHTadvertise_context["currentproxy"] = None
openDHTadvertise_context["serverlist"] = []
openDHTadvertise_context["serverlistlock"] = createlock()

def openDHTadvertise_announce(key, value, ttlval, concurrentevents=5, proxiestocheck=5, timeout=None):
  """
  <Purpose>
    Announce a (key, value) pair to openDHT.

  <Arguments>
    key:
            The new key the value should be stored under.

    value:
            The value to associate with the given key.

    ttlval:
            The length of time (in seconds) to persist this key <-> value
            association in DHT.

    concurrentevents:
            The number of concurrent events to use when checking for
            functional openDHT proxies. Defaults to 5.

    proxiestocheck:
            The number of openDHT proxies to check. Defaults to 5.

  <Exceptions>
    Exception if the xmlrpc server behaves erratically.

  <Side Effects>
    The key <-> value association gets stored in openDHT for a while.

  <Returns>
    None.
  """

  # JAC: Copy value because it seems that Python may otherwise garbage collect
  # it in some circumstances.   This seems to fix the problem
  value = str(value)[:]

  # convert ttl to an int
  ttl = int(ttlval)

  # If no timeout was specified, choose 10 seconds (completely arbitrary).
  if timeout is None:
    timeout = 10.0

#  print "Announce key:",key,"value:",value, "ttl:",ttl
  while True:
    # if we have an empty proxy list and no proxy, get more
    if openDHTadvertise_context["currentproxy"] == None and openDHTadvertise_context["proxylist"] == []:
      openDHTadvertise_context["proxylist"] = openDHTadvertise_get_proxy_list( \
          concurrentevents=concurrentevents, maxnumberofattempts=proxiestocheck)
      # we couldn't get any proxies
      if openDHTadvertise_context["proxylist"] == []:
        return False


    # if there isn't a proxy we should use, get one from our list
    if openDHTadvertise_context["currentproxy"] == None and openDHTadvertise_context["proxylist"] != []:
      openDHTadvertise_context["currentproxy"] = openDHTadvertise_context["proxylist"][0]
      del openDHTadvertise_context["proxylist"][0]


    # This code block is adopted from put.py from OpenDHT
    pxy = xmlrpc_client_Client(openDHTadvertise_context["currentproxy"])
    keytosend = xmlrpc_common_Binary(sha_new(str(key)).digest())
    valtosend = xmlrpc_common_Binary(value)

    try:
      pxy.send_request("put", (keytosend, valtosend, ttl, "put.py"), timeout=timeout)
      # if there isn't an exception, we succeeded
      break
    except (xmlrpc_common_ConnectionError, xmlrpc_common_Timeout):
      # Let's avoid this proxy.   It seems broken
      openDHTadvertise_context["currentproxy"] = None

  return True




def openDHTadvertise_lookup(key, maxvals=100, concurrentevents=5, proxiestocheck=5, timeout=None):
  """
  <Purpose>
    Retrieve a stored value from openDHT.

  <Arguments>
    key:
            The key the value is stored under.

    maxvals:
            The maximum number of values stored under this key to
            return to the caller.

    concurrentevents:
            The number of concurrent events to use when checking for
            functional openDHT proxies. Defaults to 5.

    proxiestocheck:
            The number of openDHT proxies to check. Defaults to 5.

  <Exceptions>
    Exception if the xmlrpc server behaves erratically.

  <Side Effects>
    None.

  <Returns>
    The value stored in openDHT at key.
  """

  # if no timeout is specified, pick 10 seconds (arbitrary value).
  if timeout is None:
    timeout = 10.0

  while True:
    # if we have an empty proxy list and no proxy, get more
    if openDHTadvertise_context["currentproxy"] == None and openDHTadvertise_context["proxylist"] == []:
      openDHTadvertise_context["proxylist"] = openDHTadvertise_get_proxy_list( \
          concurrentevents=concurrentevents, maxnumberofattempts=proxiestocheck)
      # we couldn't get any proxies
      if openDHTadvertise_context["proxylist"] == []:
        raise Exception, "Lookup failed"


    # if there isn't a proxy we should use, get one from our list
    if openDHTadvertise_context["currentproxy"] == None and openDHTadvertise_context["proxylist"] != []:
      openDHTadvertise_context["currentproxy"] = openDHTadvertise_context["proxylist"][0]
      del openDHTadvertise_context["proxylist"][0]


    # This code block is adopted from get.py from OpenDHT
    pxy = xmlrpc_client_Client(openDHTadvertise_context["currentproxy"])
    maxvalhash = int(maxvals)
    # I don't know what pm is for but I assume it's some sort of generator / 
    # running counter
    pm = xmlrpc_common_Binary("")
    keyhash = xmlrpc_common_Binary(sha_new(str(key)).digest())


    listofitems = []
    # If the proxy fails, then we will go to the next one...
    while openDHTadvertise_context["currentproxy"]:
      try:
        vals, pm = pxy.send_request("get", (keyhash, maxvalhash, pm, "get.py"), timeout=timeout)
        # if there isn't an exception, we succeeded

        # append the .data part of the items, the other bits are:
        # the ttl and hash / hash algorithm.
        for item in vals:
          listofitems.append(item.data)

        # reached the last item.  We're done!
        if pm.data == "":
          return listofitems

      except (xmlrpc_common_ConnectionError, xmlrpc_common_Timeout):
        # Let's avoid this proxy.   It seems broken
        openDHTadvertise_context["currentproxy"] = None




# check to see if a server is up and ready for OpenDHT...
def openDHTadvertise_checkserver(servername):
  # try three times.   Why three?   Arbitrary value
  for junkcount in range(3):
    s = openconn(servername, 5851, timeout=2.0)
    s.close()

  # this list is the "return value".   Add ourselves if no problems...
  openDHTadvertise_context["serverlistlock"].acquire(True)
  try:
    openDHTadvertise_context["serverlist"].append(servername)
  finally:
    openDHTadvertise_context["serverlistlock"].release()




# Loosely based on find-gateway.py from the OpenDHT project...
def openDHTadvertise_get_proxy_list(maxnumberofattempts=5, concurrentevents=5):
  """
  <Purpose>
    Gets a list of active openDHT proxies.

  <Arguments>
    maxnumberofattemps:
            Maximum number of servers to attempt to connect to.

    concurrentevents:
            Maximum number of events to use.

  <Exceptions>
    Exception if there are no servers in the server list.

  <Side Effects>
    Tries to connect to several proxies to see if they are online.

  <Returns>
    A list of openDHT approxies that appear to be up.
  """

  # populate server list
  socket = openconn('www.cs.washington.edu', 80)
  try: 
    socket.send("GET /homes/arvind/servers.txt HTTP/1.0\r\nHost: www.cs.washington.edu\r\n\r\n")
  
    body = ""
    while True:
      try:
        newdata = socket.recv(4096)
      except:
        # Server decided it is done.
        break
      if len(newdata) == 0:
        break   # Server finished sending us the response.
      body += newdata
  finally:
    socket.close()

  try:
    socket.close()
  except:
    pass

  headers, payload = body.split("\r\n\r\n", 1)
  lines = payload.split("\n")
  # throw away the header line
  lines = lines[1:]
  # get the server list
  servers = []
  for line in lines:
    if line.strip() == "":
      continue
    # The lines look like:
    # 4:	134.121.64.7:5850	planetlab2.eecs.wsu.edu
    # The third field is the server name
    servers.append(line.split()[2])

  if len(servers) == 0:
    raise Exception, "No servers in server list"

  numberofattempts = min(len(servers), maxnumberofattempts)
  serverstocheck = random_sample(servers, numberofattempts)

  # empty the server list
  openDHTadvertise_context["serverlist"] = []

  # start checking...
  parhandle = parallelize_initfunction(serverstocheck, openDHTadvertise_checkserver, concurrentevents=concurrentevents)

  # wait until all are finished
  while not parallelize_isfunctionfinished(parhandle):
    sleep(0.2)

  parallelize_closefunction(parhandle)


  retlist = []
  for serverip in openDHTadvertise_context["serverlist"]:
    # make it look like the right sort of url...
    retlist.append("http://"+serverip+":5851/")


  return retlist

#end include openDHTadvertise.repy
#begin include centralizedadvertise.repy
""" 
Author: Justin Cappos

Start Date: July 8, 2008

Description:
Advertisements to a central server (similar to openDHT)


"""

#begin include session.repy
# This module wraps communications in a signaling protocol.   The purpose is to
# overlay a connection-based protocol with explicit message signaling.   
#
# The protocol is to send the size of the message followed by \n and then the
# message itself.   The size of a message must be able to be stored in 
# sessionmaxdigits.   A size of -1 indicates that this side of the connection
# should be considered closed.
#
# Note that the client will block while sending a message, and the receiver 
# will block while recieving a message.   
#
# While it should be possible to reuse the connectionbased socket for other 
# tasks so long as it does not overlap with the time periods when messages are 
# being sent, this is inadvisable.

class SessionEOF(Exception):
  pass

sessionmaxdigits = 20

# get the next message off of the socket...
def session_recvmessage(socketobj):

  messagesizestring = ''
  # first, read the number of characters...
  for junkcount in range(sessionmaxdigits):
    currentbyte = socketobj.recv(1)

    if currentbyte == '\n':
      break
    
    # not a valid digit
    if currentbyte not in '0123456789' and messagesizestring != '' and currentbyte != '-':
      raise ValueError, "Bad message size"
     
    messagesizestring = messagesizestring + currentbyte

  else:
    # too large
    raise ValueError, "Bad message size"

  messagesize = int(messagesizestring)
  
  # nothing to read...
  if messagesize == 0:
    return ''

  # end of messages
  if messagesize == -1:
    raise SessionEOF, "Connection Closed"

  if messagesize < 0:
    raise ValueError, "Bad message size"

  data = ''
  while len(data) < messagesize:
    chunk =  socketobj.recv(messagesize-len(data))
    if chunk == '': 
      raise SessionEOF, "Connection Closed"
    data = data + chunk

  return data

# a private helper function
def session_sendhelper(socketobj,data):
  sentlength = 0
  # if I'm still missing some, continue to send (I could have used sendall
  # instead but this isn't supported in repy currently)
  while sentlength < len(data):
    thissent = socketobj.send(data[sentlength:])
    sentlength = sentlength + thissent



# send the message 
def session_sendmessage(socketobj,data):
  header = str(len(data)) + '\n'

  fulldata = header + data

  session_sendhelper(socketobj, fulldata)

  # This was used before. For some reason, it causes a "Bad Message Size"
  # failure on most queries sent over a network with realistic latency. (>5ms)
  # session_sendhelper(socketobj,header)

  # session_sendhelper(socketobj,data)




#end include session.repy
# I'll use socket timeout to prevent hanging when it takes a long time...
#begin include sockettimeout.repy
#already included sockettimeout.repy
#end include sockettimeout.repy
servername = "satya.cs.washington.edu"
serverport = 10101

def centralizedadvertise_announce(key, value, ttlval):
  # Escape commas because they have a special meaning. Encoding scheme:
  # , -> \c
  # \ -> \\
  value = value.replace("\\", "\\\\")
  value = value.replace(",", "\\c")

  sockobj = timeout_openconn(servername,serverport, timeout=10)
  try:
    session_sendmessage(sockobj, "PUT|"+str(key)+"|"+str(value)+"|"+str(ttlval))
    response = session_recvmessage(sockobj)
    if response != 'OK':
      raise Exception, "Centralized announce failed '"+response+"'"
  finally:
    # BUG: This raises an error right now if the call times out ( #260 )
    # This isn't a big problem, but it is the "wrong" exception
    sockobj.close()
  
  return True
      



def centralizedadvertise_lookup(key, maxvals=100):
  sockobj = timeout_openconn(servername,serverport, timeout=10)
  try:
    session_sendmessage(sockobj, "GET|"+str(key)+"|"+str(maxvals))
    recvdata = session_recvmessage(sockobj)
    # worked
    if recvdata.endswith('OK'):
      # Decode the values (unescape commas).
      encoded_values = recvdata[:-len('OK')].split(',')
      values = []
      for encoded_value in encoded_values:
        value = encoded_value.replace("\\c", ",")
        value = value.replace("\\\\", "\\")
        values.append(value)

      return values
    raise Exception, "Centralized lookup failed"
  finally:
    # BUG: This raises an error right now if the call times out ( #260 )
    # This isn't a big problem, but it is the "wrong" exception
    sockobj.close()
      



#end include centralizedadvertise.repy
#begin include DORadvertise.repy
"""
Author: Conrad Meyer

Start Date: Wed Dec 9 2009

Description:
Advertisements to the Digital Object Registry run by CNRI.

"""




#begin include sockettimeout.repy
#already included sockettimeout.repy
#end include sockettimeout.repy
#begin include httpretrieve.repy
#already included httpretrieve.repy
#end include httpretrieve.repy
#begin include xmlparse.repy
#already included xmlparse.repy
#end include xmlparse.repy




DORadvertise_FORM_LOCATION = "http://geni.doregistry.org/SeattleGENI/HashTable"




class DORadvertise_XMLError(Exception):
  """
  Exception raised when the XML recieved from the Digital Object Registry
  server does not match the structure we expect.
  """
  pass




class DORadvertise_BadRequest(Exception):
  """
  Exception raised when the Digital Object Registry interface indigates we
  have made an invalid request.
  """


  def __init__(self, errno, errstring):
    self.errno = errno
    self.errstring = errstring
    Exception.__init__(self, "Bad DOR request (%s): '%s'" % (str(errno), errstring))




def DORadvertise_announce(key, value, ttlval, timeout=None):
  """
  <Purpose>
    Announce a (key, value) pair to the Digital Object Registry.

  <Arguments>
    key:
            The new key the value should be stored under.

    value:
            The value to associate with the given key.

    ttlval:
            The length of time (in seconds) to persist this key <-> value
            association in DHT.

    timeout:
            The number of seconds to spend on this operation before failing
            early.

  <Exceptions>
    xmlparse_XMLParseError if the xml returned isn't parseable by xmlparse.
    DORadvertise_XMLError if the xml response structure does not correspond
      to what we expect.
    DORadvertise_BadRequest if the response indicates an error.
    Any exception httpretrieve_get_string() throws (including timeout errors).

  <Side Effects>
    The key <-> value association gets stored in openDHT for a while.

  <Returns>
    None.
  """

  post_params = {'command': 'announce', 'key': key, 'value': value,
      'lifetime': str(int(ttlval))}

  _DORadvertise_command(post_params, timeout=timeout)

  return None





def DORadvertise_lookup(key, maxvals=100, timeout=None):
  """
  <Purpose>
    Retrieve a stored value from the Digital Object Registry.

  <Arguments>
    key:
            The key the value is stored under.

    maxvals:
            The maximum number of values stored under this key to
            return to the caller.

    timeout:
            The number of seconds to spend on this operation before failing
            early.

  <Exceptions>
    xmlparse_XMLParseError if the xml returned isn't parseable by xmlparse.
    DORadvertise_XMLError if the xml response structure does not correspond
      to what we expect.
    DORadvertise_BadRequest if the response indicates an error.
    Any exception httpretrieve_get_string() throws (including timeout errors).

  <Side Effects>
    None.

  <Returns>
    The value stored in the Digital Object Registry at key.
  """

  post_params = {'command': 'lookup', 'key': key, 'maxvals': str(maxvals)}

  return _DORadvertise_command(post_params, timeout=timeout)



def _DORadvertise_command(parameters, timeout=None):
  # Internal helper function; calls the remote command, and returns
  # the results we can glean from it.

  post_result = httpretrieve_get_string(DORadvertise_FORM_LOCATION, \
      postdata=parameters, timeout=timeout, \
      httpheaders={"Content-Type": "application/x-www-form-urlencoded"})

  # Parse the result to check for success. Throw several exceptions to
  # ensure the XML we're reading makes sense.
  xmltree = xmlparse_parse(post_result)

  if xmltree.tag_name != "HashTableService":
    raise DORadvertise_XMLError(
        "Root node error. Expected: 'HashTableService', " +
        "got: '%s'" % xmltree.tag_name)

  if xmltree.children is None:
    raise DORadvertise_XMLError("Root node contains no children nodes.")

  # We expect to get an error code, an error string, and possibly some
  # values from the server.
  error_msg = ""
  error = None
  values = None

  for xmlchild in xmltree.children:
    # Read the numeric error code.
    if xmlchild.tag_name == "status" and xmlchild.content is not None:
      error = int(xmlchild.content.strip())

    # String error message (description:status as strerror:errno).
    elif xmlchild.tag_name == "description":
      error_msg = xmlchild.content

    # We found a <values> tag. Let's try and get some values.
    elif xmlchild.tag_name == "values" and xmlchild.children is not None:
      values = []
      for valuenode in xmlchild.children:
        if valuenode.tag_name != "value":
          raise DORadvertise_XMLError(
              "Child tag of <values>; expected: '<value>', got: '<%s>'" % \
                  valuenode.tag_name)

        content = valuenode.content
        if content is None:
          content = ""

        values.append(content)

  if error is not 0:
    raise DORadvertise_BadRequest(error, error_msg)

  return values

#end include DORadvertise.repy
#begin include parallelize.repy
#already included parallelize.repy
#end include parallelize.repy


# All the names of services we can support.
_advertise_all_services = ("central", "DHT", "DOR")


nodemanager_announce_context = {}
for service in _advertise_all_services:
  nodemanager_announce_context["skip" + service] = 0
  nodemanager_announce_context["previous" + service + "skip"] = 1
nodemanager_announce_context_lock = createlock()


# an exception to indicate an error occured while advertising
class AdvertiseError(Exception):
  pass




def _try_advertise_announce(args):
  # Helper function used by advertise_announce(). This is the worker process
  # run in parallel for DHT and central announces.
  which_service, key, value, ttlval, exceptions, finishedref = args

  if which_service not in _advertise_all_services:
    raise AdvertiseError("Incorrect service type used in internal function _try_advertise_announce.")

  try:
    if which_service == "central":
      centralizedadvertise_announce(key, value, ttlval)
    elif which_service == "DOR":
      DORadvertise_announce(key, value, ttlval)
    else:
      openDHTadvertise_announce(key, value, ttlval)

    finishedref[0] = True     # Signal that at least one service has finished.
    
    nodemanager_announce_context_lock.acquire(True)
    try:
      nodemanager_announce_context["previous" + which_service + "skip"] = 1
    finally:
      nodemanager_announce_context_lock.release()

  except Exception, e:
    nodemanager_announce_context_lock.acquire(True)
    try:
      exceptions[0] += 'announce error (type: ' + which_service + '): ' + str(e)
      nodemanager_announce_context["skip" + which_service] = \
          nodemanager_announce_context["previous" + which_service + "skip"] + 1
      nodemanager_announce_context["previous" + which_service + "skip"] = \
          min(nodemanager_announce_context["previous" + which_service + "skip"] * 2, 16)
    finally:
      nodemanager_announce_context_lock.release()





def advertise_announce(key, value, ttlval, concurrentevents=2, \
    graceperiod=10, timeout=60):
  """
  <Purpose>
    Announce (PUT) a value at the given key in the central advertise service,
    openDHT, or both.

  <Arguments>
    key:
            The key to store the value at.

    value:
            The value to store.

    ttlval:
            Time in seconds to persist the associated key<->value pair.
    
    concurrentevents (optional, defaults to 2):
            How many services to announce on in parallel.

    graceperiod (optional, defaults to 10):
            After this many seconds (can be a float or int type), if we have
            successfully announced on at least one service, return.

    timeout (optional, defaults to 60):
            After this many seconds (can be a float or int type), give up.

  <Exceptions>
    AdvertiseError if something goes wrong.

  <Side Effects>
    Spawns as many worker events as concurrentevents specifies, limited by the
    number of services available (currently 2).

  <Returns>
    None.
  """

  # Wrapped in an array so we can modify the reference (python strings are immutable).
  exceptions = [''] # track exceptions that occur and raise them at the end

  parallize_worksets = []
  start_time = getruntime()

  onefinished = [False]

  for service_type in _advertise_all_services:
    if nodemanager_announce_context["skip" + service_type] == 0:
      parallize_worksets.append((service_type, key, value, ttlval, \
          exceptions, onefinished))

    else:
      nodemanager_announce_context_lock.acquire(True)
      try:
        nodemanager_announce_context["skip" + service_type] = \
            nodemanager_announce_context["skip" + service_type] - 1
      finally:
        nodemanager_announce_context_lock.release()

  ph = parallelize_initfunction(parallize_worksets, _try_advertise_announce, \
      concurrentevents=concurrentevents)

  while not parallelize_isfunctionfinished(ph):
    sleep(0.1)
    if getruntime() - start_time > timeout or \
        (getruntime() - start_time > graceperiod and onefinished[0]):
      parallelize_abortfunction(ph)
      break

  # Note: closefunction() doesn't actually abort future functions like
  # it says it will.
  parallelize_closefunction(ph)

  if exceptions[0] != '':
    raise AdvertiseError, exceptions

  return None




def _try_advertise_lookup(args):
  # Helper function used by advertise_lookup(). This is the worker process
  # run in parallel for DHT and central lookups.
  which_service, key, maxvals, finishedref = args

  if which_service not in _advertise_all_services:
    raise AdvertiseError("Incorrect service type used in internal function _try_advertise_lookup.")

  try:
    if which_service == "central":
      results = centralizedadvertise_lookup(key, maxvals)
    elif which_service == "DOR":
      results = DORadvertise_lookup(key, maxvals=maxvals)
    else:
      results = openDHTadvertise_lookup(key, maxvals)

    finishedref[0] = True
    return results
  
  except Exception, e:
    return []




def advertise_lookup(key, maxvals=100, lookuptype=['central','opendht','DOR'], \
    concurrentevents=2, graceperiod=10, timeout=60):
  """
  <Purpose>
    Lookup (GET) (a) value(s) stored at the given key in the central advertise
    server, openDHT, or both.

  <Arguments>
    key:
            The key used to lookup values.

    maxvals (optional, defaults to 100):
            Maximum number of values to return.

    lookuptype (optional, defaults to ['central', 'opendht', 'DOR']):
            Which services to employ looking up values.
    
    concurrentevents (optional, defaults to 2):
            How many services to lookup on in parallel.

    graceperiod (optional, defaults to 10):
            After this many seconds (can be a float or int type), return the
            results if one service was reached successfully.

    timeout (optional, defaults to 60):
            After this many seconds (can be a float or int type), give up.

  <Exceptions>
    AdvertiseError if something goes wrong.

  <Side Effects>
    Spawns as many worker events as concurrentevents specifies, limited by the
    number of services in lookuptype.

  <Returns>
    All unique values stored at the key.
  """

  parallel_worksets = []
  start_time = getruntime()

  onefinished = [False]

  for type in lookuptype:
    if type == "central":
      parallel_worksets.append(("central", key, maxvals, onefinished))
    elif type == "DOR":
      parallel_worksets.append(("DOR", key, maxvals, onefinished))
    elif type == "opendht":
      parallel_worksets.append(("DHT", key, maxvals, onefinished))
    else:
      raise AdvertiseError("Incorrect service type '" + type + "' passed to advertise_lookup().")

  ph = parallelize_initfunction(parallel_worksets, _try_advertise_lookup, \
      concurrentevents=concurrentevents)

  while not parallelize_isfunctionfinished(ph):
    sleep(0.1)
    if getruntime() - start_time > timeout or \
        (getruntime() - start_time > graceperiod and onefinished[0]):
      parallelize_abortfunction(ph)
      break

  parallel_results = parallelize_getresults(ph)['returned']
  results = []

  for parallel_result in parallel_results:
    _, return_value = parallel_result
    results += return_value

  parallelize_closefunction(ph)

  return listops_uniq(results)

#end include advertise.repy

import misc

import threading

import servicelogger

import sys

import traceback


# The frequency of updating the advertisements
adfrequency = 300

# the TTL of those adverts
adTTL = 750

# This is how many seconds we'll wait between checks to see if there are new 
# keys that need to be advertised.
adsleepfrequency = 5

myname = None

# This dictionary holds the last time an address was advertised.   This is used
# to allow us to quickly re-advertise when a key changes.
# If the elapsed time between now and when we advertised is greater than the 
# adfrequency, we'll advertise.   
# I'll clean this up periodically using clean_advertise_dict()
# NOTE: This contains keys that are converted to strings because a dictionary
# isn't hashable!
lastadvertisedict = {}


# removes old items from the advertise dictionary.
def clean_advertise_dict():
  now = getruntime()
  # must copy because we're removing items
  for advertisekey in lastadvertisedict.copy():
    if now - lastadvertisedict[advertisekey] > adfrequency:
      # remove outdated item
      del lastadvertisedict[advertisekey]
      


class advertthread(threading.Thread):

  # Note: This will get updates from the main program because the dictionary
  # isn't a copy, but a reference to the same data structure
  addict = None


  def __init__(self, advertisementdictionary, nodekey):
    self.addict = advertisementdictionary
    self.nodekey = nodekey
    threading.Thread.__init__(self, name = "Advertisement Thread")


  def run(self):
    # Put everything in a try except block so that if badness happens, we can
    # log it before dying.
    try:
      while True:
        # remove stale items from the advertise dict.   This is important because
        # we're using membership in the dict to indicate a need to advertise
        clean_advertise_dict()

        # this list contains the keys we will advertise
        advertisekeylist = []

        # make a copy so there isn't an issue with a race
        for vesselname in self.addict.keys()[:]:

          try:
            thisentry = self.addict[vesselname].copy()
          except KeyError:
            # the entry must have been removed in the meantime.   Skip it!
            continue

          # if I advertise the vessel...
          if thisentry['advertise']:
            # add the owner key if not there already...
            if rsa_publickey_to_string(thisentry['ownerkey']) not in lastadvertisedict and thisentry['ownerkey'] not in advertisekeylist:
              advertisekeylist.append(thisentry['ownerkey'])

            # and all user keys if not there already
            for userkey in thisentry['userkeys']:
              if rsa_publickey_to_string(userkey) not in lastadvertisedict and userkey not in advertisekeylist:
                advertisekeylist.append(userkey)

            # also advertise under the node key
            advertisekeylist.append(self.nodekey)

        # now that I know who to announce to, send messages to annouce my IP and 
        # port to all keys I support
        for advertisekey in advertisekeylist:
          try:
            advertise_announce(advertisekey, str(myname), adTTL)
            # mark when we advertise
            lastadvertisedict[rsa_publickey_to_string(advertisekey)] = getruntime()
          
          # advertise errors are common so note them and move on
          except AdvertiseError, e:
            servicelogger.log('AdvertiseError occured, continuing: '+str(e))
          except Exception, e:
            servicelogger.log_last_exception(e)
            # an unexpected exception occured, exit and restart
            return
           

        # wait to avoid sending too frequently
        misc.do_sleep(adsleepfrequency)
    except Exception, e:
      exceptionstring = "[ERROR]:"
      (type, value, tb) = sys.exc_info()
    
      for line in traceback.format_tb(tb):
        exceptionstring = exceptionstring + line
  
      # log the exception that occurred.
      exceptionstring = exceptionstring + str(type)+" "+str(value)+"\n"

      servicelogger.log(exceptionstring)
      raise e





