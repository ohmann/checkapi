"""
<author>
  Savvas Savvides

<created>
  May 2013

<description>
  Uses the parser to get a list of actions. Examines actions that contain a path
  and constructs the fs hierarchy of all files that exist.

  This program aims for simplicity, not efficiency.

  This is meant to be a quick plugin to demonstrate the parser's usability. This 
  is not meant to be an optimal implementation
"""

import os
import sys

import parser_truss_calls
import parser_strace_calls


def print_fs_hierarchy(hierarchy, depth, path):
  """
    <Purpose>
      A recursive functin used to print the given hierarchy

    <Arguments>
      hierarchy: A dictionary representing the hierarchy.

    <Returns>
      None

  """

  # first print current path part
  print "    " * (depth),
  print path
  
  children = []
  if path in hierarchy:
    children = hierarchy[path]
    children.sort()
  
  for child in children:
    print_fs_hierarchy(hierarchy, depth+1, child)


def construct_hierarchy(paths, start):
  """
    <Purpose>
      Given a list of paths, construct and return their hierarchy

    <Arguments>
      paths: A list of paths

    <Returns>
      hierarchy: a dictionary with the hierarchy.

  """
  hierarchy = {}

  # first add the root
  hierarchy[start] = []

  for path in paths:
    # get the parts of the path
    parts = path.strip("./").split("/")

    parts = filter(None, parts)

    for part_index in range(len(parts)):
      # get the preceding part
      if part_index == 0:
        pre = start
      else:
        pre = "/" + "/".join(parts[:part_index])
      
      current_path = "/" + "/".join(parts[:part_index+1])

      # add current path to the list of the preceding part
      if current_path not in hierarchy[pre]:
        hierarchy[pre].append(current_path)

      # create an entry for the current part
      if current_path not in hierarchy:
        hierarchy[current_path] = []

  return hierarchy


def extract_paths(actions):
  """
    <Purpose>
      Given a list of actions, it extracts all the absolute and relative paths
      from all the actions.

    <Arguments>
      actions: A list of actions from a parsed trace

    <Returns>
      absolute_paths: a list with all absolute paths extracted from the actions
      relative_paths: a list with all relative paths extracted from the actions

  """

  absolute_paths = []
  relative_paths = []

  actions_with_path = ['open', 'creat', 'statfs', 'access', 'stat', 
                        'link', 'unlink', 'chdir', 'rmdir', 'mkdir']

  for action in actions:
    # get the name of the syscall and remove the "_syscall" part at the end.
    action_name = action[0][:action[0].find("_syscall")]
    
    # we only care about actions containing paths
    if action_name not in actions_with_path:
      continue

    # we only care about paths that exist
    action_result = action[2]
    if action_result == (-1, 'ENOENT'):
      continue

    path = action[1][0]

    if path.startswith("/"):
      if path not in absolute_paths:
        absolute_paths.append(path)
    else:
      if path not in relative_paths:
        relative_paths.append(path)

    # get the second path of link
    if action_name == "link":
      path = action[1][1]

      if path.startswith("/"):
        if path not in absolute_paths:
          absolute_paths.append(path)
      else:
        if path not in relative_paths:
          relative_paths.append(path)


  return absolute_paths, relative_paths





if __name__ == "__main__":
  if len(sys.argv) != 2:
    raise Exception("Please provide: trace file")
  
  fh = open(sys.argv[1], "r")
  actions = parser_strace_calls.parse_trace(fh)
  
  absolute_paths, relative_paths = extract_paths(actions)

  absolute_hierarchy = construct_hierarchy(absolute_paths, "/")
  print_fs_hierarchy(absolute_hierarchy, depth=0, path="/")

  print

  relative_hierarchy = construct_hierarchy(relative_paths, ".")
  print_fs_hierarchy(relative_hierarchy, depth=0, path=".")

  print