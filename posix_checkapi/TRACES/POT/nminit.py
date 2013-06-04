""" 
Author: Justin Cappos

Module: Node Manager initializer.   It initializes the state needed to run the
        node manager on the local node.   This would most likely be run by the
        installer.

Start date: September 10rd, 2008

This initializes the node manager for Seattle.   It sets up the starting 
resources, creates a configuration file, etc.

The design goals of this version are to be secure, simple, and reliable (in 
that order).   

"""

# need to generate a public key
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

# need randomfloat...
import random
randomfloat = random.random


import os

import persist

# embedded here.   Is this really the right thing to do?
justinpubkey = {'e':22599311712094481841033180665237806588790054310631222126405381271924089573908627143292516781530652411806621379822579071415593657088637116149593337977245852950266439908269276789889378874571884748852746045643368058107460021117918657542413076791486130091963112612854591789518690856746757312472362332259277422867, 'n':12178066700672820207562107598028055819349361776558374610887354870455226150556699526375464863913750313427968362621410763996856543211502978012978982095721782038963923296750730921093699612004441897097001474531375768746287550135361393961995082362503104883364653410631228896653666456463100850609343988203007196015297634940347643303507210312220744678194150286966282701307645064974676316167089003178325518359863344277814551559197474590483044733574329925947570794508677779986459413166439000241765225023677767754555282196241915500996842713511830954353475439209109249856644278745081047029879999022462230957427158692886317487753201883260626152112524674984510719269715422340038620826684431748131325669940064404757120601727362881317222699393408097596981355810257955915922792648825991943804005848347665699744316223963851263851853483335699321871483966176480839293125413057603561724598227617736944260269994111610286827287926594015501020767105358832476708899657514473423153377514660641699383445065369199724043380072146246537039577390659243640710339329506620575034175016766639538091937167987100329247642670588246573895990251211721839517713790413170646177246216366029853604031421932123167115444834908424556992662935981166395451031277981021820123445253}

ivanpubkey = {'e':6481764711916916397109273726155956377656536637642807312800757546468526438704587962838968130419349372877884749341748111210223731976275154922405947360547743L, 'n':338268226945045594040102034878758444764651534167506742110546096640083709576476389210311132469953959393591066992795836386110112598793559135339292833492240869157982347822379943074587320930881739344852033537843848473043128034075489712546721364258219630002902462839364391703058991174756678850745791050455715522819926432293598770270226759125320092184546422006399480232477970392705428953893948935507551291416633551949790971970309886077216112873834384725916279080756901772364218481535522170812626810368956042592229275686877306681530987143867223127594219058268997365351814588360451088611972783470143103530508782003784668721L}

andreaspubkey = {'e':2822540257849010647923776035626629838287235702704423096484847564654414465000881225428345657955502007283165026369457182106577477435673832705387872492044591, 'n':7882973334996053142664942135950444026685861344481859933376041911948219184913053557765978471764229745595651142694669215028934939643234703102261844806689829406623921142369711977840151829485724053715028017335204594765830956122106406342326605977659034321244220740521419889555563680752118278474604590311585813615909531550891420826960367366865035282430327062985682986212519631866305528935391849319049870616965616088088569190841921248106372804406270878233331052124845608476344647222603275832610760223847946462440120107424978654173015761966334681181665203909859876981557162746876336597081684996911168277402512063104549204937}

brentpubkey = {'e':13320637419729342324775464999050861486620207563289680221497576052388175183061457679807442479774032202586062376188244107037281567734856017246126615397816987, 'n':1664580811888919290322204386558991234618254900951529532302133070531168818003858721747272149690631987748580351955990179501255913110694396600216879077732002470881341935976316877085959939004416255719683229745084259916415734451722865966223832634066289733468156160367733425804203272891858242672578795220978282904336116171736295014176775641186644943132523508056618157857119718575880947188606341972480839706601198399600225860757160583497623882064668962077040113842430719849512995440241391131732067227002145871127232717089191139600707583888074613766713552503609290793641760419007328315145998064258640100176806286961432584093}

carterpubkey = {'e':7168437282876876633529422802762647606914193494803337768799081122185700696756563786082605549299608670375696543059776847908603899996329486965226631637840087, 'n':13724582806519489309968126783922147743627863615598200511401696263542228069378681666246810044371293214491884953122564270345036227213513705482186874644188248345092250636909105502001485885529938258392160401994355515499603431204210994869079065175753824307231699145470453865619794727786444147717765876934692580725863517337863828133103123656377281294656369539247378625499431358002787792903340479787368588244936134498455457634534658784891779316675575606443982304587254557775365931820487291639088098643507354164406035353826606748832467578180697619008125509252740195069184206787138540651467518667460180512988620825126472109931}

