#!/usr/bin/python           # This is the chat server application

#Roy Cheung
#CSCI 367
#W01024078

#Needs to accept multiple incoming connections from clients
#Parse incoming messages and broadcast to all other clients
from random import choice
import socket, select, sys, Queue, getopt, re


############################################################### CONSTANTS/VARIABLES
connections = []

players = []
lobby = []
activeplayers = []

incoming_buffer = 4096
lobby_timeout = 0
min_players = 0
max_players = 30
action_timeout = 30

active_clients = 0
running = True
debug_flag = False

#TODO: names, not remove spaces from the messages! Also need to do sending to any. Also fix the thing where people are getting disconnected.

class Player():
    def __init__(self, address, socket):
        self.name = ''
        self.strikes = 0
        self.socket = socket
        self.address = address
        self.buffer_string = ''
        self.inLobby = False
        self.isActive = False

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[96m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

def remove_player(sock):
    for person in players:
        if sock == person.socket:
            players.remove(person)
            broadstat("(sstat({}))".format(current_players()))


def find_player_by_sock(sock):
    for person in players:
        if sock == person.socket:
            return person


def find_player_by_name(name):
    for person in players:
        if name == person.name:
            return person


def current_players():
    playernames = ''
    for person in players:
        if person.name != '':
            playernames = playernames + "," + person.name
    return playernames[1:len(playernames)]

def current_num_players():
    num = 0
    for person in players:
        if person.name != '':
            num += 1
    return num

def send_this_stuff(thissocket, message):
    try:
        thissocket.send(message)
    except:
        if debug_flag:
            print "send_this_stuff exception raised"
        thissocket.close()
        connections.remove(thissocket)
        remove_player(thissocket)

def any_send(fromc, message):
    send_this_stuff(choice(players).socket, "(schat({})({}))".format(fromc, message))

def broadcast(fromc, message):
    for play in players:
        send_this_stuff(play.socket, "(schat({})({}))".format(fromc, message))

def broadstat(message):
    # if len(players) > 0:
    for play in players:
        send_this_stuff(play.socket, message)
#check someone disconnected, use some signal thing.

###############################################################                                           #TODO THIS.

def cchat(names, message, fromc, sock):
    if find_player_by_sock(sock).name != '':
        names = names.replace(" ", "")
        namelist = re.split(',', names)
        if len(names) > 389:
            cstrike(sock, "toolong")
        else:
            for i in namelist:
                if len(namelist) == 1 and i == "ALL":
                    broadcast(fromc, message)
                elif len(namelist) == 1 and i == "ANY":
                    any_send(fromc, message)
                else:
                    if debug_flag:
                        print i
                    if find_player_by_name(i):
                        send_this_stuff(find_player_by_name(i).socket, ("(schat({})({}))".format(fromc, message)))
                    else:
                        cstrike(sock, "malformed")
    else:
        cstrike(sock, "malformed")


def cjoin(sock, name):
    new_name = new_user_name(name, sock)
    if new_name == "*****":
        cstrike(sock, "malformed")
    else:
        find_player_by_sock(sock).name = new_name
        hell = current_players()
        send_this_stuff(sock, "(sjoin({})({})({},{},{}))".format(new_name, hell, min_players, lobby_timeout, action_timeout))
        for player in players:
            if player.socket != sock and player.name != '':
                send_this_stuff(player.socket, "(sstat({}))".format(current_players()))


def cstat(dest):
    send_this_stuff(dest, "(sstat({}))".format(current_players()))

def cstrike(sock, reason):
    find_player_by_sock(sock).strikes += 1
    strike_num = find_player_by_sock(sock).strikes
    if strike_num < 3:
        send_this_stuff(sock, "(strike({})({}))".format(strike_num, reason))
    else:
        send_this_stuff(sock, "(strike({})({}))".format(strike_num, reason))
        remove_player(sock)

###############################################################             #Subtools used for stripping chars, and name verification
def strip_non_ascii(string):
    ''' Returns the string without any special and delete of ASCII'''
    stripped = (c for c in string if 31 < ord(c) < 127)
    return ''.join(stripped)

def name_strip(string):
    ''' removes all invalid characters from name '''
    stripped = (c for c in string if ord(c) == 46 or ord(c) in range(48, 58) or ord(c) in range(65, 91) or ord(c) in range(97, 123))
    return ''.join(stripped)

def new_user_name(name, sock):
    name = name.upper()
    name = name_strip(name)
    while (name.count(".") > 1):
        (startn, dot, endin) = name.partition(".")
        name = startn + endin
    (startn, dot, endin) = name.partition(".")
    if len(startn) > 8:
        startn = startn[0:8]
    if len(endin) > 3:
        endin = endin[0:3]
    name = startn + dot + endin
    if (name == "ALL" or name == "ANY" or name == ''):
        name = "*****"
    if find_player_by_name(name):
        (startn, dot, endin) = name.partition(".")
        startn = startn[0:6] + "~1"
        name = startn + dot + endin
    while find_player_by_name(name):
        (startn, dot, endin) = name.partition(".")
        preName, tilde, num = startn.partition("~")
        nameNumber = int(num)
        nameNumber += 1
        if nameNumber == 10:
            startn = preName[0:5] + tilde + str(nameNumber)
        else:
            startn = preName + tilde + str(nameNumber)
        name = startn + dot + endin
    return name

def process_dis(sock):
    buffers = find_player_by_sock(sock).buffer_string
    buffers = strip_non_ascii(buffers)
    state = 0
    name = ""
    message = ""
    reSync = False
    NotGood = True
    msglength = 481

    # cmand = False
    i = 0
    print bcolors.WARNING + buffers + bcolors.ENDC
    # if len(buffers) > msglength:
    #     cstrike(sock, "toolong")
    #     buffers = ""
    #     find_player_by_sock(sock).buffer_string = buffers

    while i < msglength and i < len(buffers):
        # cmand = False
        if debug_flag:
            print "i: " + str(i)
            print "state: " + str(state)
            print "I AM AT: " + buffers[i]
            print buffers

        if state == 0 and buffers[i:i+2] == '(c' and not reSync:
            state = 1
            i += 2
            NotGood = True
        elif state == 0 and buffers[i:i+2] != '(c' and not reSync:
            reSync = True
            NotGood = True
        elif state == 1 and buffers[i:i+5] == 'join(' and not reSync:
            state = 21
            i += 5
            NotGood = False
        elif state == 1 and buffers[i:i+5] == 'chat(' and not reSync:
            state = 20
            i += 5
            NotGood = False
        elif state == 1 and buffers[i:i+5] == 'stat)' and not reSync:
            i += 5
            buffers = buffers[i:len(buffers)]
            find_player_by_sock(sock).buffer_string = buffers
            state = 0
            i = 0
            cstat(sock)
            NotGood = False
        elif state == 1 and NotGood and not reSync:
            reSync = True
        elif state == 21 and not reSync:
            while  i < len(buffers) and buffers[i] != ')' and not reSync:
                if buffers[i] == '(':
                    reSync = True
                else:
                    name += buffers[i]
                    if debug_flag:
                        print name
                    i += 1
            if i < len(buffers) and buffers[i] == ')':
                state = 31
                i += 1
            else:
                reSync = True
        elif state == 31 and not reSync:
            if buffers[i] == ')':
                if debug_flag:
                    print bcolors.OKGREEN + "Client cjoined with: ({})".format(name) + bcolors.ENDC
                cjoin(sock, name)
                name = ""
                i += 1
                state = 0
                buffers = buffers[i:]
                find_player_by_sock(sock).buffer_string = buffers
                if debug_flag:
                    print "Current Buffer: " + buffers
                i = 0
            else:
                reSync = True
                if debug_flag:
                    print "RESYNC AND STRIKE 3"
        elif state == 20 and not reSync:
            while i < len(buffers) and buffers[i] != ')' and not reSync:
                if buffers[i] == '(':
                    reSync = True
                else:
                    name += buffers[i]
                    # state = 30
                    i += 1
            if i < len(buffers) and buffers[i] == ')' and not reSync:
                state = 30
                i += 1
        elif state == 30 and not reSync:
            if buffers[i] == "(" and not reSync:
                state = 40
                i += 1
            else:
                reSync = True
        elif state == 40 and not reSync:
            harr = 0
            while i < len(buffers) and buffers[i] != ')' and not reSync:
                harr += 1
                if buffers[i] == '(':
                    reSync = True
                    i -= harr
                else:
                    message += buffers[i]
                    i += 1
                    # state = 50
            if i < len(buffers) and buffers[i] == ')' and not reSync:
                state = 50
                i += 1
        elif state == 50 and not reSync:
            if buffers[i] == ')' and not reSync:
                if debug_flag:
                    print bcolors.OKGREEN +  "SCHAT sent to ({}): ({})".format(name, message) + bcolors.ENDC
                fromc = find_player_by_sock(sock).name
                if len(message) > 80:
                    cstrike(sock, "toolong")
                else:
                    cchat(name.upper(), message, fromc, sock)
                state = 0
                name = ""
                message = ""
                i += 1
                buffers= buffers[i:]
                find_player_by_sock(sock).buffer_string = buffers
                i = 0
            else:
                reSync = True
        elif reSync:
            cstrike(sock, "malformed")
            while i < len(buffers):
                if buffers[i:i+2] != '(c':
                    i += 1
                elif buffers[i:i+2] == '(c':
                    buffers = buffers[i:]
                    find_player_by_sock(sock).buffer_string = buffers
                    # i = 0
                    break
                if i == len(buffers):
                    buffers = ""
                    find_player_by_sock(sock).buffer_string = buffers
                    break
            reSync = False
            i = 0
            state = 0
            name = ""
            message = ""
        else:
            continue


###############################################################
if __name__ == "__main__":

    ################################################ 								ARGUMENT HANDLING *TODO: ADD DATA TYPE CHECK
    def arguments(argv):
        global action_timeout, min_players, wait_time, debug_flag
        try:
            opts, args = getopt.getopt(argv, "t:l:m:hd", [])
        except getopt.GetoptError:
            print 'server.py -t <timeout> -l <lobby wait time> -m <min players>'
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print 'server.py -t <timeout> -l <lobby wait time> -m <min players>'
                sys.exit(1)
            elif opt == "-t":
                action_timeout = arg
                print "Timeout is set to: " + action_timeout
            elif opt == "-m":
                min_players = arg
                print "Minplayers is set to: " + min_players
            elif opt == "-l":
                wait_time = arg
                print "Waittime is set to: " + wait_time
            elif opt == "-d":
                debug_flag = True
                print "Debug Flag ON"

    arguments(sys.argv[1:])

    ################################################ 								BINDS AND SETS SOCKETS

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
        print bcolors.WARNING + "Failed to create socket. Error code: (), Error message: ({})".format(str(msg[0]), + msg[1]) + bcolors.ENDC
        sys.exit();


    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = 36703
    server_address = ('', port)
    print bcolors.HEADER + "Server claiming %s port %s" % server_address + bcolors.ENDC
    s.bind(server_address)
    s.listen(5)

    connections.append(s)  #Append server socket to input sockets list
    s.setblocking(0)
    ################################################ 						MAIN

    while running:
        #Select, yo.
        read_sockets, write_sockets, error_sockets = select.select(connections, [], [])
        for sock in read_sockets:
            #incoming connection
            if sock == s:
                try:
                    csock, address = s.accept()                                                                         #TODO: FIX THE PART WHERE THE CLINET JOINS BUT DOESN'T SEND A CJOIN. AND DISCONNECTS, STILL MAINTAINS IN PLAYERS. CAUSE NOTHING EVER GETS SENT TO THEM.
                    if current_num_players() == max_players:
                        send_this_stuff(csock, "(snovac)")
                        print bcolors.WARNING + "NO VACANCY." + bcolors.ENDC
                        csock.close()
                    else:
                        connections.append(csock)
                        if debug_flag:
                            print csock
                        players.append(Player(address, csock))
                        print bcolors.OKBLUE + "Client (%s, %s) connected" % address + bcolors.ENDC
                except:
                    continue
            else:
                try:
                    data = sock.recv(incoming_buffer)  #Gets broadcast, comes in as the string
                    if data:
                        temp_string = strip_non_ascii(data.decode())  #Decode data then strip non-print ascii.
                        find_player_by_sock(sock).buffer_string += temp_string  #add to the player's buffer_string after finding them in the list
                        process_dis(sock)
                    else:
                        try:
                            remove_player(sock)
                            sock.close()
                            connections.remove(sock)
                            print bcolors.OKBLUE + "Client (%s, %s) disconnected" % address + bcolors.ENDC
                        except Exception as e:
                             print bcolors.FAIL + "Exception raised: " + str(e) + bcolors.ENDC
                except Exception as E:
                    print bcolors.FAIL + "Exception raised: {}".format(str(E)) + bcolors.ENDC
                    print bcolors.WARNING + "Client (%s, %s) disconnected" % address + bcolors.ENDC
                    sock.close()
                    connections.remove(sock)
                    remove_player(sock)
                    continue
    s.close()
