###########
# IMPORTS #
###########

### Use with Repy ###
dy_import_module_symbols("lind_fs_constants")
dy_import_module_symbols("lind_net_constants")

### Use with Python ###
#from lind_fs_constants import *
#from lind_net_constants import *
#def log(*args):
#    perint args[0]

#############
# CONSTANTS #
#############
ALL_COMMANDS = ["socket", "bind", "connect", "sendto", "send", "recvfrom", "recv", "getsockname", "getpeername", "listen", "accept", "getsockopt", "setsockopt", "shutdown", "close", "fstatfs", "statfs", "access", "chdir", "mkdir", "rmdir", "link", "unlink", "stat", "fstat", "open", "creat", "lseek", "read", "write", "dup2", "dup", "fcntl", "getdents", "pipe", "eventfd", "eventfd2", "dup3", "inotify_init", "inotify_init1"]
UNIMPLEMENTED_ERROR = -1
FILE_NAME = "skype.strace_network"
#FILE_NAME = "ktorrent.strace_full"
#FILE_NAME = "chromium.strace_full"
SIGS = ["---", "+++"]
DEBUG = False
pendingStraceTable = []
ignore_fds = []


###########
# STRUCTS #
###########
class PendingStrace(object):
    def __init__(self, pid, command, firstHalf):
        self.pid = pid
        self.command = command
        self.firstHalf = firstHalf

    def __str__(self):
        line = str([self.pid, self.command, self.firstHalf])
        return line


#############
# FUNCTIONS #
#############
def getNumberValidTraceLines(fh, num):
    traces = []
    trace = []

    if num == -1:
        trace = getValidTraceLine(fh)
        while trace != []:
            traces += trace
            trace = getValidTraceLine(fh)
    else:
        while num > 0:
            trace = getValidTraceLine(fh)
            if trace == []:
                break
            traces += trace
            num -= 1

    return traces


