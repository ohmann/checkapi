###########
# IMPORTS #
###########

### Use with Repy ###
dy_import_module_symbols("lind_fs_constants")
dy_import_module_symbols("lind_net_constants")


#############
# CONSTANTS #
#############
ALL_COMMANDS = ["socket", "bind", "connect", "sendto", "send", "recvfrom", "recv", "getsockname", "getpeername", "listen", "accept", "getsockopt", "setsockopt", "shutdown", "close", "fstatfs", "statfs", "access", "chdir", "mkdir", "rmdir", "link", "unlink", "stat", "fstat", "open", "creat", "lseek", "read", "write", "dup2", "dup", "fcntl", "getdents", "pipe", "eventfd", "eventfd2", "dup3", "inotify_init", "inotify_init1"]
UNIMPLEMENTED_ERROR = -1
#FILE_NAME = "skype.strace_network"
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

            message += "*" * (int(parameters[2]) - len(message))

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

            message += "*" * (int(parameters[2]) - len(message))

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
                TRACE.append(('recvfrom_syscall',(sockfd, message, length, flags, remoteip, remoteport), straceResult))

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
    return stringParts


# For testing purposes...
'''
def main():
    fh = open(FILE_NAME, "r")
    trace = getNumberValidTraceLines(fh, -1)
    for action in trace:
        log(action)

main()
'''
