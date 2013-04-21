"""
  Author: Vjekoslav Brajkovic
 
  Start Date: May 16th, 2009
  
  Purpose: Test cases for the condition variable primitive implementation.
"""

#begin include cv.repy
"""
Author: Vjekoslav Brajkovic


Start date: May 24th, 2009

Purpose: This module provides condition variable (cv) interface.

Abstract: Conceptually a condition variable is a queue of threads, 
associated with a semaphore upon which a thread(s) may wait for some 
assertion to become true. Thus each condition variable is associated with 
some assertion. While a thread is waiting upon a condition variable, that 
thread is not considered to occupy the semaphore, and so other threads may
enter the semaphore to notify the waiting thread(s).

Thread-Safety: Safe to call notify_one()/notify_all()/wait()
concurrently. However, in case you call destroy() make sure this
is a last call for that conditional variable -- otherwise you will
receive an exception about invalid handle. 
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



cv_handle_dict = {}



def cv_create():
  """
  <Purpose>
    Create a new condition variable and return it to the user.
      
  <Precondition>
    None.
    
  <Arguments>
    None.

  <Exceptions>
    None.

  <Side Effects>
    None.

  <Returns>
    The semaphore handle. 
  """
  # An unique ID associated with the condition variable.
  new_handle = uniqueid_getid()
  
  # Waiters Semaphore is used as a simple mutex, assuring that at most
  # one function in this module is executed at any point in time.
  waiters_semaphore = semaphore_create()
  semaphore_up(waiters_semaphore)
  
  # Dispatcher Semaphore is used as a queuing mechanism for threads.
  dispatcher_semaphore = semaphore_create()
  
  # How many waiting threads do we have in queue?
  waiter_count = 0
  
  cv_handle_dict[new_handle] = {'waiters_semaphore':waiters_semaphore,
                                'dispatcher_semaphore':dispatcher_semaphore,
                                'waiter_count':waiter_count}

  return new_handle





def cv_destroy(handle):
  """
  <Purpose>
    Destroy the condition variable.
      
  <Arguments>
    handle: The condition variable handle.

  <Precondition>
    All threads waiting on this condition variable have been notified by a 
    call to notify_one or notify_all.
  
    No other function calls in this module should be called concurrently or
    after. The fact that some other function call in this module might raise 
    an exception  while the condition variable is getting destroyed implies a
    design error in client's code.
    
  <Exceptions>
    ValueError if the condition variable handle is invalid.
    
  <Side Effects>
    Undefined behavior when the second precondition is not met.

  <Returns>
    None.
  """
  try:
    
    waiters_semaphore = cv_handle_dict[handle]['waiters_semaphore']
    
    # Block all other functions from accessing the number of waiting threads.
    semaphore_down(waiters_semaphore)
  
    # Are there any threads waiting for this condition variable? If so,
    # notify the client by raising the exception. This is an exceptional 
    # state and implies a bug in client's code.
    if cv_handle_dict[handle]['waiter_count'] > 0:
      raise RuntimeError("condition variable thread queue not empty")
    
    # Now that we know that the thread queue is empty, we can safely
    # delete all internal variables.
    semaphore_destroy(cv_handle_dict[handle]['dispatcher_semaphore'])
    semaphore_destroy(cv_handle_dict[handle]['waiters_semaphore'])
    
    del cv_handle_dict[handle] 
   
  except (IndexError, KeyError, ValueError):
    raise ValueError("invalid or destroyed condition variable handle: " + str(handle)) 
 


def cv_wait(handle):
  """
  <Purpose>
    Wait for a condition.

  <Arguments>
    handle: The condition variable handle.

  <Precondition>
    None.

  <Exceptions>
    ValueError if the condition variable handle is invalid.

  <Side Effects>
    None.

  <Returns>
    None.
  """
  try:
    
    waiters_semaphore = cv_handle_dict[handle]['waiters_semaphore']  
  
    # OK, we want to wait for a condition. Signal the Writers Semaphore
    # that we want to enter a critical section, and increment the
    # number of threads that are currently waiting.
    semaphore_down(waiters_semaphore) # Begin critical section.
    cv_handle_dict[handle]['waiter_count'] = cv_handle_dict[handle]['waiter_count'] + 1
    semaphore_up(waiters_semaphore) # End critical section.
    
    # ... and wait for the condition to happen.
    semaphore_down(cv_handle_dict[handle]['dispatcher_semaphore'])

  except (IndexError, KeyError, ValueError):
    raise ValueError("invalid or destroyed condition variable handle: " + str(handle)) 



def cv_notify_one(handle):
  """
  <Purpose>
    Notify the next thread in line that the condition was met.

  <Arguments>
    handle: The condition variable handle.

  <Precondition>
    None.

  <Exceptions>
    ValueError if the condition variable handle is invalid.

  <Side Effects>
    None.

  <Returns>
    None.
  """
  try:
    
    waiters_semaphore = cv_handle_dict[handle]['waiters_semaphore']
    
    semaphore_down(waiters_semaphore) # Begin critical section.
    
    # In case there is at least one thread waiting for a condition,
    # update the number of threads waiting for that condition, and 
    # signal the change.
    if cv_handle_dict[handle]['waiter_count'] > 0:
      cv_handle_dict[handle]['waiter_count'] = cv_handle_dict[handle]['waiter_count'] - 1
      semaphore_up(cv_handle_dict[handle]['dispatcher_semaphore'])
      
    semaphore_up(waiters_semaphore) # End critical section.
  
  except (IndexError, KeyError, ValueError):
    raise ValueError("invalid or destroyed condition variable handle: " + str(handle)) 



def cv_notify_all(handle):
  """
  <Purpose>
    Notify all waiting threads that the condition was met.

  <Arguments>
    handle: The condition variable handle.

  <Precondition>
    None.

  <Exceptions>
    ValueError if the condition variable handle is invalid.

  <Side Effects>
    None.

  <Returns>
     None.
  """

  try:
    
    waiters_semaphore = cv_handle_dict[handle]['waiters_semaphore']
    
    semaphore_down(waiters_semaphore) # Begin critical section.
    
    # Cycle through all waiting threads and signal the change.
    while cv_handle_dict[handle]['waiter_count'] > 0:
      cv_handle_dict[handle]['waiter_count'] = cv_handle_dict[handle]['waiter_count'] - 1
      semaphore_up(cv_handle_dict[handle]['dispatcher_semaphore'])
      
    semaphore_up(waiters_semaphore) # End critical section.
  
  except (IndexError, KeyError, ValueError):
    raise ValueError("invalid or destroyed condition variable handle: " + str(handle))  

#end include cv.repy


  
def _cv_functor(condition, number, container):
  """
  Internal function that adds the specified number to the specified
  container only when it receives a notification for a given condition.
  """
  cv_wait(condition)
  container.append(number)





def cv_test_notify_all():
  """
  Very similar to cv_test_notify_one(). The only difference is that instead
  of calling notify_one() N times, we are doing a single notify_all() call.
  This time we are only checking to see if both containers are same in size, 
  since we know that FIFO order is preserved.
  """
  condition = cv_create()
  container = []
  limit = 5
  
  for count in range(limit):
    settimer(0.0, _cv_functor, (condition, count, container,))
  
  sleep(1)
  cv_notify_all(condition)
  sleep(1)
  
  cv_destroy(condition)
  
  if len(container) == limit:
    pass
  else:
    print "fail: notify_all failed: some threads were never executed"





if callfunc == 'initialize':
  
  cv_test_notify_all()
  
  exitall()