def getValidTraceLine(fh):
    TRACE = []
    # Open the file and process each line
    for line in fh:
        line = line.strip()
        # Ignore SIGS
        if line[:3] in SIGS:
            continue

        # Did the strace get interrupted?
        if line.find("<unfinished ...>") != -1:
            # Ignore lines with only unfinished
            if line != "<unfinished ...>":
                try:
                    pid = int(line[line.find(" ")+1:line.find("]")])
                    command = line[line.find("]")+1:line.find("(")].strip()
                except:
                    pid = int(line[:line.find(" ")])
                    command = line[line.find(" ")+1:line.find("(")].strip()
                if command in ALL_COMMANDS:
                    #return [(pid, command)]
                    pendingStraceTable.append(PendingStrace(pid, command, line[:line.find("<unfinished ...>")].strip()))
            continue

        # Is the strace resuming?
        if line.find("<... ") != -1 and line.find(" resumed>") != -1:
            try:
                pid = int(line[line.find(" ")+1:line.find("]")])
            except:
                pid = int(line[:line.find(" ")])
            command = line[line.find("<... ") + 5:line.find(" resumed>")]
            pendingIdx = findPendingStrace(pendingStraceTable, pid, command)
            # If pending strace isn't found, ignore and continue
            if pendingIdx == None:
                continue
            else:
                pending = pendingStraceTable[pendingIdx]
                secondHalf = line[line.find("resumed>")+8:].strip()
                if secondHalf[0] != ')':
                    secondHalf = " " + secondHalf
                oldLine = line
                line = pending.firstHalf + secondHalf
                pendingStraceTable.pop(pendingIdx)

        # Ignore lines starting with Process:
        if line[:line.find(" ")] == "Process":
            continue
        
        # Ignore incomplete strace lines without '(', ')', and '='
        if line.find('(') == -1 or line.find(')') == -1 or line.find('=') == -1:
            continue
 
        # Get the first command name, parameters, and result
        if DEBUG:
            log(line)
        if line[0] == '[':
            command = line[line.find(']')+2:line.find('(')]
        elif len(line[:line.find('(')].split(" ")) > 1:
            command = line[:line.find('(')].split(" ")[-1]
        else:
            command = line[:line.find('(')]
        parameterChunk = line[line.find('(')+1:line.rfind('=')].strip()
        parameters = parameterChunk[:-1].split(", ")
        straceResult = line[line.rfind('=')+2:].strip()

        #EFM
        # Fix errors from split on messages
        mergeQuoteParameters(parameters)

        #JR
        # Is the result a status number or error message?
        spaced_results = straceResult.split(" ")
        if len(spaced_results) > 1:
            straceResult = straceResult[:straceResult.find(" ")]
        # Apparently the strace result can also be a ?...
        try:
            straceResult = int(straceResult)
        except:
            pass

        if straceResult == -1 and len(spaced_results) > 1:
            straceResult = (straceResult, spaced_results[1])
        else:
            straceResult = (straceResult, None)

        # Convert parameters into ints, execute, and assert ==

        #################### NET CALLS ####################

        ##### SOCKET #####
        if command == "socket":
            try:
                domain = int(parameters[0])
            except:
                domain = splitAndCombine(parameters[0])

            try:
                socktype = int(parameters[1])
            except:
                socktype = splitAndCombine(parameters[1])

            try:
                protocol = int(parameters[2])
            except:
                protocol = splitAndCombine(parameters[2])

            if DEBUG:
                log(command, domain, socktype, protocol, straceResult, '\n')
            if domain == UNIMPLEMENTED_ERROR or socktype == UNIMPLEMENTED_ERROR or protocol == UNIMPLEMENTED_ERROR:
                if straceResult[0] != -1:
                    ignore_fds.append(straceResult[0])
                if DEBUG:
                    log("Unimplemented parameter, skipping...\n")
            else:
                TRACE.append(('socket_syscall', (domain,socktype, protocol), straceResult))

        ##### BIND #####
        elif command == "bind":
            sockfd = int(parameters[0])
            if sockfd in ignore_fds:
                continue

            localip = UNIMPLEMENTED_ERROR
            localport = UNIMPLEMENTED_ERROR
            for index in range(1,len(parameters)-1, 1):
                p = parameters[index]
                if p.find("sin_addr") != -1:
                    localip = p[p.find("\"")+1:p.rfind("\"")]
                elif p.find("sin_port") != -1:
                    localport = int(p[p.find("(")+1:p.rfind(")")])

            if DEBUG:
                log(command, sockfd, localip, localport, straceResult, '\n')
            if localip == UNIMPLEMENTED_ERROR or localport == UNIMPLEMENTED_ERROR:
                if DEBUG:

                    log("Unimplemented parameter, skipping...\n")
            else:
                TRACE.append(('bind_syscall',(sockfd, localip, localport), straceResult))

        ##### CONNECT #####
        elif command == "connect":
            sockfd = int(parameters[0])
            if sockfd in ignore_fds:
                continue

            remoteip = UNIMPLEMENTED_ERROR
            remoteport = UNIMPLEMENTED_ERROR
            for index in range(1,len(parameters)-1, 1):
                p = parameters[index]
                if p.find("sin_addr") != -1:
                    remoteip = p[p.find("\"")+1:p.rfind("\"")]
                elif p.find("sin_port") != -1:
                    remoteport = int(p[p.find("(")+1:p.rfind(")")])

            if DEBUG:
                log(command, sockfd, remoteip, remoteport, straceResult)
            if remoteip == UNIMPLEMENTED_ERROR or remoteport == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    log("Unimplemented parameter, skipping...")


            else:
                TRACE.append(('connect_syscall',(sockfd, remoteip, remoteport), straceResult))

        # BUG: If message is larger than a certain length then strace will cut it off with '...' which could cause a false failure in comparison
        ##### SENDTO #####
        elif command == "sendto":

            sockfd = int(parameters[0])
            if sockfd in ignore_fds:
                continue

            # Get the message without quotes
            message = parameters[1].strip("...")[1:len(parameters[1])-1]

            try:
                flags = int(parameters[3])
            except:
                flags = splitAndCombine(parameters[3])

            if parameters[4] == "NULL":
                remoteip = ''
                remoteport = 0
            else:
                remoteip = UNIMPLEMENTED_ERROR
                remoteport = UNIMPLEMENTED_ERROR
                for index in range(4,len(parameters)-1, 1):
                    p = parameters[index]
                    if p.find("sin_addr") != -1:
                        remoteip = p[p.find("\"")+1:p.rfind("\"")]
                    elif p.find("sin_port") != -1:
                        remoteport = int(p[p.find("(")+1:p.rfind(")")])
            
            if DEBUG:
                log(command, sockfd, message, remoteip, remoteport, flags, straceResult)
            if remoteip == UNIMPLEMENTED_ERROR or remoteport == UNIMPLEMENTED_ERROR or flags == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    log("Unimplemented parameter, skipping...")
            else:
                TRACE.append(('sendto_syscall',(sockfd, message, remoteip, remoteport, flags), straceResult))

        ##### SEND #####
        elif command == "send":
            if(len(parameters) > 4):
                merge(parameters, 1, len(parameters)-2)

            sockfd = int(parameters[0])
            if sockfd in ignore_fds:
                continue

            # Get the message without quotes
            message = parameters[1].strip("...")[1:len(parameters[1])-1]

            try:
                flags = int(parameters[-1])
            except:
                flags = splitAndCombine(parameters[-1])

            if DEBUG:
                log(command, sockfd, message, flags, straceResult)
            if flags == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    log("Unimplemented parameter, skipping...")
            else:
                TRACE.append(('send_syscall',(sockfd, message, flags), straceResult))

        ##### RECVFROM #####
        elif command == "recvfrom":
            sockfd = int(parameters[0])
            if sockfd in ignore_fds:
                continue

            # Get the message without quotes
            message = parameters[1].strip("...")[1:len(parameters[1])-1]

            length = int(parameters[2])

            try:
                flags = int(parameters[3])
            except:
                flags = splitAndCombine(parameters[3])

            if parameters[4] == "NULL":
                remoteip = ''
                remoteport = 0
            else:
                remoteip = UNIMPLEMENTED_ERROR
                remoteport = UNIMPLEMENTED_ERROR
                for index in range(4,len(parameters)-1, 1):
                    p = parameters[index]
                    if p.find("sin_addr") != -1:
                        remoteip = p[p.find("\"")+1:p.rfind("\"")]
                    elif p.find("sin_port") != -1:
                        remoteport = int(p[p.find("(")+1:p.rfind(")")])

            if DEBUG:
                log(command, sockfd, message, remoteip, remoteport, flags, straceResult)
            if remoteip == UNIMPLEMENTED_ERROR or remoteport == UNIMPLEMENTED_ERROR or flags == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    log("Unimplemented parameter, skipping...")
            else:
                straceResult = (message,) + straceResult[1:]
                TRACE.append(('recvfrom_syscall',(sockfd, length, flags), straceResult))

        ##### RECV #####
        elif command == "recv":
            if(len(parameters) > 4):
                merge(parameters, 1, len(parameters)-2)

            sockfd = int(parameters[0])
            if sockfd in ignore_fds:
                continue

            # Get the message without quotes
            message = parameters[1].strip("...")[1:len(parameters[1])-1]

            length = int(parameters[-2])

            try:
                flags = int(parameters[-1])
            except:
                flags = splitAndCombine(parameters[-1])

            if DEBUG:
                log(command, sockfd, length, flags, straceResult)
            if flags == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    log("Unimplemented parameter, skipping...")
            else:
                straceResult = (message,) + straceResult[1:]
                TRACE.append(('recv_syscall',(sockfd, length, flags), straceResult))

        ##### GETSOCKNAME #####
        elif command == "getsockname":
            sockfd = int(parameters[0])
            if sockfd in ignore_fds:
                continue

            localip = UNIMPLEMENTED_ERROR
            localport = UNIMPLEMENTED_ERROR
            for index in range(1,len(parameters)-1, 1):
                p = parameters[index]
                if p.find("sin_addr") != -1:
                    localip = p[p.find("\"")+1:p.rfind("\"")]
                elif p.find("sin_port") != -1:
                    localport = int(p[p.find("(")+1:p.rfind(")")])
            
            if DEBUG:
                log(command, sockfd, localip, localport, straceResult)
            if localip == UNIMPLEMENTED_ERROR or localport == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    log("Unimplemented parameter, skipping...")
            else:
                straceResult = ((localip, localport),) + straceResult[1:]
                TRACE.append(('getsockname_syscall',(sockfd,), straceResult))
                #TRACE.append(('getsockname_syscall',(sockfd,), (localip, localport)))

        ##### GETPEERNAME #####
        elif command == "getpeername":
            sockfd = int(parameters[0])
            if sockfd in ignore_fds:
                continue

            remoteip = UNIMPLEMENTED_ERROR
            remoteport = UNIMPLEMENTED_ERROR
            for index in range(1,len(parameters)-1, 1):
                p = parameters[index]
                if p.find("sin_addr") != -1:
                    remoteip = p[p.find("\"")+1:p.rfind("\"")]
                elif p.find("sin_port") != -1:
                    remoteport = int(p[p.find("(")+1:p.rfind(")")])

            if DEBUG:
                log(command, sockfd, remoteip, remoteport, straceResult)
            if remoteip == UNIMPLEMENTED_ERROR or remoteport == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    log("Unimplemented parameter, skipping...")
            else:
                straceResult = ((remoteip,remoteport),) + straceResult[1:]
                TRACE.append(('getpeername_syscall',(sockfd,), straceResult))

        ##### LISTEN  #####
        elif command == "listen":
            sockfd = int(parameters[0])
            if sockfd in ignore_fds:
                continue

            try:
                backlog = int(parameters[1])
            except:
                backlog = splitAndCombine(parameters[1])

            if DEBUG:
                log(command, sockfd, backlog, straceResult)
            TRACE.append(('listen_syscall',(sockfd, backlog), straceResult))

        ##### ACCEPT #####
        elif command == "accept" or command == "accept4":
            sockfd = int(parameters[0])
            if sockfd in ignore_fds:
                continue

            remoteip = UNIMPLEMENTED_ERROR
            remoteport = UNIMPLEMENTED_ERROR
            for index in range(1,len(parameters)-1, 1):
                p = parameters[index]
                if p.find("sin_addr") != -1:
                    remoteip = p[p.find("\"")+1:p.rfind("\"")]
                elif p.find("sin_port") != -1:
                    remoteport = int(p[p.find("(")+1:p.rfind(")")])

            if DEBUG:
                log(command, sockfd, remoteip, remoteport, straceResult)
            if remoteip == UNIMPLEMENTED_ERROR or remoteport == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    log("Unimplemented parameter, skipping...")
            else:
                TRACE.append(('accept_syscall',(sockfd,remoteip,remoteport), straceResult))

        ##### GETSOCKOPT #####
        elif command == "getsockopt":
            sockfd = int(parameters[0])
            if sockfd in ignore_fds:
                continue

            try:
                level = int(parameters[1])
            except:
                level = splitAndCombine(parameters[1])

            try:
                optname = int(parameters[2])
            except:
                optname = splitAndCombine(parameters[2])

            try:
                result = (parameters[3], None)
                tmp = eval(parameters[3])
                tmp = tmp[0]
                result = (tmp, None)
            except:
                result = straceResult

            if DEBUG:
                log(command, sockfd, level, optname, result)

            if level == UNIMPLEMENTED_ERROR or optname == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    log("Unimplemented parameter, skipping...")
            else:
                TRACE.append(('getsockopt_syscall',(sockfd, level, optname), result))

        ##### SETSOCKOPT #####
        elif command == "setsockopt":
            sockfd = int(parameters[0])
            if sockfd in ignore_fds:
                continue

            try:
                level = int(parameters[1])
            except:
                level = splitAndCombine(parameters[1])

            try:
                optname = int(parameters[2])
            except:
                optname = splitAndCombine(parameters[2])

            try:
                optval = int(parameters[3].strip("[]"))
            except:
                optval = splitAndCombine(parameters[3])

            if DEBUG:
                log(command, sockfd, level, optname, optval, straceResult)
            if level == UNIMPLEMENTED_ERROR or optname == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    log("Unimplemented parameter, skipping...")
            else:
                TRACE.append(('setsockopt_syscall',(sockfd, level, optname, optval), straceResult))

        ##### SHUTDOWN #####
        elif command == "shutdown":
            sockfd = int(parameters[0])
            if sockfd in ignore_fds:
                continue

            try:
                how = int(parameters[1])
            except:
                how = splitAndCombine(parameters[1])

            if DEBUG:
                log(command, sockfd, how, straceResult)
            if how == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    log("Unimplemented parameter, skipping...")
            else:
                TRACE.append(('setshutdown_syscall',(sockfd, how), straceResult))

        ##### CLOSE #####
        elif command == "close":
            sockfd = int(parameters[0])
            if sockfd in ignore_fds:
                ignore_fds.pop(ignore_fds.index(sockfd))
                continue

            if DEBUG:
                log(command, sockfd, straceResult)
            TRACE.append(('close_syscall', (sockfd,), straceResult))


        ##### SOCKETPAIR #####

        ##### RECVMSG #####
