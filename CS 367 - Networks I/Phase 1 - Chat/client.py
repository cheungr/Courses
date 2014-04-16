#!/usr/bin/python           # This is the chat client application

#Roy Cheung
#CSCI 367
#W01024078

#Needs to accept multiple incoming connections from clients
#Parse incoming messages and broadcast to all other clients
from random import choice, randint
import socket, select, sys, Queue, getopt, re, urllib, os

def restart_program():
    python = sys.executable
    os.execl(python, python, * sys.argv)

#main function
if __name__ == "__main__":

    def strip_non_ascii(string):
        ''' Returns the string without any special and delete of ASCII'''
        stripped = (c for c in string if 31 < ord(c) < 127)
        return ''.join(stripped)

    f = urllib.urlopen("https://cds.cheungr.com/content/quotes.html")
    s = f.read()
    f.close()
    quote_list = re.findall("<p>(.+)</p>", s)

################################################                                 CONSTANTS/VARIABLES
    manual_mode = False
    debug_mode = False
    running = True

    host = ""
    port = 36703
    name = "MIRA"
    incoming_buffer = 4096

    name_list = []

    connections = []
################################################                                 ARGUMENT HANDLING *TODO: ADD DATA TYPE CHECK
    def gen_message():
        return strip_non_ascii(choice(quote_list))

    def process_input(c, input_i):
        global name_list
        global name
        print input_i
        if input_i[0:6] == '(sstat':
            names = re.search("\(sstat\((.+)\)\)", input_i)
            names = names.group(1).replace(" ", "")
            name_list = names.split(",")
            random_doing(c)
        elif input_i[0:6] == '(schat':
            taken = re.search("\(schat\((.+)\)\((.+)\)\)", input_i)
            in_name = taken.group(1)
            message = taken.group(2)
            if debug_mode:
                print "Message from: {} | {}".format(in_name, message)
            if in_name != name:
                c.send("(cchat({})({}))".format(in_name, gen_message()))
        elif input_i[0:7] == '(strike':
            if debug_mode:
                print "Striked by Server. I'm a good client though!"
            random_doing(c)
        elif input_i[0:6] == '(sjoin':
            myname = re.search("\(sjoin\((.+)\)\(.+\)\(.+\)", input_i)
            name = myname.group(1)
            random_doing(c)

    def random_doing(c):
        global name
        rand = randint(1,4)
        if debug_mode:
            print "Sending to random person and all"
            print "This is rand: " + str(rand)
        if rand == 1:
            if len(name_list) > 1:
                this_name = choice(name_list)
                if this_name != name:
                    c.send("(cchat({})({}))".format(this_name, gen_message()))
        elif rand == 2:
            c.send("(cchat(ALL)({}))".format(gen_message()))
        elif rand == 3:
            c.send("(cstat)")

    def mahsa(c, input_a):
        if input_a[0] == "@":
            name_group = re.match("@(.+):", input_a)
            message_group = re.match("@.+:\s?(.+)", input_a)
            nameq = name_group.group(1)
            nameq = nameq.upper()
            message = message_group.group(1)
            nameq = nameq.replace(" ", "")
            c.send("(cchat({})({}))".format(nameq, message))
        if input_a == 'stat':
            c.send("(cstat)")

    def arguments (argv):
        global manual_mode, debug_mode, host, port, name
        try:
            opts, args = getopt.getopt(argv,"s:p:n:mhd",[])
        except getopt.GetoptError:
            print 'client.py -s <server address> -p <server port> -n <Name> -m [Toggles Manual Mode] -d <debug num>'
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print 'client.py -s <server address> -p <server port> -n <Name> -m [Toggles Manual Mode] -d <debug num>'
                sys.exit(1)
            elif opt == '-s':
                host = arg
                print "Server to connect to: " + host
            elif opt == '-p':
                port = int(arg)
                print "On port: " + str(port)
            elif opt == '-n':
                name = arg
                print "Player name set to: " + name
            elif opt == '-m':
                manual_mode = True
                print "Manual Mode Active"
            elif opt == '-d':
                debug_mode = True
                print "Debug Mode ON"

    arguments(sys.argv[1:])

################################################

    try:
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connections.append(c)
    except socket.error, msg:
        print "Failed to create socket. Error code: " + str(msg[0]) + ", Error message: " + msg[1]
        sys.text();

    try:
        c.connect((host, port))
        c.send("(cjoin({}))".format(name))
    except:
        print "Unable to Connect"
        sys.exit()

    print "Connected to {}{}.".format(host, port)
    c.setblocking(0)
    if manual_mode:
        connections.append(sys.stdin)

    while running:
        # try:
        read_sockets, write_sockets, error_sockets = select.select(connections, [], [])
        if not manual_mode:
            for sock in read_sockets:
                if sock == c:
                    data = sock.recv(4096)
                    if not data:
                        print "Disconnected from Server"
                        # sys.exit()
                        restart_program()
                    else:
                         process_input(c, data)
        elif manual_mode:
            print "<To send a message. Use: '@<username(s)*comma separated>: <message>'. For stat. Use: 'stat' "
            for sock in read_sockets:
                if sock == c:
                    data = sock.recv(4096)
                    if not data:
                        print "Disconnected from Server"
                        sys.exit()
                    else:
                        print(data)
                elif sock == sys.stdin:
                    line = sys.stdin.readline()
                    mahsa(c, line)


        # except:
        #     print "Error somewhere in Client"
        #     c.close()
        #     sys.exit()









    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