armonpubkey = {'e':3200941279173345080519384120021978738782253369732074792477284573335223989343368779528294503375136136053581878735944057988977016652466388720005919328614569, 'n':10553235881745543965137165331102432144225249224999120640550160795651004055141451077300441253063569456659555680900071806944299541573086873371906595419171669228793899400999760006896569579804445778200967916782666825777779527057870748694361762861470028374995168134276333298069549991573308145061643966828157536009984242670282950296031461069582089864549886939538988421709037403953460736874810775713352604046647570646063851167596096553164256127741778276907048527345789544310548454829925324855330039115251074424987130126399705652571956713617760718661078219136803706956075647543263871868993131570886861669612952313210350277323}

cosminpubkey = {'e':7464313175644513168887997744670197216333000296354197242445151519761504998981125780277221724878744115700245550050922885815874909770986351004470139292347799, 'n':5166923677011039755827733929519744979819679623762854241784562417614217033545741940486526418826236364419803842179010374289699995420620924879739633685352210702672742640627499819008012778100349108343082031728623289614040677248497446845750382415953993876705269331334135372972752054447786652022051356046844517168288974483920665154285041052294863296555313446636772615755907095066673797201543950176696075209934813375579921682346075069334926946959040236649186664203325185266985125536978403971085971814812113301555195462618654824626590790622973196762839114686728486351358141165471099773851900314642876491326191107813285382101}


kyungpubkey = {'e':11982834196181141260506010180308270855680653406337235774683333408763963018095300381624627449070255932606419233872822964155179661556140871823461403280265061, 'n':4545103278803184664785828362936668880385736545505423731656699929328390307650054478885855959293582492222118379534939515534504426410706682077004338092024910139743650930741139799450460528199982343120740446388950383095882206034545454151790038610951335439728039864518669360779845402779817426625909179794068292408331048258044602531678529469780131385941771393112498888925305762431363984275516442120381279894993082998112042145269189762889863936169922236763504067652051967137198111570516536122040089214964646207252038973487224346595800354866074385496633452068631506635900294186068046269028804783935234012560912143370854322011}

whitakerpubkey = {'e':10477634680045729170740871005801335641467768434351218193273260736261663260683071190501046740023833805678163947127562567143191763342750947386321129914903107, 'n':44987427972981674752339260202819704730517012150882421722152697507846945597536877512849248015247993496568330468293075099787234124471424993175870958499015752893408423430082235375761053594777621966335657140472558698057752710295102525769733694073754884636247281190665961093377545172427190375844018444884761012112133739252122574732783030450970299506665020988579143717488684873689177064850330080994102560293739679100812859869381904410648772073797463068959999303077023921012354811367752768596219324890425280911356960190242126711549743155477658643884669817671332003188080760023501529565620306559281242446187771479563495411}

kimbrlpubkey = {'e': 12750798911637834184493527277417932326435441532475403800774448739175725604187281847686680376958704258670377931363481008581812321272598098576380537893645661L, 'n': 1694119530377438178605327756918343609642560622450587281085538055601623338006046648422430575979743420720649177376633749707999100479375160182394152499579839724683354585691974439852380416307269958137584031145136607216688365388087428373517454211196220827675163168016261083305774677889141003695384360551834830801509387290263299501085011926406888315285033360312476828837194563160330075556874587331556422111760991448002655062285927283196075326065616510803128158683903383229542721447070637697949343508170520988317745716036498936859443370187163993975449123494153595187542432453684508809154880133201690029687292976773096857649L}



# This is the public key of the person who will control most of the resources.
controllerpubkey = {'e': 1515278400394037168869631887206225761783197636247636149274740854708478416229147500580877416652289990968676310353790883501744269103521055894342395180721167L, 'n': 8811850224687278929671477591179591903829730117649785862652866020803862826558480006479605958786097112503418194852731900367494958963787480076175614578652735061071079458992502737148356289391380249696938882025028801032667062564713111819847043202173425187133883586347323838509679062142786013585264788548556099117804213139295498187634341184917970175566549405203725955179602584979965820196023950630399933075080549044334508921319264315718790337460536601263126663173385674250739895046814277313031265034275415434440823182691254039184953842629364697394327806074576199279943114384828602178957150547925812518281418481896604655037L}



