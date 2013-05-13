"""
<author>
  Savvas Savvides

<created>
  May 2013

<description>
  Uses the parser to get a list of actions. Uses these actions to track all the
  activity pertaining to a file.

  This is meant to be a quick plugin to demonstrate the parser's usability. This 
  is not meant to be an optimal implementation
"""

import os
import sys

import parser_truss_calls
import parser_strace_calls


def print_tracked_actions(tracked_actions):
  """
    <Purpose>
      Print all the actions tracked

    <Arguments>
      tracked_actions: A list of tracked actions

    <Returns>
      None

  """
  
  for ta in tracked_actions:
    action_list = tracked_actions[ta]
    for item in action_list:
      # add indentation in all tracked actions except the open one.
      if not item.startswith("OPEN"):
        print "    ",
      print item
    print
    print





def track_path(actions, path=None):
  """
    <Purpose>
      Given a list of actions, it tracks all the activity on files. If a path is
      given, only the activity on that path will be tracked. Otherwise the
      activity on all paths will be tracked.

    <Arguments>
      actions: A list of actions from a parsed trace

      path: The path to track

    <Returns>
      tracked_actions: A list with the tracked actions

  """

  # this list will contain nested lists inside it with each nested list being a
  # tracked activity for a file
  tracked_actions = {}
  
  # maps fd to the file.
  fd_to_file = {}

  for action in actions:
    # get the name of the syscall and remove the "_syscall" part at the end.
    action_name = action[0][:action[0].find("_syscall")]
    
    if action_name == "open":
      # int open(const char *pathname, int flags, mode_t mode);
      #
      # ('open_syscall', ('syscalls2.txt', ['O_RDWR', 'O_CREAT', 'O_APPEND'], 
      #                         ['S_IWUSR', 'S_IRUSR', 'S_IWGRP']), 
      #                  (4, None))

      # get the pathname from the action
      pathname = action[1][0]

      # if we are tracking a specific path, only proceed if the pathname is the
      # one we want to track
      if path != None and pathname != path:
        continue

      # if open failed do not proceed
      if action[2][0] == -1:
        continue

      # get the fd and add it to the list of fds to track
      fd = action[2][0]

      # create a new entry in tracked ections
      tracked_actions[pathname] = []
      fd_to_file[fd] = pathname

      # track this action
      flags = action[1][1]
      tracked_actions[pathname].append("OPEN \"" + 
                      pathname + "\" flags: " + "|".join(flags))


    elif action_name == "close":
      # int close(int fd);
      # 
      # ('close_syscall', (3,), (0, None))
      # ('close_syscall', (3,), (-1, 'EBADF'))

      fd = action[1][0]
      
      if fd not in fd_to_file:
        continue

      # if close was unsuccessful do not proceed
      if action[2][0] == -1:
        continue
      
      # track this action
      tracked_actions[fd_to_file[fd]].append("CLOSE FILE")

      del fd_to_file[fd]

    elif action_name in ['creat', 'statfs', 'access', 'stat', 'link', 'unlink', 
                         'chdir', 'rmdir', 'mkdir', 'symlink']:
      path1 = action[1][0]
      
      item = ''
      dangerous = ["chmod", "link", "symlink", "unlink"]
      if action_name in dangerous:
        item = "**"
        action_name = action_name.upper()

      # track this action
      item += action_name + "\n         arguments: " + \
               str(action[1]).strip("()") + "\n         return: " + \
               str(action[2][0]) + ", " + str(action[2][1]).strip("(),")
      
      if path1 not in tracked_actions:
        tracked_actions[path1] = []
      tracked_actions[path1].append(item)


    elif action_name in ["fstatfs", "fstat", "lseek", "read", "write", "dup",
                         "dup2", "dup3", "getdents", "fcntl"]:
      fd = action[1][0]

      if fd not in fd_to_file:
        continue

      if action_name == "read":
        action_name = "**READ"
        
      # track this action
      item = action_name + "\n         arguments: " + \
               str(action[1]).strip("()") + "\n         return: " + \
               str(action[2][0]) + ", " + str(action[2][1]).strip("(),")
      tracked_actions[fd_to_file[fd]].append(item)


  return tracked_actions





if __name__ == "__main__":
  if len(sys.argv) < 2 or len(sys.argv) > 3:
    raise Exception("Please provide: trace file [file_path]")
  
  fh = open(sys.argv[1], "r")
  actions = parser_strace_calls.parse_trace(fh)
  
  if sys.argv == 3:
    tracked_actions = track_path(actions, sys.argv[2])
  else:
    tracked_actions = track_path(actions)

  print_tracked_actions(tracked_actions)