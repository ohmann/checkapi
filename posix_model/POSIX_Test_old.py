###########
# IMPORTS #
###########
from lind_fs_constants import *
from lind_net_constants import *

def do_nothing(*args):
    pass

#############
# CONSTANTS #
#############
UNIMPLEMENTED_ERROR = -1
FILE_NAME = "skype.strace_network"
#FILE_NAME = "ktorrent.strace_full"
#FILE_NAME = "firefox.strace_full"
DEBUG = False
TRACE = []

###########
# STRUCTS #
###########
class fds(object):
    def __init__(self, stracefd, posixfd):
        self.stracefd = stracefd
        self.posixfd = posixfd


#############
# FUNCTIONS #
#############
def testStraces(fileName):
    fdTable = []
    # Open the file and process each line
    fh = open(fileName, 'r')
    for line in fh:
        # Ignore SIGS
        if line[:3] == "---":
            continue

        # Get the first command name, parameters, and result
        if line[0] == '[':
            command = line[line.find(']')+2:line.find('(')]
        else:
	    command = line[:line.find('(')]
        parameterChunk = line[line.find('(')+1:line.rfind('=')].strip()
        parameters = parameterChunk[:-1].split(", ")
        straceResult = line[line.rfind('=')+2:].strip()

        # Is the result a status number or error message?
        if len(straceResult.split(" ")) > 1:
            straceResult = straceResult[:straceResult.find(" ")]
        # Apparently the strace result can also be a ?...
        try:
            straceResult = int(straceResult)
        except:
            pass

        # Convert parameters into ints, execute, and assert ==

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
                print command, domain, socktype, protocol, straceResult
            if domain == UNIMPLEMENTED_ERROR or socktype == UNIMPLEMENTED_ERROR or protocol == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    print "Unimplemented parameter, skipping..."
            else:
                TRACE.append(('socket_syscall', (domain,socktype, protocol), straceResult))
                pass
                #result = socket_syscall(domain, socktype, protocol)
                #assert (result >= 0 and straceResult >= 0) or (result < 0 and straceResult < 0)
                #fdTable.append(fds(straceResult, result))

        ##### BIND #####
        elif command == "bind":
            sockfd = straceToPosixFD(fdTable, int(parameters[0]))

            localip = UNIMPLEMENTED_ERROR
            localport = UNIMPLEMENTED_ERROR
            for index in range(1,len(parameters)-1, 1):
                p = parameters[index]
                if p.find("sin_addr") != -1:
                    localip = p[p.find("\"")+1:p.rfind("\"")]
                elif p.find("sin_port") != -1:
                    localport = int(p[p.find("(")+1:p.rfind(")")])

            if DEBUG:
                print command, sockfd, localip, localport, straceResult
            if localip == UNIMPLEMENTED_ERROR or localport == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    print "Unimplemented parameter, skipping..."
            else:
                TRACE.append(('bind_syscall',(sockfd, localip, localport), straceResult))
                pass
                #result = bind_syscall(sockfd, localip, localport)
                #assert result == straceResult

        ##### CONNECT #####
        elif command == "connect":
            sockfd = straceToPosixFD(fdTable, int(parameters[0]))

            remoteip = UNIMPLEMENTED_ERROR
            remoteport = UNIMPLEMENTED_ERROR
            for index in range(1,len(parameters)-1, 1):
                p = parameters[index]
                if p.find("sin_addr") != -1:
                    remoteip = p[p.find("\"")+1:p.rfind("\"")]
                elif p.find("sin_port") != -1:
                    remoteport = int(p[p.find("(")+1:p.rfind(")")])

            if DEBUG:
                print command, sockfd, remoteip, remoteport, straceResult
            if remoteip == UNIMPLEMENTED_ERROR or remoteport == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    print "Unimplemented parameter, skipping..."
            else:
                TRACE.append(('connect_syscall',(sockfd, remoteip, remoteport), straceResult))
                pass
                #result = connect_syscall(sockfd, remoteip, remoteport)
                #assert result == straceResult

        # BUG: If message contains a ", " it will mess up send and recieve related strace parsing
        # BUG: If message is larger than a certain length then strace will cut it off with '...' which could cause a false failure in comparison
        ##### SENDTO #####
        elif command == "sendto":
            sockfd = straceToPosixFD(fdTable, int(parameters[0]))

            # Get the message without quotes
	    message = parameters[1].strip("...")[1:len(parameters[1])-1]

            try:
                flags = int(parameters[3])
            except:
                flags = splitAndCombine(parameters[3])

            remoteip = UNIMPLEMENTED_ERROR
            remoteport = UNIMPLEMENTED_ERROR
            for index in range(4,len(parameters)-1, 1):
                p = parameters[index]
                if p.find("sin_addr") != -1:
                    remoteip = p[p.find("\"")+1:p.rfind("\"")]
                elif p.find("sin_port") != -1:
                    remoteport = int(p[p.find("(")+1:p.rfind(")")])
            
            if DEBUG:
                print command, sockfd, message, remoteip, remoteport, flags, straceResult
            if remoteip == UNIMPLEMENTED_ERROR or remoteport == UNIMPLEMENTED_ERROR or flags == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    print "Unimplemented parameter, skipping..."
            else:
                TRACE.append(('sendto_syscall',(sockfd, message, remoteip, remoteport, flags), straceResult))
                pass
                #result = sendto_syscall(sockfd, message, remoteip, remoteport, flags)
                #assert result == straceResult

        ##### SEND #####
        elif command == "send":
            sockfd = straceToPosixFD(fdTable, int(parameters[0]))

            # Get the message without quotes
	    message = parameters[1].strip("...")[1:len(parameters[1])-1]

            try:
                flags = int(parameters[3])
            except:
                flags = splitAndCombine(parameters[3])

            if DEBUG:
                print command, sockfd, message, flags, straceResult
            if flags == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    print "Unimplemented parameter, skipping..."
            else:
                TRACE.append(('send_syscall',(sockfd, message, flags), straceResult))
                pass
                #result = send_syscall(sockfd, message, flags)
                #assert result == straceResult

        ##### RECVFROM #####
        elif command == "recvfrom":
            sockfd = straceToPosixFD(fdTable, int(parameters[0]))

            # Get the message without quotes
	    message = parameters[1].strip("...")[1:len(parameters[1])-1]

	    length = int(parameters[2])

            try:
                flags = int(parameters[3])
            except:
                flags = splitAndCombine(parameters[3])

            remoteip = UNIMPLEMENTED_ERROR
            remoteport = UNIMPLEMENTED_ERROR
            for index in range(4,len(parameters)-1, 1):
                p = parameters[index]
                if p.find("sin_addr") != -1:
                    remoteip = p[p.find("\"")+1:p.rfind("\"")]
                elif p.find("sin_port") != -1:
                    remoteport = int(p[p.find("(")+1:p.rfind(")")])
            
            if DEBUG:
                print command, sockfd, message, remoteip, remoteport, flags, straceResult
            if remoteip == UNIMPLEMENTED_ERROR or remoteport == UNIMPLEMENTED_ERROR or flags == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    print "Unimplemented parameter, skipping..."
            else:
                TRACE.append(('recvfrom_syscall',(sockfd, length, flags), message))
                pass
                #result = recvfrom_syscall(sockfd, length, flags)
		#if len(result) == 1:
                    #assert result == message
                    # Or to avoid the problem with the strace cutting off the full message use the assert below instead
                    #assert result.find(message) != -1
                #else:
                    #assert result[:2] == (remoteip, remoteport) and result[2].find(message) != -1

        ##### RECV #####
        elif command == "recv":
            sockfd = straceToPosixFD(fdTable, int(parameters[0]))

            # Get the message without quotes
	    message = parameters[1].strip("...")[1:len(parameters[1])-1]

	    length = int(parameters[2])

            try:
                flags = int(parameters[3])
            except:
                flags = splitAndCombine(parameters[3])

            if DEBUG:
                print command, sockfd, length, flags, straceResult
            if flags == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    print "Unimplemented parameter, skipping..."
            else:
                TRACE.append(('recv_syscall',(sockfd, length, flags), message))
                pass
                #result = recv_syscall(sockfd, length, flags)
                #assert result.find(message) != -1

        ##### GETSOCKNAME #####
        elif command == "getsockname":
            sockfd = straceToPosixFD(fdTable, int(parameters[0]))

            localip = UNIMPLEMENTED_ERROR
            localport = UNIMPLEMENTED_ERROR
            for index in range(1,len(parameters)-1, 1):
                p = parameters[index]
                if p.find("sin_addr") != -1:
                    localip = p[p.find("\"")+1:p.rfind("\"")]
                elif p.find("sin_port") != -1:
                    localport = int(p[p.find("(")+1:p.rfind(")")])
            
            if DEBUG:
                print command, sockfd, localip, localport, straceResult
            if localip == UNIMPLEMENTED_ERROR or localport == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    print "Unimplemented parameter, skipping..."
            else:
                TRACE.append(('getsockname_syscall',(sockfd,), (localip, localport)))
                pass
                #result = getsockname_syscall(sockfd)
                #assert result == (localip, localport)

        ##### GETPEERNAME #####
        elif command == "getpeername":
            sockfd = straceToPosixFD(fdTable, int(parameters[0]))

            remoteip = UNIMPLEMENTED_ERROR
            remoteport = UNIMPLEMENTED_ERROR
            for index in range(1,len(parameters)-1, 1):
                p = parameters[index]
                if p.find("sin_addr") != -1:
                    remoteip = p[p.find("\"")+1:p.rfind("\"")]
                elif p.find("sin_port") != -1:
                    remoteport = int(p[p.find("(")+1:p.rfind(")")])

            if DEBUG:
                print command, sockfd, remoteip, remoteport, straceResult
            if remoteip == UNIMPLEMENTED_ERROR or remoteport == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    print "Unimplemented parameter, skipping..."
            else:
                TRACE.append(('getpeername_syscall',(sockfd,), (remoteip, remoteport)))
                pass
                #result = getpeername_syscall(sockfd)
                #assert result == (remoteip, remoteport)

        ##### LISTEN  #####
        elif command == "listen":
            sockfd = straceToPosixFD(fdTable, int(parameters[0]))

            try:
                backlog = int(parameters[1])
            except:
                backlog = splitAndCombine(parameters[1])

            if DEBUG:
                print command, sockfd, backlog, straceResult
            TRACE.append(('listen_syscall',(sockfd, backlog), straceResult))
            #result = listen_syscall(sockfd, backlog)
            #assert result == straceResult

        ##### ACCEPT #####
        elif command == "accept":
            sockfd = straceToPosixFD(fdTable, int(parameters[0]))

            remoteip = UNIMPLEMENTED_ERROR
            remoteport = UNIMPLEMENTED_ERROR
            for index in range(1,len(parameters)-1, 1):
                p = parameters[index]
                if p.find("sin_addr") != -1:
                    remoteip = p[p.find("\"")+1:p.rfind("\"")]
                elif p.find("sin_port") != -1:
                    remoteport = int(p[p.find("(")+1:p.rfind(")")])

            if DEBUG:
                print command, sockfd, remoteip, remoteport, straceResult
            if remoteip == UNIMPLEMENTED_ERROR or remoteport == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    print "Unimplemented parameter, skipping..."
            else:
                TRACE.append(('accept_syscall',(sockfd,), straceResult))
                pass
                #result = accept_syscall(sockfd)
                #assert (result >= 0 and straceResult >= 0) or (result < 0 and straceResult < 0)
                #fdTable.append(fds(straceResult, result))

        ##### GETSOCKOPT #####
        elif command == "getsockopt":
            sockfd = straceToPosixFD(fdTable, int(parameters[0]))

            try:
                level = int(parameters[1])
            except:
                level = splitAndCombine(parameters[1])

            try:
                optname = int(parameters[2])
            except:
                optname = splitAndCombine(parameters[2])

            if DEBUG:
                print command, sockfd, level, optname, straceResult
            if level == UNIMPLEMENTED_ERROR or optname == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    print "Unimplemented parameter, skipping..."
            else:
                TRACE.append(('getsockopt_syscall',(sockfd, level, optname), straceResult))
                pass
                #result = getsockopt_syscall(sockfd, level, optname)
                #assert result == straceResult

        ##### SETSOCKOPT #####
        elif command == "setsockopt":
            sockfd = straceToPosixFD(fdTable, int(parameters[0]))

            try:
                level = int(parameters[1])
            except:
                level = splitAndCombine(parameters[1])

            try:
                optname = int(parameters[2])
            except:
                optname = splitAndCombine(parameters[2])

            optval = int(parameters[3].strip("[]"))

            if DEBUG:
                print command, sockfd, level, optname, optval, straceResult
            if level == UNIMPLEMENTED_ERROR or optname == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    print "Unimplemented parameter, skipping..."
            else:
                TRACE.append(('setsockopt_syscall',(sockfd, level, optname, optval), straceResult))
                pass
                #result = setsockopt_syscall(sockfd, level, optname, optval)
                #assert result == straceResult


        ##### SHUTDOWN #####
        elif command == "shutdown":
            sockfd = straceToPosixFD(fdTable, int(parameters[0]))

            try:
                how = int(parameters[1])
            except:
                how = splitAndCombine(parameters[1])

            if DEBUG:
                print command, sockfd, how, straceResult
            if how == UNIMPLEMENTED_ERROR:
                if DEBUG:
                    print "Unimplemented parameter, skipping..."
            else:
                TRACE.append(('setshutdown_syscall',(sockfd, how), straceResult))
                pass
                #result = setshutdown_syscall(sockfd, how)
                #assert result == straceResult
                #removeFD(fdTable, sockfd)

        ##### SOCKETPAIR #####

        ##### RECVMSG #####
