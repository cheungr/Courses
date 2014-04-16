#!/usr/bin/python           # This is the byzantium client application

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
    strikes_list = []
    troops_list = []
    connections = []
    round_num = 0
################################################                                 ARGUMENT HANDLING *TODO: ADD DATA TYPE CHECK

    def rand_name(darn):
        gen_name = choice(name_list)
        while gen_name == darn:
            gen_name = choice(name_list)
        
        print gen_name
        return gen_name


    def return_lowest_troop(dog):
        lowest = dog
        for i in troops_list:
            if int(i) < int(lowest):
                lowest = int(i)

        d = troops_list.index(str(lowest))
        namea = name_list[d]
        return namea


    def gen_message():
        return strip_non_ascii(choice(quote_list))


    def do_stuff(message):
        global round_num
        try:
            reg_test = re.search("(.+)\,(\d+)\,?([^,]+)?\,?([^,]+)?\,?([^,]+)?", message)
            print "This is what reg_test_group is returning: " + reg_test.group(1)
            if reg_test.group(1) == "PLAN":
                round_num = reg_test.group(2)
                c.send("(cchat(SERVER)(PLAN,{},PASS))".format(str(round_num)))
            elif reg_test.group(1) == "OFFER" or reg_test.group(1) == "OFFERL":
                round_num = reg_test.group(2)
                ALLY = reg_test.group(3)
                rand_num = randint(1,2)
                if ALLY != None and ALLY != "(sstat":
                    if rand_num == 1:
                        c.send("(cchat(SERVER)(DECLINE,{},{}))".format(str(round_num),ALLY))
                    else:
                        c.send("(cchat(SERVER)(ACCEPT,{},{}))".format(str(round_num),ALLY))
            elif reg_test.group(1) == "ACTION":
                if reg_test.group(2) != None:
                    round_num = reg_test.group(2)
                    rand_num = randint(1,2)
                    if rand_num == 1:
                    	c.send("(cchat(SERVER)(ACTION,{},PASS))".format(str(round_num)))
                    else:
                    	try:
                            d = return_lowest_troop(999999)
                            c.send("(cchat(SERVER)(ACTION,{},ATTACK,{}))".format(str(round_num),d))
                        except:
                            c.send("(cchat(SERVER)(ACTION,{},PASS))".format(str(round_num)))
                else:
                    c.send("(cchat(SERVER)(ACTION,{},PASS))".format(str(round_num)))
        except:
        	pass

    def process_input(c, input_i):
        global name_list
        global name
        print input_i
        global troops_list
        global name_list
        global strikes_list
        if input_i[0:6] == '(sstat':
            names = re.search("\(sstat\((.+)\)\)", input_i)
            string_thing = names.group(1)
            listing = string_thing.split(",")
            name_list =[]
            strikes_list = []
            troops_list = []
            i = 0
            while i < len(listing):
                name_list.append(listing[i])
                i += 3
            
            print name_list

            try:
                name_list.remove(name)
            except:
                pass

            y = 1
            while y < len(listing):
                strikes_list.append(listing[y])
                y += 3

            print strikes_list

            x = 2
            while x < len(listing):
                troops_list.append(listing[x])
                x += 3

            print troops_list
        elif input_i[0:6] == '(schat':
            taken = re.search("\(schat\((.+)\)\((.+)\)\)", input_i)
            in_name = taken.group(1)
            message = taken.group(2)
            if debug_mode:
                print "Message from: {} | {}".format(in_name, message)

            if in_name == "SERVER":
                do_stuff(message)
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
        rand = randint(1,10)
        if debug_mode:
            print "This is rand: " + str(rand)
        if rand == 1:
            if len(name_list) > 1:
                this_name = choice(name_list)
                if this_name != name and this_name != "SERVER":
                    c.send("(cchat({})({}))".format(this_name, gen_message()))
        elif rand == 2:
            print "Just sent a cchat"
            c.send("(cchat(ALL)({}))".format(gen_message()))
        elif rand == 3:
            print "just sent a cstat"
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
                        sys.exit()
                        #restart_program()
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









    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