#        elif command == "recvmsg":
#            sockfd = int(parameters[0])
#
#            try:
#                flags = int(parameters[-1])
#            except:
#                flags = splitAndCombine(parameters[-1])
#
#            message = UNIMPLEMENTED_ERROR
#            for index in range(1,len(parameters)-1, 1):
#                p = parameters[index]
#                if p.find("msg_iov") != -1:
#                    message = p[p.find("\"")+1:p.rfind("\"")]
#            
#            if DEBUG:
#                log(command, sockfd, message, flags, straceResult)
#            if message == UNIMPLEMENTED_ERROR or flags == UNIMPLEMENTED_ERROR:
#                if DEBUG:
#                    log("Unimplemented parameter, skipping...")
#            else:
#                pass
#                #result = recvmsg_syscall(sockfd, flags)
#                #assert result == message
#
        ##### SENDMSG #####
#        elif command == "sendmsg":
#            sockfd = int(parameters[0])
#
#            try:
#                flags = int(parameters[-1])
#            except:
#                flags = splitAndCombine(parameters[-1])
#
#            message = UNIMPLEMENTED_ERROR
#            for index in range(1,len(parameters)-1, 1):
#                p = parameters[index]
#                if p.find("msg_iov") != -1:
#                    message = p[p.find("\"")+1:p.rfind("\"")]
#
#            if DEBUG:
#                log(command, sockfd, message, flags, straceResult)
#            if message == UNIMPLEMENTED_ERROR or flags == UNIMPLEMENTED_ERROR:
#                if DEBUG:
#                    log("Unimplemented parameter, skipping...")
#            else:
#                pass
#                #result = sendmsg_syscall(sockfd, message, flags)
#                #assert result == straceResult
#

        #################### FILE SYSTEM CALLS ####################

        ##### FSTATFS #####
        elif command == "fstatfs" or command == "fstatfs64":
            fd = int(parameters[0])

            if fd in ignore_fds:
                continue

            if DEBUG:
                log(command, fd, straceResult)            
            TRACE.append(('fstatfs_syscall', (fd,), straceResult))

        ##### STATFS #####
        elif command == "statfs" or command == "statfs64":
            path = parameters[0].strip("\"")

            if DEBUG:
                log(command, path, straceResult)
            TRACE.append(('statfs_syscall', (path,), straceResult))

        ##### ACCESS #####
        elif command == "access":
            path = parameters[0].strip("\"")

            try:
                mode = int(parameters[1])
            except:
                mode = splitAndCombine(parameters[1])

            if DEBUG:
                log(command, path, mode, straceResult)
            if mode == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    log("Unimplemented parameter, skipping...")
            else:
                TRACE.append(('access_syscall', (path, mode), straceResult))

        ##### CHDIR #####
        elif command == "chdir":
            path = parameters[0].strip("\"")

            if DEBUG:
                log(command, path, straceResult)
            TRACE.append(('chdir_syscall', (path,), straceResult))

        ##### MKDIR #####
        elif command == "mkdir":
            path = parameters[0].strip("\"")

            try:
                mode = int(parameters[1])
            except:
                mode = splitAndCombine(parameters[1])

            if DEBUG:
                log(command, path, mode, straceResult)
            if mode == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    log("Unimplemented parameter, skipping...")
            else:
                TRACE.append(('mkdir_syscall', (path, mode), straceResult))

        ##### RMDIR #####
        elif command == "rmdir":
            path = parameters[0].strip("\"")

            if DEBUG:
                log(command, path, straceResult)
            TRACE.append(('rmdir_syscall', (path,), straceResult))

        ##### LINK  #####
        elif command == "link":
            oldpath = parameters[0].strip("\"")

            newpath = parameters[0].strip("\"")

            if DEBUG:
                log(command, oldpath, newpath, straceResult)
            TRACE.append(('link_syscall', (oldpath, newpath), straceResult))

        ##### UNLINK #####
        elif command == "unlink":
            path = parameters[0].strip("\"")

            if DEBUG:
                log(command, path, straceResult)
            TRACE.append(('unlink_syscall', (path,), straceResult))

        ##### STAT #####
        elif command == "stat" or command == "stat64":
            path = parameters[0].strip("\"")

            if DEBUG:
                log(command, path, straceResult)
            TRACE.append(('stat_syscall', (path,), straceResult))

        ##### FSTAT #####
        elif command == "fstat" or command == "fstat64":
            fd = int(parameters[0])

            if fd in ignore_fds:
                continue

            if DEBUG:
                log(command, fd, straceResult)            
            TRACE.append(('fstat_syscall', (fd,), straceResult))

        ##### OPEN #####
        elif command == "open":
            path = parameters[0].strip("\"")

            try:
                flags = int(parameters[1])
            except:
                flags = splitAndCombine(parameters[1])

            if len(parameters) > 2:
                try:
                    mode = int(parameters[2])
                except:
                    mode = splitAndCombine(parameters[2])

                if DEBUG:
                    log(command, path, flags, mode, straceResult)
                if flags == UNIMPLEMENTED_ERROR or mode == UNIMPLEMENTED_ERROR:
                    if DEBUG:
                        log("Unimplemented parameter, skipping...")
                    if straceResult[0] != -1:
                        ignore_fds.append(straceResult[0])
                else:
                    TRACE.append(('open_syscall', (path, flags, mode), straceResult))

            else:
                if DEBUG:
                    log(command, path, flags, straceResult)
                if flags == UNIMPLEMENTED_ERROR:
                    if DEBUG:
                        log("Unimplemented parameter, skipping...")
                    if straceResult[0] != -1:
                        ignore_fds.append(straceResult[0])
                else:
                    # POTENTIAL BUG: I have to put some kind of mode value for the open syscall. For now it's 0.
                    TRACE.append(('open_syscall', (path, flags, 0), straceResult))

        ##### CREAT #####
        elif command == "creat":
            path = parameters[0].strip("\"")

            try:
                mode = int(parameters[1])
            except:
                mode = splitAndCombine(parameters[1])

            if DEBUG:
                log(command, path, mode, straceResult)
            if mode == UNIMPLEMENTED_ERROR:
                if straceResult[0] != -1:
                    ignore_fds.append(straceResult[0])
                if DEBUG:
                    log("Unimplemented parameter, skipping...")
            else:
                TRACE.append(('creat_syscall', (path, mode), straceResult))

        ##### LSEEK #####
        elif command == "lseek":
            fd = int(parameters[0])

            if fd in ignore_fds:
                continue

            try:
                offset = int(parameters[1])
            except:
                offset = splitAndCombine(parameters[1])

            try:
                whence = int(parameters[2])
            except:
                whence = splitAndCombine(parameters[2])

            if DEBUG:
                log(command, fd, offset, whence, straceResult)
            if offset == UNIMPLEMENTED_ERROR or whence == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    log("Unimplemented parameter, skipping...")
            else:
                TRACE.append(('lseek_syscall', (fd, offset, whence), straceResult))

        ##### READ #####
        elif command == "read":
            if(len(parameters) > 3):
                merge(parameters, 1, len(parameters)-1)

            fd = int(parameters[0])

            if fd in ignore_fds:
                continue

            count = int(parameters[-1])

            if DEBUG:
                log(command, fd, count, straceResult)
            TRACE.append(('read_syscall', (fd, count), straceResult))

        ##### WRITE #####
        elif command == "write":
            if(len(parameters) > 3):
                merge(parameters, 1, len(parameters)-1)

            fd = int(parameters[0])

            if fd in ignore_fds:
                continue

            # Remove ... and then remove "'s without changing data
            data = parameters[1].strip(".").strip("\"")

            if DEBUG:
                log(command, fd, data, straceResult)
            TRACE.append(('write_syscall', (fd, data), straceResult))

        ##### CLOSE #####
        # Already implemented for sockets above... Works same way.

        ##### DUP2 #####
        elif command == "dup2":
            oldfd = int(parameters[0])

            newfd = int(parameters[1])

            if oldfd in ignore_fds:
                if straceResult[0] != -1:
                    ignore_fds.append(straceResult[0])
                continue

            if DEBUG:
                log(command, oldfd, newfd, straceResult)
            TRACE.append(('dup2_syscall', (oldfd, newfd), straceResult))

        ##### DUP #####
        elif command == "dup":
            fd = int(parameters[0])

            if fd in ignore_fds:
                if straceResult[0] != -1:
                    ignore_fds.append(straceResult[0])
                continue

            if DEBUG:
                log(command, fd, straceResult)
            TRACE.append(('dup_syscall', (fd,), straceResult))

        ##### FCNTL #####
        elif command == "fcntl" or command == "fcntl64":
            fd = int(parameters[0])

            if fd in ignore_fds:
                if ("F_DUPFD" in parameters[1].split("|") or "F_DUPFD_CLOEXEC" in parameters[1].split("|")) and straceResult[0] != -1:
                    ignore_fds.append(straceResult[0])
                continue
            try:
                cmd = int(parameters[1])
            except:
                cmd = splitAndCombine(parameters[1])

            if len(parameters) > 2:
                try:
                    args = int(parameters[2])
                except:
                    args = splitAndCombine(parameters[2])

                if DEBUG:
                    log(command, fd, cmd, args, straceResult)
                if cmd == UNIMPLEMENTED_ERROR or args == UNIMPLEMENTED_ERROR:
                    if ("F_DUPFD" in parameters[1].split("|") or "F_DUPFD_CLOEXEC" in parameters[1].split("|")) and straceResult[0] != -1:
                        ignore_fds.append(straceResult[0])

                    if DEBUG:
                        log("Unimplemented parameter, skipping...")
                else:
                    TRACE.append(('fcntl_syscall', (fd, cmd, args), straceResult))

            else:
                if DEBUG:
                    log(command, fd, cmd, straceResult)
                if cmd == UNIMPLEMENTED_ERROR:
                    if ("F_DUPFD" in parameters[1].split("|") or "F_DUPFD_CLOEXEC" in parameters[1].split("|")) and straceResult[0] != -1:
                        ignore_fds.append(straceResult[0])

                    if DEBUG:
                        log("Unimplemented parameter, skipping...")
                else:
                    # POTENTIAL BUG: I have to put some kind of mode value for the fcntl syscall. For now it's 0.
                    TRACE.append(('fcntl_syscall', (fd, cmd), straceResult))

        ##### GETDENTS #####
        elif command == "getdents" or command == "getdents64":
            fd = int(parameters[0])

            if fd in ignore_fds:
                continue

            quantity = int(parameters[2])

            if DEBUG:
                log(command, fd, quantity, straceResult)
            TRACE.append(('getdents_syscall', (fd, quantity), straceResult))

        ##### PIPE #####
        elif (command == "pipe" or command == "pipe2") and straceResult[0] != -1:
            fd1 = int(parameters[0].strip('['))
            fd2 = int(parameters[1].strip(']'))
            # Parent fd
            ignore_fds.append(fd1)
            ignore_fds.append(fd2)
            # Child fd
            ignore_fds.append(fd1)
            ignore_fds.append(fd2)

        ##### EVENTFD #####
        elif command == "eventfd":
            if straceResult[0] != -1:
                ignore_fds.append(straceResult[0])

        ##### EVENTFD2 #####
        elif command == "eventfd2":
            if straceResult[0] != -1:
                ignore_fds.append(straceResult[0])

        ##### DUP3 #####
        elif command == "dup3":
            oldfd = int(parameters[0])

            newfd = int(parameters[1])

            if straceResult[0] != -1:
                ignore_fds.append(straceResult[0])

        ##### INOTIFY_INIT #####
        elif command == "inotify_init":
            if straceResult[0] != -1:
                ignore_fds.append(straceResult[0])

        ##### INOTIFY_INIT1 #####
        elif command == "inotify_init1":
            if straceResult[0] != -1:
                ignore_fds.append(straceResult[0])

        ##### NOT IMPLEMENTED #####
        else:
            if DEBUG:
                log("Command " + command + " currently not supported. Skipping...")

        if DEBUG:
            log('\n')

        if len(TRACE) >= 1:
            return TRACE

    return TRACE