#        elif command == "recvmsg":
#            sockfd = straceToPosixFD(fdTable, int(parameters[0]))
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
#                print command, sockfd, message, flags, straceResult
#            if message == UNIMPLEMENTED_ERROR or flags == UNIMPLEMENTED_ERROR:
#                if DEBUG:
#                    print "Unimplemented parameter, skipping..."
#            else:
#                pass
#                #result = recvmsg_syscall(sockfd, flags)
#                #assert result == message
#
        ##### SENDMSG #####
#        elif command == "sendmsg":
#            sockfd = straceToPosixFD(fdTable, int(parameters[0]))
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
#                print command, sockfd, message, flags, straceResult
#            if message == UNIMPLEMENTED_ERROR or flags == UNIMPLEMENTED_ERROR:
#                if DEBUG:
#                    print "Unimplemented parameter, skipping..."
#            else:
#                pass
#                #result = sendmsg_syscall(sockfd, message, flags)
#                #assert result == straceResult
#
        ##### NOT IMPLEMENTED #####
        else:
            if DEBUG:
                print "Command " + command + " currently not supported. Skipping..."

        if DEBUG:
            print

def removeFD(fdlst, posixfd):
    for index in fdlst:
        if fdlst[index].posixfd == posixfd:
            fdlst.pop(index)
            return


def straceToPosixFD(fdlst, stracefd):
    for aFds in fdlst:
        if aFds.stracefd == stracefd:
            return aFds.posixfd
    return stracefd


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
    # Parameters that don't translate to POSIX model but are often used...
    # Ignoring MSG_NOSIGNAL
    elif string == "MSG_NOSIGNAL":
        return 0
    # PF_UNIX is a synonym for PF_FILE
    elif string == "PF_FILE":
        return PF_UNIX
    # Ignoring SOCK_CLOEXEC because it seems to be needed more for multi-threading
    elif string == "SOCK_CLOEXEC":
        return 0
    # SOCK_NONBLOCK is the same as O_NONBLOCK
    elif string == "SOCK_NONBLOCK":
        return O_NONBLOCK
    else:
        if DEBUG:
            print "INVALID CONSTANT: " + string
        return UNIMPLEMENTED_ERROR

        

# For testing purposes...
def main():
    testStraces(FILE_NAME)
    for action in TRACE:
      name, args, ret = action
      print name + str(args), '->', ret

main()