offcutresourcedata ="""# BUG: How do we come up with these values dynamically?
resource cpu .002
resource memory 1000000   # 1 MiB
resource diskused 100000 # .1 MiB
resource events 2
resource filewrite 1000
resource fileread 1000 
resource filesopened 1 
resource insockets 0
resource outsockets 0
resource netsend 0
resource netrecv 0
resource loopsend 0  # would change with prompt functionality (?)
resource looprecv 0
resource lograte 100 # the monitor might log something
resource random 0    # Shouldn't generate random numbers on our own
"""

bigresourcedata = """resource cpu .08
resource memory 100000000   # 100 MiB
resource diskused 80000000 # 80 MiB
resource events 50
resource filewrite 100000
resource fileread 100000
resource filesopened 10
resource insockets 10
resource outsockets 10
resource netsend 100000
resource netrecv 100000
resource loopsend 1000000
resource looprecv 1000000
resource lograte 30000
resource random 100
resource messport 11111
resource messport 12222
resource messport 13333
resource messport 14444
resource messport 15555
resource messport 16666
resource messport 17777
resource messport 18888
resource messport 19999
resource connport 11111
resource connport 12222
resource connport 13333
resource connport 14444
resource connport 15555
resource connport 16666
resource connport 17777
resource connport 18888
resource connport 19999

call gethostbyname_ex allow
call sendmess allow
call recvmess allow
call openconn allow
call waitforconn allow
call stopcomm allow                     # it doesn't make sense to restrict
call socket.close allow                 # let's not restrict
call socket.send allow                  # let's not restrict
call socket.recv allow                  # let's not restrict

# open and file.__init__ both have built in restrictions...
call open allow                         # can read / write
call file.__init__ allow                # can read / write
call file.close allow                   # shouldn't restrict
call file.flush allow                   # they are free to use
call file.next allow                    # free to use as well...
call file.read allow                    # allow read
call file.readline allow                # shouldn't restrict
call file.readlines allow               # shouldn't restrict
call file.seek allow                    # seek doesn't restrict
call file.write allow                   # shouldn't restrict (open restricts)
call file.writelines allow              # shouldn't restrict (open restricts)
call sleep allow                        # harmless
call settimer allow                     # we can't really do anything smart
call canceltimer allow                  # should be okay
call exitall allow                      # should be harmless 

call log.write allow
call log.writelines allow
call getmyip allow                      # They can get the external IP address
call listdir allow                      # They can list the files they created
call removefile allow                   # They can remove the files they create
call randomfloat allow                  # can get random numbers
call getruntime allow                   # can get the elapsed time
call getlock allow                      # can get a mutex
"""

smallresourcedata = """resource cpu .02
resource memory 30000000   # 30 MiB
resource diskused 20000000 # 20 MiB
resource events 15
resource filewrite 100000
resource fileread 100000
resource filesopened 5
resource insockets 5
resource outsockets 5
resource netsend 10000
resource netrecv 10000
resource loopsend 1000000
resource looprecv 1000000
resource lograte 30000
resource random 100
resource messport %s
resource messport %s
resource messport %s
resource messport %s
resource connport %s
resource connport %s
resource connport %s
resource connport %s

call gethostbyname_ex allow
call sendmess allow
call recvmess allow
call openconn allow
call waitforconn allow
call stopcomm allow                     # it doesn't make sense to restrict
call socket.close allow                 # let's not restrict
call socket.send allow                  # let's not restrict
call socket.recv allow                  # let's not restrict

# open and file.__init__ both have built in restrictions...
call open allow                         # can read / write
call file.__init__ allow                # can read / write
call file.close allow                   # shouldn't restrict
call file.flush allow                   # they are free to use
call file.next allow                    # free to use as well...
call file.read allow                    # allow read
call file.readline allow                # shouldn't restrict
call file.readlines allow               # shouldn't restrict
call file.seek allow                    # seek doesn't restrict
call file.write allow                   # shouldn't restrict (open restricts)
call file.writelines allow              # shouldn't restrict (open restricts)
call sleep allow                        # harmless
call settimer allow                     # we can't really do anything smart
call canceltimer allow                  # should be okay
call exitall allow                      # should be harmless 

call log.write allow
call log.writelines allow
call getmyip allow                      # They can get the external IP address
call listdir allow                      # They can list the files they created
call removefile allow                   # They can remove the files they create
call randomfloat allow                  # can get random numbers
call getruntime allow                   # can get the elapsed time
call getlock allow                      # can get a mutex
"""





