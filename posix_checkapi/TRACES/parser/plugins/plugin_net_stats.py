"""
<author>
  Savvas Savvides

<created>
  May 2013

<description>
  Uses the parser to get a list of actions and uses these actions to discover
  networks statistics.

  This is meant to be a quick plugin to demonstrate the parser's usability. This 
  is not meant to be an optimal implementation
"""

import os
import sys

import parser_truss_calls
import parser_strace_calls

stats = {"sends":0, "send_buf":0, "send_data":0, "send_errs":0, 
         "recvs":0, "recv_buf":0, "recv_data":0, "recv_errs":0}
send_err_labels = {}
send_families = {}
recv_err_labels = {}
recv_families = {}

sockets = {}
accepts = {}


def print_net_stats():
  """
    <Purpose>
      Print all network statistics

    <Arguments>
      None

    <Returns>
      None
  """
  print "- Total number of send syscalls:                 ", stats["sends"]
  if stats["sends"] > 0:
    print "- average buffer size per send syscall: ", (stats["send_buf"] / stats["sends"])
    print "- average data sent per send syscall:   ", (stats["send_data"] / stats["sends"])
    print
    print "Number of socket families used:"
    for fam in send_families:
      print "    ", fam, ":", send_families[fam]
    print
    print "Number of send errors:"
    if len(send_err_labels) == 0:
      print "    None"
    else:
      for err in send_err_labels:
        print "    ", err, ": ", send_err_labels[err]

  print
  print "- Total number of recv syscalls:                     ", stats["recvs"]
  if stats["recvs"] > 0:
    print "- average buffer size per recv syscall: ", (stats["recv_buf"] / stats["recvs"])
    print "- average data received per recv syscall:   ", (stats["recv_data"] / stats["recvs"])
    print
    print "Number of socket families used:"
    for fam in recv_families:
      print "    ", fam, ":", recv_families[fam]
    print
    print "Number of recv errors:"
    if len(recv_err_labels) == 0:
      print "    None"
    else:
      for err in recv_err_labels:
        print "    ", err, ": ", recv_err_labels[err]

  print



def net_stat(actions):
  """
    <Purpose>
      Given a list of actions, it generates network statistics

    <Arguments>
      actions: A list of actions from a parsed trace

    <Returns>
      None
  """
  for action_index in range(len(actions)):
    action = actions[action_index]

    # get the name of the syscall and remove the "_syscall" part at the end.
    action_name = action[0][:action[0].find("_syscall")]
    
    if action_name == "sendto":
      # ('sendto_syscall', (3, 'Message for sendto.\x00', 20, 0, ['AF_INET'], 
      #                     25588, '127.0.0.1', 16), (20, None))
      if action[2][0] != -1:
        stats["sends"] += 1
        stats["send_buf"] += action[1][2]
        stats["send_data"] += action[2][0]

        fam = action[1][4][0]
        if fam in send_families:
          send_families[fam] += 1
        else:
          send_families[fam] = 1
      else:
        stats["send_errs"] += 1
        err_label = action[2][1]
        if err_label in send_err_labels:
          send_err_labels[err_label] += 1
        else:
          send_err_labels[err_label] = 1

    elif action_name == "send":
      # ('send_syscall', (5, 'None shall be revealed\x00', 23, ['MSG_OOB']), 
      #                  (23, None))
      if action[2][0] != -1:
        stats["sends"] += 1
        stats["send_buf"] += action[1][2]
        stats["send_data"] += action[2][0]

        # get the socket family
        sockfd = action[1][0]
        fam = None
        if sockfd in sockets:
          fam = sockets[sockfd]
        elif sockfd in accepts:
          fam = accepts[sockfd]
          
        if fam != None:
          if fam in send_families:
            send_families[fam] += 1
          else:
            send_families[fam] = 1

      else:
        stats["send_errs"] += 1
        err_label = action[2][1]
        if err_label in send_err_labels:
          send_err_labels[err_label] += 1
        else:
          send_err_labels[err_label] = 1

    elif action_name == "recvfrom":
      # ('recvfrom_syscall', (3, 512, 0), (20, ('Message for sendto.\x00', 
      #                              ['AF_INET'], 52213, '127.0.0.1', 16)))
      if action[2][0] != -1:
        stats["recvs"] += 1
        stats["recv_buf"] += action[1][1]
        stats["recv_data"] += action[2][0]

        fam = action[2][1][1][0]
        if fam in recv_families:
          recv_families[fam] += 1
        else:
          recv_families[fam] = 1
      else:
        stats["recv_errs"] += 1
        err_label = action[2][1]
        if err_label in recv_err_labels:
          recv_err_labels[err_label] += 1
        else:
          recv_err_labels[err_label] = 1
    
    elif action_name == "recv":
      # ('recv_syscall', (5, 24, 0), (24, ('Message to be received.\x00',)))
      if action[2][0] != -1:
        stats["recvs"] += 1
        stats["recv_buf"] += action[1][1]
        stats["recv_data"] += action[2][0]

        # get the socket family
        sockfd = action[1][0]
        fam = None
        if sockfd in sockets:
          fam = sockets[sockfd]
        elif sockfd in accepts:
          fam = accepts[sockfd]

        if fam != None:
          if fam in recv_families:
            recv_families[fam] += 1
          else:
            recv_families[fam] = 1

      else:
        stats["recv_errs"] += 1
        err_label = action[2][1]
        if err_label in recv_err_labels:
          recv_err_labels[err_label] += 1
        else:
          recv_err_labels[err_label] = 1
    
    elif action_name == "socket":
      # ('socket_syscall', (['PF_FILE'], ['SOCK_STREAM', 'SOCK_CLOEXEC', 'SOCK_NONBLOCK'], 0), (4, None))
      if action[2][0] != -1:
        sockets[action[2][0]] = action[1][0][0]

    elif action_name == "accept":
      # ('accept_syscall', (3,), (4, (['AF_INET'], 50383, '127.0.0.1', 16)))
      if action[2][0] != -1:
        accepts[action[2][0]] = action[2][1][0][0]




if __name__ == "__main__":
  if len(sys.argv) < 2 or len(sys.argv) > 3:
    raise Exception("Please provide: trace file [file_path]")
  
  fh = open(sys.argv[1], "r")
  actions = parser_strace_calls.parse_trace(fh)
  
  net_stat(actions)
  print_net_stats()