def merge(parameters, start, end):
    for i in range(start, end - 1):
        parameters[start] += ", " + parameters[start+1]
        parameters.pop(start+1)


def mergeQuoteParameters(parameters):
    removeEmptyParameters(parameters)
    if len(parameters) <= 1:
        return
    index = 0
    while index < len(parameters):
        if  parameters[index][0] == "\"" and (len(parameters[index]) == 1 or parameters[index].strip(".")[-1] != "\""):
            # The only quote is the first quote which means the whole sentence got split and should be put back together.
            while index+1 < len(parameters):
                if parameters[index+1].strip(".")[-1] != "\"":
                    parameters[index] += ", " + parameters[index+1]
                    parameters.pop(index+1)
                else:
                    parameters[index] += ", " + parameters[index+1]
                    parameters.pop(index+1)
                    break
        index += 1


def removeEmptyParameters(parameters):
    for i in range(-1, -len(parameters), -1):
        if len(parameters[i]) == 0:
            parameters.pop(i)


def findPendingStrace(table, pid, command):
    for index in range(0, len(table), 1):
        if table[index].pid == pid and table[index].command == command:
            return index


def splitAndCombine(string):
    result = 0
    stringParts = string.split("|")
    for param in stringParts:
        paramValue = convert(param)

        if paramValue == UNIMPLEMENTED_ERROR:
            return UNIMPLEMENTED_ERROR
        result |= paramValue
    return result