def make_vessel(vesselname, pubkey, resourcetemplate, resourceargs):
  retdict = {'userkeys':[], 'ownerkey':pubkey, 'oldmetadata':None, 'stopfilename':vesselname+'.stop', 'logfilename':vesselname+'.log', 'statusfilename':vesselname+'.status', 'resourcefilename':'resource.'+vesselname, 'advertise':True, 'ownerinformation':'', 'status':'Fresh'}

  try:
    WindowsError

  except NameError: # not on windows...
    # make the vessel dirs...
    try:
      os.mkdir(vesselname)
    except OSError,e:
      if e[0] == 17:
        # directory exists
        pass
      else:
        raise

  else: # on Windows...

    # make the vessel dirs...
    try:
      os.mkdir(vesselname)
    except (OSError,WindowsError),e:
      if e[0] == 17 or e[0] == 183:
        # directory exists
        pass
      else:
        raise


  #### write the vessel's resource file...
  outfo = open(retdict['resourcefilename'],"w")
  # write the args into the resource data template
  outfo.write(resourcetemplate % resourceargs)
  outfo.close()
  
  return retdict



# lots of little things need to be initialized...   
def initialize_state():

  # initialize my configuration file.   This involves a few variables:
  #    pollfrequency --  the amount of time to sleep after a check when "busy
  #                      waiting".   This trades CPU load for responsiveness.
  #    ports         --  the ports the node manager could listen on.
  #    publickey     --  the public key used to identify the node...
  #    privatekey    --  the corresponding private key for the node...
  configuration = {}

  configuration['pollfrequency'] = 1.0

  # NOTE: I chose these randomly (they will be uniform across all NMs)...   
  # Was this wise?
  configuration['ports'] = [1224, 2888, 9625, 10348, 39303, 48126, 52862, 57344, 64310]

  print "Generating key..."
  keys = rsa_gen_pubpriv_keys(100)
  configuration['publickey'] = keys[0]
  configuration['privatekey'] = keys[1]
  configuration['service_vessel'] = 'v2'

  print "Writing config file..."
  # write the config file...
  persist.commit_object(configuration,"nodeman.cfg")

  # write the offcut file...
  outfo = open("resources.offcut","w")
  outfo.write(offcutresourcedata)
  outfo.close()

#  vessel1 = make_vessel('v1',controllerpubkey,bigresourcedata, []) 
  vessel1 = make_vessel('v1',controllerpubkey,smallresourcedata, ('12345','12346', '12347','12348','12345','12346','12347','12348')) 
  vessel2 = make_vessel('v2',justinpubkey,smallresourcedata, ('20000','20001', '20002','20003','20000','20001','20002','20003')) 
  vessel3 = make_vessel('v3',ivanpubkey,smallresourcedata, ('30000','30001', '30002','30003','30000','30001','30002','30003')) 
  vessel4 = make_vessel('v4',andreaspubkey,smallresourcedata, ('21000','21001', '21002','21003','21000','21001','21002','21003')) 
  vessel5 = make_vessel('v5',brentpubkey,smallresourcedata, ('22000','22001', '22002','22003','22000','22001','22002','22003')) 
  vessel6 = make_vessel('v6',carterpubkey,smallresourcedata, ('23000','23001', '23002','23003','23000','23001','23002','23003')) 
  vessel7 = make_vessel('v7',armonpubkey,smallresourcedata, ('24000','24001', '24002','24003','24000','24001','24002','24003')) 
  vessel8 = make_vessel('v8',cosminpubkey,smallresourcedata, ('25000','25001', '25002','25003','25000','25001','25002','25003')) 
  vessel9 = make_vessel('v9',kimbrlpubkey,smallresourcedata, ('26000','26001', '26002','26003','26000','26001','26002','26003')) 
  vessel10 = make_vessel('v10',whitakerpubkey,smallresourcedata, ('27000','27001', '27002','27003','27000','27001','27002','27003')) 
  

  vesseldict = {'v1':vessel1, 'v2':vessel2, 'v3':vessel3, 'v4':vessel4, 'v5':vessel5, 'v6':vessel6, 'v7':vessel7, 'v8':vessel8, 'v9':vessel9, 'v10':vessel10}

  print "Writing vessel dictionary..."
  # write out the vessel dictionary...
  persist.commit_object(vesseldict,"vesseldict")










if __name__ == '__main__':
  initialize_state() 

