"""
  Author: Justin Cappos
 
  Start Date: May 16th, 2009

  Description: Basic tests for the semaphore library...
"""

#begin include semaphore.repy
"""
Author: Justin Cappos


Start date: May 15th, 2009

Purpose: A simple library that provides a semaphore abstration on top of repy's locks...
"""

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


# this dictionary stores private data about the semaphores.   The format of an
# entry is: {'semcount' = 0, 'blockedlist' = [], 'semlock'=createlock()}.
# semcount is the number of nodes that can do a down before it blocks.   
# blockedlist is the set of nodes that are already blocked.   
# it will never be true that 'semcount' > 0  AND 'blockedlist' != []
semaphore_handle_dict = {}

def semaphore_create():
  """
   <Purpose>
      Create a new semaphore and return it to the user.   

   <Arguments>
      None

   <Exceptions>
      None

   <Side Effects>
      None.

   <Returns>
      The semaphore handle 
  """
  thissemhandle = uniqueid_getid()
  newlock = createlock()
  semaphore_handle_dict[thissemhandle] = {'semcount':0, 'blockedlist':[], 
        'semlock':newlock}

  return thissemhandle




def semaphore_destroy(semaphorehandle):
  """
   <Purpose>
      Clean up a semaphore that is no longer needed.   All currently blocked 
      threads will be unblocked.   All future uses of the semaphore will fail.

   <Arguments>
      semaphorehandle:   The semaphore handle to destroy

   <Exceptions>
      None

   <Side Effects>
      None.

   <Returns>
      True if it cleaned up the semaphore handle, False if the handle was 
      already cleaned up
  """

  # Acquire the lock.   If this fails, assume the semaphore has already been 
  # cleaned up
  try:
    # I intentionally index both of these so that if the handle is removed by
    # another call to semaphore_destroy in the mean time.   All calls that
    # acquire the lock need to do this.
    semaphore_handle_dict[semaphorehandle]['semlock'].acquire(True)
  except (IndexError, KeyError):
    return False

  # NOTE: We will release all parties that are blocking on the semaphore...   
  # Is this the right thing to do?
  for blockedthreadlock in semaphore_handle_dict[semaphorehandle]['blockedlist']:
    blockedthreadlock.release()
  
  # I need to get (and release) the lock so that I can unblock anyone waiting 
  # to modify the semaphore.   (They will then get an error)
  mylock = semaphore_handle_dict[semaphorehandle]['semlock']
  del semaphore_handle_dict[semaphorehandle]


  return True
  
  



def semaphore_up(semaphorehandle):
  """
   <Purpose>
      Increment a sempahore (possibly unblocking a thread)

   <Arguments>
      semaphorehandle:   The semaphore handle

   <Exceptions>
      ValueError if the semaphorehandle is invalid.

   <Side Effects>
      None.

   <Returns>
      None
  """

  try:
    # I intentionally index both of these so that if the handle is removed by
    # another call to semaphore_destroy in the mean time.   All calls that
    # acquire the lock need to do this.
    semaphore_handle_dict[semaphorehandle]['semlock'].acquire(True)
  except (IndexError, KeyError):
    raise ValueError("Invalid or destroyed semaphore handle")

  # If someone is blocked, then release the first one
  if semaphore_handle_dict[semaphorehandle]['blockedlist']:

    assert(semaphore_handle_dict[semaphorehandle]['semcount'] == 0)

    thefirstblockedthread = semaphore_handle_dict[semaphorehandle]['blockedlist'].pop(0)
    thefirstblockedthread.release()

  else:
    # If no one is blocked, instead increment the count...
    semaphore_handle_dict[semaphorehandle]['semcount'] = semaphore_handle_dict[semaphorehandle]['semcount'] + 1

  semaphore_handle_dict[semaphorehandle]['semlock'].release()
  





def semaphore_down(semaphorehandle):
  """
   <Purpose>
      Decrement a sempahore (possibly blocking this thread)

   <Arguments>
      semaphorehandle:   The semaphore handle

   <Exceptions>
      ValueError if the semaphorehandle is invalid.

   <Side Effects>
      None.

   <Returns>
      None.
  """
  try:
    # I intentionally index both of these so that if the handle is removed by
    # another call to semaphore_destroy in the mean time.   All calls that
    # acquire the lock need to do this.
    semaphore_handle_dict[semaphorehandle]['semlock'].acquire(True)
  except (IndexError, KeyError):
    raise ValueError("Invalid or destroyed semaphore handle")

  # If the semaphore count is 0, we should block.   The list is a queue, so 
  # we should append a lock for ourselves to the end.
  if semaphore_handle_dict[semaphorehandle]['semcount'] == 0:

    # get a lock for us and do an acquire so that the next acquire will block.
    mylock = createlock()
    mylock.acquire(True)

    semaphore_handle_dict[semaphorehandle]['blockedlist'].append(mylock)

    # release the semaphore lock...
    semaphore_handle_dict[semaphorehandle]['semlock'].release()
    
    # acquire my lock...   (someone who does an up or destroy will release us)
    mylock.acquire(True)

  else:
    # Since the count is > 0, we should decrement
    semaphore_handle_dict[semaphorehandle]['semcount'] = semaphore_handle_dict[semaphorehandle]['semcount'] - 1

    # release the semaphore lock...
    semaphore_handle_dict[semaphorehandle]['semlock'].release()
  


#end include semaphore.repy


# I use this to know when all threads have exited...

mycontext['countlist'] = []

def blockingchild(mynumber,sem):
  mycontext['countlist'].append(mynumber)
  try:
    semaphore_down(sem)
  except ValueError:
    print "It took more than 1 second to start a thread and do a down...   "
    print "This isn't technically wrong, but is suspicious"

  mycontext['countlist'].pop()
  if mycontext['countlist'] == []:
    # if this was the last element then exit...
    exitall()

 
def timedout():
  print "Timed out!"
  exitall()

if callfunc == 'initialize':

  # prevent this from hanging...
  settimer(10, timedout,())

  sem1 = semaphore_create()

  children = 5

  # start some number of children
  for num in range(children):
    settimer(0.0, blockingchild,(num, sem1))

  # wait for the children to start and block...
  while len(mycontext['countlist']) != children:
    sleep(.1)

  # destroy the semaphore.   The children should be released...
  semaphore_destroy(sem1)

  sleep(5)
  print "Error, a child should have caused us to exit..."
  exitall() 

  