def convert(string):
    if string == "SOCK_STREAM":
        return SOCK_STREAM
    elif string == "SOCK_DGRAM":
        return SOCK_DGRAM
    elif string == "SOCK_RAW":
        return SOCK_RAW
    elif string == "SOCK_RDM":
        return SOCK_RDM
    elif string == "SOCK_SEQPACKET":
        return SOCK_SEQPACKET
    elif string == "AF_UNSPEC":
        return AF_UNSPEC
    elif string == "AF_UNIX":
        return AF_UNIX
    elif string == "AF_LOCAL":
        return AF_LOCAL
    elif string == "PF_FILE":
        return PF_FILE
    elif string == "AF_INET":
        return AF_INET
    elif string == "AF_IMPLINK":
        return AF_IMPLINK
    elif string == "AF_PUP":
        return AF_PUP
    elif string == "AF_CHAOS":
        return AF_CHAOS
    elif string == "AF_NS":
        return AF_NS
    elif string == "AF_ISO":
        return AF_ISO
    elif string == "AF_OSI":
        return AF_OSI
    elif string == "AF_ECMA":
        return AF_ECMA
    elif string == "AF_DATAKIT":
        return AF_DATAKIT
    elif string == "AF_CCITT":
        return AF_CCITT
    elif string == "AF_SNA":
        return AF_SNA
    elif string == "AF_DECnet":
        return AF_DECnet
    elif string == "AF_DLI":
        return AF_DLI
    elif string == "AF_LAT":
        return AF_LAT
    elif string == "AF_HYLINK":
        return AF_HYLINK
    elif string == "AF_APPLETALK":
        return AF_APPLETALK
    elif string == "AF_ROUTE":
        return AF_ROUTE
    elif string == "AF_LINK":
        return AF_LINK
    elif string == "pseudo_AF_XTP":
        return pseudo_AF_XTP
    elif string == "AF_COIP":
        return AF_COIP
    elif string == "AF_CNT":
        return AF_CNT
    elif string == "pseudo_AF_RTIP":
        return pseudo_AF_RTIP
    elif string == "AF_IPX":
        return AF_IPX
    elif string == "AF_SIP":
        return AF_SIP
    elif string == "pseudo_AF_PIP":
        return pseudo_AF_PIP
    elif string == "pseudo_AF_BLUE":
        return pseudo_AF_BLUE
    elif string == "AF_NDRV":
        return AF_NDRV
    elif string == "AF_ISDN":
        return AF_ISDN
    elif string == "AF_E164":
        return AF_E164
    elif string == "pseudo_AF_KEY":
        return pseudo_AF_KEY
    elif string == "AF_INET6":
        return AF_INET6
    elif string == "AF_NATM":
        return AF_NATM
    elif string == "AF_SYSTEM":
        return AF_SYSTEM
    elif string == "AF_NETBIOS":
        return AF_NETBIOS
    elif string == "AF_PPP":
        return AF_PPP
    elif string == "pseudo_AF_HDRCMPLT":
        return pseudo_AF_HDRCMPLT
    elif string == "AF_RESERVED_36":
        return AF_RESERVED_36
    elif string == "AF_IEEE80211":
        return AF_IEEE80211
    elif string == "AF_MAX":
        return AF_MAX
    elif string == "IPPROTO_IP":
        return IPPROTO_IP
    elif string == "IPPROTO_ICMP":
        return IPPROTO_ICMP
    elif string == "IPPROTO_IGMP":
        return IPPROTO_IGMP
    elif string == "IPPROTO_GGP":
        return IPPROTO_GGP
    elif string == "IPPROTO_IPV4":
        return IPPROTO_IPV4
    elif string == "IPPROTO_IPIP":
        return IPPROTO_IPIP
    elif string == "IPPROTO_TCP":
        return IPPROTO_TCP
    elif string == "IPPROTO_ST":
        return IPPROTO_ST
    elif string == "IPPROTO_EGP":
        return IPPROTO_EGP
    elif string == "IPPROTO_PIGP":
        return IPPROTO_PIGP
    elif string == "IPPROTO_RCCMON":
        return IPPROTO_RCCMON
    elif string == "IPPROTO_NVPII":
        return IPPROTO_NVPII
    elif string == "IPPROTO_PUP":
        return IPPROTO_PUP
    elif string == "IPPROTO_ARGUS":
        return IPPROTO_ARGUS
    elif string == "IPPROTO_EMCON":
        return IPPROTO_EMCON
    elif string == "IPPROTO_XNET":
        return IPPROTO_XNET
    elif string == "IPPROTO_CHAOS":
        return IPPROTO_CHAOS
    elif string == "IPPROTO_UDP":
        return IPPROTO_UDP
    elif string == "IPPROTO_MUX":
        return IPPROTO_MUX
    elif string == "IPPROTO_MEAS":
        return IPPROTO_MEAS
    elif string == "IPPROTO_HMP":
        return IPPROTO_HMP
    elif string == "IPPROTO_PRM":
        return IPPROTO_PRM
    elif string == "IPPROTO_IDP":
        return IPPROTO_IDP
    elif string == "IPPROTO_TRUNK1":
        return IPPROTO_TRUNK1
    elif string == "IPPROTO_TRUNK2":
        return IPPROTO_TRUNK2
    elif string == "IPPROTO_LEAF1":
        return IPPROTO_LEAF1
    elif string == "IPPROTO_LEAF2":
        return IPPROTO_LEAF2
    elif string == "IPPROTO_RDP":
        return IPPROTO_RDP
    elif string == "IPPROTO_IRTP":
        return IPPROTO_IRTP
    elif string == "IPPROTO_TP":
        return IPPROTO_TP
    elif string == "IPPROTO_BLT":
        return IPPROTO_BLT
    elif string == "IPPROTO_NSP":
        return IPPROTO_NSP
    elif string == "IPPROTO_INP":
        return IPPROTO_INP
    elif string == "IPPROTO_SEP":
        return IPPROTO_SEP
    elif string == "IPPROTO_3PC":
        return IPPROTO_3PC
    elif string == "IPPROTO_IDPR":
        return IPPROTO_IDPR
    elif string == "IPPROTO_XTP":
        return IPPROTO_XTP
    elif string == "IPPROTO_DDP":
        return IPPROTO_DDP
    elif string == "IPPROTO_CMTP":
        return IPPROTO_CMTP
    elif string == "IPPROTO_TPXX":
        return IPPROTO_TPXX
    elif string == "IPPROTO_IL":
        return IPPROTO_IL
    elif string == "IPPROTO_IPV6":
        return IPPROTO_IPV6
    elif string == "IPPROTO_SDRP":
        return IPPROTO_SDRP
    elif string == "IPPROTO_ROUTING":
        return IPPROTO_ROUTING
    elif string == "IPPROTO_FRAGMENT":
        return IPPROTO_FRAGMENT
    elif string == "IPPROTO_IDRP":
        return IPPROTO_IDRP
    elif string == "IPPROTO_RSVP":
        return IPPROTO_RSVP
    elif string == "IPPROTO_GRE":
        return IPPROTO_GRE
    elif string == "IPPROTO_MHRP":
        return IPPROTO_MHRP
    elif string == "IPPROTO_BHA":
        return IPPROTO_BHA
    elif string == "IPPROTO_ESP":
        return IPPROTO_ESP
    elif string == "IPPROTO_AH":
        return IPPROTO_AH
    elif string == "IPPROTO_INLSP":
        return IPPROTO_INLSP
    elif string == "IPPROTO_SWIPE":
        return IPPROTO_SWIPE
    elif string == "IPPROTO_NHRP":
        return IPPROTO_NHRP
    elif string == "IPPROTO_ICMPV6":
        return IPPROTO_ICMPV6
    elif string == "IPPROTO_NONE":
        return IPPROTO_NONE
    elif string == "IPPROTO_DSTOPTS":
        return IPPROTO_DSTOPTS
    elif string == "IPPROTO_AHIP":
        return IPPROTO_AHIP
    elif string == "IPPROTO_CFTP":
        return IPPROTO_CFTP
    elif string == "IPPROTO_HELLO":
        return IPPROTO_HELLO
    elif string == "IPPROTO_SATEXPAK":
        return IPPROTO_SATEXPAK
    elif string == "IPPROTO_KRYPTOLAN":
        return IPPROTO_KRYPTOLAN
    elif string == "IPPROTO_RVD":
        return IPPROTO_RVD
    elif string == "IPPROTO_IPPC":
        return IPPROTO_IPPC
    elif string == "IPPROTO_ADFS":

        return IPPROTO_ADFS
    elif string == "IPPROTO_SATMON":
        return IPPROTO_SATMON
    elif string == "IPPROTO_VISA":
        return IPPROTO_VISA
    elif string == "IPPROTO_IPCV":
        return IPPROTO_IPCV
    elif string == "IPPROTO_CPNX":
        return IPPROTO_CPNX
    elif string == "IPPROTO_CPHB":
        return IPPROTO_CPHB
    elif string == "IPPROTO_WSN":
        return IPPROTO_WSN
    elif string == "IPPROTO_PVP":
        return IPPROTO_PVP
    elif string == "IPPROTO_BRSATMON":
        return IPPROTO_BRSATMON
    elif string == "IPPROTO_ND":
        return IPPROTO_ND
    elif string == "IPPROTO_WBMON":
        return IPPROTO_WBMON
    elif string == "IPPROTO_WBEXPAK":
        return IPPROTO_WBEXPAK
    elif string == "IPPROTO_EON":
        return IPPROTO_EON
    elif string == "IPPROTO_VMTP":
        return IPPROTO_VMTP
    elif string == "IPPROTO_SVMTP":
        return IPPROTO_SVMTP

    elif string == "IPPROTO_VINES":
        return IPPROTO_VINES
    elif string == "IPPROTO_TTP":
        return IPPROTO_TTP
    elif string == "IPPROTO_IGP":
        return IPPROTO_IGP
    elif string == "IPPROTO_DGP":
        return IPPROTO_DGP
    elif string == "IPPROTO_TCF":
        return IPPROTO_TCF
    elif string == "IPPROTO_IGRP":
        return IPPROTO_IGRP
    elif string == "IPPROTO_OSPFIGP":
        return IPPROTO_OSPFIGP
    elif string == "IPPROTO_SRPC":
        return IPPROTO_SRPC
    elif string == "IPPROTO_LARP":
        return IPPROTO_LARP
    elif string == "IPPROTO_MTP":
        return IPPROTO_MTP
    elif string == "IPPROTO_AX25":
        return IPPROTO_AX25
    elif string == "IPPROTO_IPEIP":
        return IPPROTO_IPEIP
    elif string == "IPPROTO_MICP":
        return IPPROTO_MICP
    elif string == "IPPROTO_SCCSP":
        return IPPROTO_SCCSP
    elif string == "IPPROTO_ETHERIP":
        return IPPROTO_ETHERIP
    elif string == "IPPROTO_ENCAP":
        return IPPROTO_ENCAP
    elif string == "IPPROTO_APES":
        return IPPROTO_APES
    elif string == "IPPROTO_GMTP":
        return IPPROTO_GMTP
    elif string == "IPPROTO_PIM":
        return IPPROTO_PIM
    elif string == "IPPROTO_IPCOMP":
        return IPPROTO_IPCOMP
    elif string == "IPPROTO_PGM":
        return IPPROTO_PGM
    elif string == "IPPROTO_SCTP":
        return IPPROTO_SCTP
    elif string == "IPPROTO_DIVERT":
        return IPPROTO_DIVERT
    elif string == "IPPROTO_RAW":
        return IPPROTO_RAW
    elif string == "IPPROTO_MAX":
        return IPPROTO_MAX
    elif string == "IPPROTO_DONE":
        return IPPROTO_DONE
    elif string == "PF_UNSPEC":
        return PF_UNSPEC
    elif string == "PF_LOCAL":
        return PF_LOCAL
    elif string == "PF_UNIX":
        return PF_UNIX
    elif string == "PF_FILE":
        return PF_FILE
    elif string == "PF_INET":
        return PF_INET
    elif string == "PF_IMPLINK":
        return PF_IMPLINK
    elif string == "PF_PUP":
        return PF_PUP
    elif string == "PF_CHAOS":
        return PF_CHAOS
    elif string == "PF_NS":
        return PF_NS
    elif string == "PF_ISO":
        return PF_ISO
    elif string == "PF_OSI":
        return PF_OSI
    elif string == "PF_ECMA":
        return PF_ECMA
    elif string == "PF_DATAKIT":
        return PF_DATAKIT
    elif string == "PF_CCITT":
        return PF_CCITT
    elif string == "PF_SNA":
        return PF_SNA
    elif string == "PF_DECnet":
        return PF_DECnet
    elif string == "PF_DLI":
        return PF_DLI
    elif string == "PF_LAT":
        return PF_LAT
    elif string == "PF_HYLINK":
        return PF_HYLINK
    elif string == "PF_APPLETALK":
        return PF_APPLETALK
    elif string == "PF_ROUTE":
        return PF_ROUTE
    elif string == "PF_LINK":
        return PF_LINK
    elif string == "PF_XTP":
        return PF_XTP
    elif string == "PF_COIP":
        return PF_COIP
    elif string == "PF_CNT":
        return PF_CNT
    elif string == "PF_SIP":
        return PF_SIP
    elif string == "PF_IPX":
        return PF_IPX
    elif string == "PF_RTIP":
        return PF_RTIP
    elif string == "PF_PIP":
        return PF_PIP
    elif string == "PF_NDRV":
        return PF_NDRV
    elif string == "PF_ISDN":
        return PF_ISDN
    elif string == "PF_KEY":
        return PF_KEY
    elif string == "PF_INET6":
        return PF_INET6
    elif string == "PF_NATM":
        return PF_NATM
    elif string == "PF_SYSTEM":
        return PF_SYSTEM
    elif string == "PF_NETBIOS":
        return PF_NETBIOS
    elif string == "PF_PPP":
        return PF_PPP
    elif string == "PF_RESERVED_36":
        return PF_RESERVED_36
    elif string == "PF_MAX":
        return PF_MAX
    elif string == "SOMAXCONN":
        return SOMAXCONN
    elif string == "MSG_OOB":
        return MSG_OOB
    elif string == "MSG_PEEK":
        return MSG_PEEK
    elif string == "MSG_DONTROUTE":
        return MSG_DONTROUTE
    elif string == "MSG_EOR":
        return MSG_EOR
    elif string == "MSG_TRUNC":
        return MSG_TRUNC
    elif string == "MSG_CTRUNC":
        return MSG_CTRUNC
    elif string == "MSG_WAITALL":
        return MSG_WAITALL
    elif string == "MSG_DONTWAIT":
        return MSG_DONTWAIT
    elif string == "MSG_EOF":
        return MSG_EOF
    elif string == "MSG_WAITSTREAM":
        return MSG_WAITSTREAM
    elif string == "MSG_FLUSH":
        return MSG_FLUSH
    elif string == "MSG_HOLD":
        return MSG_HOLD
    elif string == "MSG_SEND":
        return MSG_SEND
    elif string == "MSG_HAVEMORE":
        return MSG_HAVEMORE
    elif string == "MSG_RCVMORE":
        return MSG_RCVMORE
    elif string == "MSG_NEEDSA":
        return MSG_NEEDSA
    elif string == "SHUT_RD":
        return SHUT_RD
    elif string == "SHUT_WR":
        return SHUT_WR
    elif string == "SHUT_RDWR":
        return SHUT_RDWR
    elif string == "SO_DEBUG":
        return SO_DEBUG
    elif string == "SO_ACCEPTCONN":
        return SO_ACCEPTCONN
    elif string == "SO_REUSEADDR":
        return SO_REUSEADDR
    elif string == "SO_KEEPALIVE":
        return SO_KEEPALIVE
    elif string == "SO_DONTROUTE":
        return SO_DONTROUTE
    elif string == "SO_BROADCAST":
        return SO_BROADCAST
    elif string == "SO_USELOOPBACK":
        return SO_USELOOPBACK
    elif string == "SO_LINGER":
        return SO_LINGER
    elif string == "SO_OOBINLINE":
        return SO_OOBINLINE
    elif string == "SO_REUSEPORT":
        return SO_REUSEPORT
    elif string == "SO_TIMESTAMP":
        return SO_TIMESTAMP
    elif string == "SO_ACCEPTFILTER":
        return SO_ACCEPTFILTER
    elif string == "SO_DONTTRUNC":
        return SO_DONTTRUNC
    elif string == "SO_WANTMORE":
        return SO_WANTMORE
    elif string == "SO_WANTOOBFLAG":
        return SO_WANTOOBFLAG
    elif string == "SO_SNDBUF":
        return SO_SNDBUF
    elif string == "SO_RCVBUF":
        return SO_RCVBUF
    elif string == "SO_SNDLOWAT":
        return SO_SNDLOWAT
    elif string == "SO_RCVLOWAT":
        return SO_RCVLOWAT
    elif string == "SO_SNDTIMEO":
        return SO_SNDTIMEO
    elif string == "SO_RCVTIMEO":
        return SO_RCVTIMEO
    elif string == "SO_ERROR":
        return SO_ERROR
    elif string == "SO_TYPE":
        return SO_TYPE
    elif string == "SO_NREAD":
        return SO_NREAD
    elif string == "SO_NKE":
        return SO_NKE
    elif string == "SO_NOSIGPIPE":
        return SO_NOSIGPIPE
    elif string == "SO_NOADDRERR":
        return SO_NOADDRERR
    elif string == "SO_NWRITE":
        return SO_NWRITE
    elif string == "SO_REUSESHAREUID":
        return SO_REUSESHAREUID
    elif string == "SO_NOTIFYCONFLICT":
        return SO_NOTIFYCONFLICT
    elif string == "SO_UPCALLCLOSEWAIT":
        return SO_UPCALLCLOSEWAIT
    elif string == "SO_LINGER_SEC":
        return SO_LINGER_SEC
    elif string == "SO_RESTRICTIONS":
        return SO_RESTRICTIONS
    elif string == "SO_RESTRICT_DENYIN":
        return SO_RESTRICT_DENYIN
    elif string == "SO_RESTRICT_DENYOUT":
        return SO_RESTRICT_DENYOUT
    elif string == "SO_RESTRICT_DENYSET":
        return SO_RESTRICT_DENYSET
    elif string == "SO_RANDOMPORT":
        return SO_RANDOMPORT
    elif string == "SO_NP_EXTENSIONS":
        return SO_NP_EXTENSIONS
    elif string == "SO_LABEL":
        return SO_LABEL
    elif string == "SO_PEERLABEL":
        return SO_PEERLABEL
    elif string == "TCP_NODELAY":
        return TCP_NODELAY
    elif string == "TCP_MAXSEG":
        return TCP_MAXSEG
    elif string == "TCP_NOPUSH":
        return TCP_NOPUSH
    elif string == "TCP_NOOPT":
        return TCP_NOOPT
    elif string == "TCP_KEEPALIVE":
        return TCP_KEEPALIVE
    elif string == "TCP_CONNECTIONTIMEOUT":
        return TCP_CONNECTIONTIMEOUT
    elif string == "PERSIST_TIMEOUT":
        return PERSIST_TIMEOUT
    elif string == "TCP_RXT_CONNDROPTIME":
        return TCP_RXT_CONNDROPTIME
    elif string == "TCP_RXT_FINDROP":
        return TCP_RXT_FINDROP
    elif string == "SOL_SOCKET":
        return SOL_SOCKET
    elif string == "SOL_TCP":
        return SOL_TCP
    elif string == "SOL_UDP":
        return SOL_UDP
    elif string == "F_OK":
        return F_OK
    elif string == "X_OK":
        return X_OK
    elif string == "W_OK":
        return W_OK
    elif string == "R_OK":
        return R_OK
    elif string == "O_RDONLY":
        return O_RDONLY
    elif string == "O_WRONLY":
        return O_WRONLY
    elif string == "O_RDWR":
        return O_RDWR
    elif string == "O_RDWRFLAGS":
        return O_RDWRFLAGS
    elif string == "O_CREAT":
        return O_CREAT
    elif string == "O_EXCL":
        return O_EXCL
    elif string == "O_NOCTTY":
        return O_NOCTTY
    elif string == "O_TRUNC":
        return O_TRUNC
    elif string == "O_APPEND":
        return O_APPEND
    elif string == "O_NONBLOCK":
        return O_NONBLOCK
    elif string == "O_SYNC":
        return O_SYNC
    elif string == "O_ASYNC":
        return O_ASYNC
    elif string == "S_IRWXA":
        return S_IRWXA
    elif string == "S_IRWXU":
        return S_IRWXU
    elif string == "S_IRUSR":
        return S_IRUSR
    elif string == "S_IWUSR":
        return S_IWUSR
    elif string == "S_IXUSR":
        return S_IXUSR
    elif string == "S_IRWXG":
        return S_IRWXG
    elif string == "S_IRGRP":
        return S_IRGRP
    elif string == "S_IWGRP":
        return S_IWGRP
    elif string == "S_IXGRP":
        return S_IXGRP
    elif string == "S_IRWXO":
        return S_IRWXO
    elif string == "S_IROTH":
        return S_IROTH
    elif string == "S_IWOTH":
        return S_IWOTH
    elif string == "S_IXOTH":
        return S_IXOTH
    elif string == "S_IFBLK":
        return S_IFBLK
    elif string == "S_IFCHR":
        return S_IFCHR
    elif string == "S_IFDIR":
        return S_IFDIR
    elif string == "S_IFIFO":
        return S_IFIFO
    elif string == "S_IFLNK":
        return S_IFLNK
    elif string == "S_IFREG":
        return S_IFREG
    elif string == "S_IFSOCK":
        return S_IFSOCK
    elif string == "S_FILETYPEFLAGS":
        return S_FILETYPEFLAGS
    elif string == "S_IWRITE":
        return S_IWRITE
    elif string == "S_ISUID":
        return S_ISUID
    elif string == "S_IREAD":
        return S_IREAD
    elif string == "S_ENFMT":
        return S_ENFMT
    elif string == "S_ISGID":
        return S_ISGID
    elif string == "SEEK_SET":
        return SEEK_SET
    elif string == "SEEK_CUR":
        return SEEK_CUR
    elif string == "SEEK_END":
        return SEEK_END
    elif string == "F_DUPFD":
        return F_DUPFD
    elif string == "F_GETFD":
        return F_GETFD
    elif string == "F_SETFD":
        return F_SETFD
    elif string == "F_GETFL":
        return F_GETFL
    elif string == "F_SETFL":
        return F_SETFL
    elif string == "F_GETLK":
        return F_GETLK
    elif string == "F_GETLK64":
        return F_GETLK64
    elif string == "F_SETLK":
        return F_SETLK
    elif string == "F_SETLK64":
        return F_SETLK64
    elif string == "F_SETLKW":
        return F_SETLKW
    elif string == "F_SETLKW64":
        return F_SETLKW64
    elif string == "F_SETOWN":
        return F_SETOWN
    elif string == "F_GETOWN":
        return F_GETOWN
    elif string == "F_SETSIG":
        return F_SETSIG
    elif string == "F_GETSIG":
        return F_GETSIG
    elif string == "F_SETLEASE":
        return F_SETLEASE
    elif string == "F_GETLEASE":
        return F_GETLEASE
    elif string == "F_NOTIFY":
        return F_NOTIFY
    elif string == "F_RDLCK":
        return F_RDLCK
    elif string == "F_WRLCK":
        return F_WRLCK
    elif string == "F_UNLCK":
        return F_UNLCK
    elif string == "F_EXLCK":
        return F_EXLCK
    elif string == "F_SHLCK":
        return F_SHLCK
    elif string == "PATH_MAX":
        return PATH_MAX
    elif string == "MAX_FD":
        return MAX_FD
    elif string == "DT_UNKNOWN":
        return DT_UNKNOWN
    elif string == "DT_FIFO":
        return DT_FIFO
    elif string == "DT_CHR":
        return DT_CHR
    elif string == "DT_DIR":
        return DT_DIR
    elif string == "DT_BLK":
        return DT_BLK
    elif string == "DT_REG":
        return DT_REG
    elif string == "DT_LNK":
        return DT_LNK
    elif string == "DT_SOCK":
        return DT_SOCK
    elif string == "DT_WHT":
        return DT_WHT
    # Parameters that don't translate to POSIX model but are often used...

    # Ignoring MSG_NOSIGNAL
    elif string == "MSG_NOSIGNAL":
        return 0
    # Ignoring SOCK_CLOEXEC because it seems to be needed more for multi-threading
    elif string == "SOCK_CLOEXEC":
        return 0
    # SOCK_NONBLOCK is the same as O_NONBLOCK
    elif string == "SOCK_NONBLOCK":
        return O_NONBLOCK
    else:
        if DEBUG:
            log("INVALID CONSTANT: " + string, '\n')
        return UNIMPLEMENTED_ERROR

        
'''
# For testing purposes...
def main():
    fh = open(FILE_NAME, "r")
    trace = getNumberValidTraceLines(fh, -1)
    for action in trace:
        log(action)

main()
'''
