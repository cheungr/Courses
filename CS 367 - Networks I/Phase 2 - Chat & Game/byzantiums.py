#!/usr/bin/python           # This is the byzantium server application

#Roy Cheung
#CSCI 367
#W01024078

#Needs to accept multiple incoming connections from clients
#Parse incoming messages and broadcast to all other clients
from random import choice, randint
import socket, select, sys, Queue, getopt, re, time

############################################################### CONSTANTS/VARIABLES
connections = []

players = []
lobby = []
active_players = []

incoming_buffer = 4096
lobby_timeout = 10 #TODO: DEFAULT 10 SECONDS
min_players = 3 #TODO: DEFAULT IS 3
max_players = 30
play_timeout = 4 #TODO: DEFAULT 30 SECONDS
init_troops = 1000

phase = 0
round_num = 0
select_timeout = 1

lobby_timer = 0.0
phase_timer = 0.0
current_timer = 0.0

timer_set = False
lobby_timer_set = False
in_session = False
phase_timer_set = False
dispatch_offers = False

running = True
debug_flag = False

#TODO: Round incrementer. Makes sure the number does not go above 99999 and loops back to 1 instead.

class Player():
    def __init__(self, address, socket):
        self.name = ''
        self.strikes = 0
        self.socket = socket
        self.address = address
        self.buffer_string = ''
        self.in_lobby = False
        self.is_active = False
        self.current_troops = 0
        self.timeout = True
        self.ally_prop = []
        self.attackee_prop = []
        self.proposed = False
        self.attacking = []
        self.encounters = []
        self.divided_troops = []
        self.divided_index = 0
        self.battled_troops = 0
# class Battle_stats():
#     def __init__(self, player):
#         self.name = ''
#         self.socket = player
#         self.troops = 0


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
            broadstat("(sstat({}))".format(current_players_stats()))


def find_player_by_sock(sock):
    for person in players:
        if sock == person.socket:
            return person


def find_player_by_name(name):
    for person in players:
        if name == person.name:
            return person


def is_player_valid(name):
    try:
        if find_player_by_name(name):
            return True
        else:
            return False
    except:
        return False


def current_players(): #TODO: Change to return a string with name, strikes and number of troops.
    playernames = ''
    for person in players:
        if person.name != '':
            playernames = playernames + "," + person.name
    return playernames[1:len(playernames)]


def current_players_stats():
    playernames = ''
    for person in players:
        if person.name != '':
            playernames = playernames + "," + person.name + "," + str(person.strikes) + "," + str(person.current_troops)
    return playernames[1:len(playernames)]


def current_num_players(): #Used to check if total cjoined players exceed 30 or not.
    num = 0
    for person in players:
        if person.name != '':
            num += 1
    return num


def current_in_lobby():
    num = 0
    for person in players:
        if person.in_lobby:
            num += 1
    return num


def current_in_game():
    num = 0
    for person in players:
        if person.is_active:
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
        print message
#check someone disconnected, use some signal thing.

###############################################################

def cchat(names, message, fromc, sock):
    if find_player_by_sock(sock).name != '':
        names = names.replace(" ", "")
        namelist = re.split(',', names)
        if len(names) > 389:
            cstrike(sock, "toolong")
        else:
            if namelist[0] == "SERVER" and in_session:             #TODO:make sure namelist only has one item and not more than that.
                if len(namelist) == 1:
                    game_process(message, fromc, sock)
                else:
                    cstrike(sock, "malformed")
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
        if find_player_by_sock(sock).name == '':
            find_player_by_sock(sock).name = new_name
            find_player_by_sock(sock).in_lobby = True
            hell = current_players()
            send_this_stuff(sock, "(sjoin({})({})({},{},{}))".format(new_name, hell, min_players, lobby_timeout, play_timeout))
            for player in players:
                if player.socket != sock and player.name != '':
                    send_this_stuff(player.socket, "(sstat({}))".format(current_players_stats()))
        else:
            cstrike(sock, "malformed")


def cstat(dest):
    send_this_stuff(dest, "(sstat({}))".format(current_players_stats()))


def cstrike(sock, reason):
    find_player_by_sock(sock).strikes += 1
    strike_num = find_player_by_sock(sock).strikes
    if strike_num < 3:
        send_this_stuff(sock, "(strike({})({}))".format(strike_num, reason))
    else:
        send_this_stuff(sock, "(strike({})({}))".format(strike_num, reason))
        remove_player(sock)


def timestrike():
    for player in players:
        if player.timeout and player.is_active:
            cstrike(player.socket, "timeout")


def reset_timestrike():
    for player in players:
        if player.timeout == False and player.is_active:
            player.timeout = True


def next_round():
    print "in next_round"
    global round_num
    if round_num < 99999:
        round_num += 1
        new_round_join()
        broadstat("(sstat({}))".format(current_players_stats()))
    else:
        round_num = 1


def reset_active_players():
    print "In reset_active_players"
    for player in players:
        if player.is_active:
            player.ally_prop = []
            player.attackee_prop =[]
            player.proposed = False
            player.attacking = []
            player.encounters = []
            player.divided_troops = []
            player.divided_index = 0


def reset_master():
    print "in reset_master"
    for player in players:
        if player.is_active:
            player.is_active = False
            player.in_lobby = True


def reset_proposed():
    print "in reset_propsed"
    for player in players:
        if player.is_active:
            player.proposed = False


###############################################################             #Subtools used for stripping chars, and name verification

def strip_non_ascii(string):
    stripped = (c for c in string if 31 < ord(c) < 127)
    return ''.join(stripped)


def name_strip(string):
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
    if (name == "ALL" or name == "ANY" or name == '' or name == "SERVER"):
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

###############################################################

def remove_ally(fromc, ally):
    print "in remove_ally"
    try:
        find_player_by_name(fromc).attackee_prop.pop(find_player_by_name(fromc).ally_prop.index(ally))
        find_player_by_name(fromc).ally_prop.remove(ally)
    except Exception as E:
        print bcolors.FAIL + "ERROR IN REMOVE_ALLY " + str(E) + bcolors.ENDC


def ally_lack_strike():
    print "in ally_lack_strike"
    for person in players:
        if len(person.ally_prop) != 0 and person.is_active:
            cstrike(person.socket, "timeout")
            for i in person.ally_prop:
                try:
                    send_this_stuff(find_player_by_name(i).socket, "(schat(SERVER)(DECLINE,{},{}))".format(round_num, person.name))
                    remove_ally(person.name, i)
                except:
                    pass


def ally_check(fromc, ally):
    print "in Ally_check"
    for person in players:
        if person.name == fromc:
            for i in person.ally_prop:
                if i == ally:
                    return True
    return False


def phase_2_dispatcher():
    print "in phase_2_dispatch"
    global dispatch_offers
    if not dispatch_offers:
        for person in players:
            i = 0
            if person.name != '' and person.is_active:
                if len(person.ally_prop) == 0:
                    send_this_stuff(person.socket, "(schat(SERVER)(OFFERL,{}))".format(round_num))
                elif (len(person.ally_prop)) == 1:
                    send_this_stuff(person.socket, "(schat(SERVER)(OFFERL,{},{},{}))".format(round_num, person.ally_prop[i],person.attackee_prop[i]))
                else:
                    while i < len(person.ally_prop):
                        if i == len(person.ally_prop)-1:
                            send_this_stuff(person.socket, "(schat(SERVER)(OFFERL,{},{},{}))".format(round_num, person.ally_prop[i],person.attackee_prop[i]))
                            i += 1
                        else:
                            send_this_stuff(person.socket, "(schat(SERVER)(OFFER,{},{},{}))".format(round_num, person.ally_prop[i],person.attackee_prop[i]))
                            i += 1
        dispatch_offers = True
###############################################################


def troops_divide_init():
    print "in troops_divide_init"
    try:
        for player in players:
            player.divided_troops = []
            if player.is_active and player.current_troops != 0 and len(player.encounters) != 0:
                divided = player.current_troops / len(player.encounters)
                for i in range(0, len(player.encounters)):
                    player.divided_troops.append(divided)
                remaining_troops = player.current_troops - (divided * len(player.encounters))
                if remaining_troops > 0:
                    for i in range(0, remaining_troops):
                        player.divided_troops[i] = player.divided_troops[i] + 1
    except Exception as E:
        if debug_flag:
            print bcolors.FAIL + "Exception raised: at Divide {}".format(str(E)) + bcolors.ENDC
        pass


def roll_three_dice():
    rolls = []
    for i in range(0,3):
        rolls.append(randint(1,10))
    rolls.sort(reverse=True)
    return rolls


def roll_two_dice():
    rolls =[]
    for i in range(0,2):
        rolls.append(randint(1,10))
    rolls.sort(reverse=True)
    return rolls


def troop_aggregate():
    for player in players:
        if player.is_active and len(player.divided_troops) != 0:
            curr_troops = 0
            for i in player.divided_troops:
                if i >= 0:
                    curr_troops += i

            if curr_troops > 99999:
                curr_troops = 99999

            player.current_troops = curr_troops
            if curr_troops == 0:
                player.socket.close()
                connections.remove(player.socket)
                remove_player(player.socket)



def battle(attacker, defender, duel): #TODO: HANDLE WHEN A CLIENT DROPS.
    print "in battle"
    try:
        broadcast("SERVER", "NOTIFY,{},{},{}".format(round_num, attacker, defender))
        if find_player_by_name(defender).divided_index <= len(find_player_by_name(defender).divided_troops) and find_player_by_name(attacker).divided_index <= len(find_player_by_name(attacker).divided_troops):
            attacker_troops = find_player_by_name(attacker).divided_troops[find_player_by_name(attacker).divided_index]
            defender_troops = find_player_by_name(defender).divided_troops[find_player_by_name(defender).divided_index]
        else:
            raise "Index_ERROR in Battle"
       
        if attacker_troops <= 10:
            attacker_half = 0
        else:
            attacker_half = attacker_troops/2

        if defender_troops <= 10:
            defender_half = 0
        else:
            defender_half = defender_troops/2

        if debug_flag:
            print "THIS IS ATTACKER_HALF " + str(attacker_half)
            print "This is DEFENDER_HALF " + str(defender_half)

        while attacker_troops > attacker_half and defender_troops > defender_half:
            if debug_flag:
                print "attacker_troops = {}".format(attacker_troops)
                print "defender_troops = {}".format(defender_troops)
            attacker_dices = roll_three_dice()
            if duel:
                defender_dices = roll_three_dice()
                for i in range(0,3):
                    if attacker_dices[i] > defender_dices[i]:
                        defender_troops -= 1
                    else:
                        attacker_troops -= 1
            else:
                defender_dices = roll_two_dice()
                for i in range(0,2):
                    if attacker_dices[i] > defender_dices[i]:
                        defender_troops -= 1
                    else:
                        attacker_troops -= 1

        if attacker_troops > 99999:
            attacker_troops = 99999
        if defender_troops > 99999:
            defender_troops = 99999

        if attacker_troops <= 0:
            defender_troops += init_troops
        if defender_troops <= 0:
            attacker_troops += init_troops

        if attacker_troops < 0:
            attacker_troops = 0
        if defender_troops < 0:
            defender_troops = 0

        find_player_by_name(attacker).divided_troops[find_player_by_name(attacker).divided_index] = attacker_troops
        find_player_by_name(defender).divided_troops[find_player_by_name(defender).divided_index] = defender_troops

        find_player_by_name(attacker).divided_index += 1
        find_player_by_name(defender).divided_index += 1

    except Exception as E:
        if debug_flag:
            print bcolors.FAIL + "Exception raised: at Battle {}".format(str(E)) + bcolors.ENDC
        pass


def new_round_join():
    print "in new_round_join"
    for player in players:
        if player.name != "" and player.in_lobby:
            player.is_active = True
            player.in_lobby = False
            player.current_troops = init_troops


def commence_battles():
    print "In commence_battles"
    troops_divide_init()
    for player in players:
        if player.is_active and len(player.attacking) != 0:
            try:
                if find_player_by_name(player.attacking[0]).attacking == player.name:
                    find_player_by_name(player.attacking[0]).attacking = []
                    battle(player.name, player.attacking[0], True)
                else:
                    battle(player.name, player.attacking[0], False)
            except Exception as E:
                if debug_flag:
                  print bcolors.FAIL + "Exception raised: at commence battle {}".format(str(E)) + bcolors.ENDC
                pass


###############################################################

def game_process(message, fromc, sock):
    print "in game_process"
    global round_num
    find_player_by_sock(sock).timeout = False
    #TODO: REMOVE SPACES FROM THE STRING, CHECK NAMES ONCE GOTTEN FROM STRING.
    #TODO: CHECK TO MAKE SURE PLAYER IS ACTUALLY IN GAME. ELSE STRIKE THEM!                                     #TODO: MAKE SURE PLAYER IS ONLY MAKING ONE OFFER!
    if phase == 1:
        try:
            reg_test = re.search("PLAN\,(\d+)\,(.+)", message)
            if int(reg_test.group(1)) == round_num:
                play_list = reg_test.group(2).split(",")
                if play_list[0] != "PASS":
                    if play_list[0] == "APPROACH":
                        play_list.remove(play_list[0])
                        if len(play_list) > 2:
                            cstrike(sock, "malformed")
                        else:
                            ally = play_list[0]
                            attackee = play_list[1]
                            if debug_flag:
                                print bcolors.OKGREEN + "APPROACH ALLIANCE - ALLY:({}) ATTACKEE:({})".format(ally, attackee) + bcolors.ENDC
                            if find_player_by_name(fromc).proposed:
                                cstrike(find_player_by_name(fromc).socket, "malformed")
                            else:
                                find_player_by_name(fromc).proposed = True
                                find_player_by_name(ally).ally_prop.append(fromc)
                                find_player_by_name(ally).attackee_prop.append(attackee)
                    else:
                        cstrike(sock, "malformed")
                elif play_list[0] == "PASS":
                    find_player_by_name(fromc).proposed = True
                    if debug_flag:
                        print "PLAYER ({}) PASSED".format(fromc)
                else:
                    cstrike(sock, "malformed")
            else:
                if int(reg_test.group(1)) >= 99999:
                    cstrike(sock, "badint")
                else:
                    cstrike(sock, "malformed")
        except:
            cstrike(sock, "malformed")
    elif phase == 2:
        try:
            reg_test = re.search("(.+)\,(\d+)\,(.+)", message)
            if int(reg_test.group(2)) == round_num:
                if reg_test.group(1) == "ACCEPT":
                    # print "ACCEPTED"
                    # print reg_test.group(3)
                    # print fromc
                    # print"END ACCEPTED"
                    # # if find_player_by_name(reg_test.group(3)):
                    if ally_check(fromc, reg_test.group(3)):
                        send_this_stuff(find_player_by_name(reg_test.group(3)).socket, "(schat(SERVER)(ACCEPT,{},{}))".format(round_num, fromc))
                        remove_ally(fromc, reg_test.group(3))
                    else:
                        cstrike(sock, "malformed")
                elif reg_test.group(1) == "DECLINE":
                    if ally_check(fromc, reg_test.group(3)):
                        send_this_stuff(find_player_by_name(reg_test.group(3)).socket, "(schat(SERVER)(DECLINE,{},{}))".format(round_num, fromc))
                        remove_ally(fromc, reg_test.group(3))
                    else:
                        cstrike(sock, "malformed")
                else:
                    cstrike(sock, "malformed")
            else:
                cstrike(sock, "malformed")
        except:
            cstrike(sock, "malformed")
    elif phase == 3:
        try:
            reg_test = re.search("ACTION,(\d+),?([^,]+),?(.+)?", message)
            print "PASSED REGEX"
            if int(reg_test.group(1)) == round_num:
                if reg_test.group(2) == "PASS" and reg_test.group(3) == None:
                    find_player_by_sock(sock).proposed = True
                    if debug_flag:
                        print "PLAYER ({}) PASSED".format(fromc)
                elif reg_test.group(2) == "ATTACK":
                    attackee = reg_test.group(3)
                    if debug_flag:
                        print "PLAYER ({}) IS ATTACKING".format(fromc)
                    #TODO: add the thing to attack table thing.
                    if find_player_by_sock(sock).proposed:
                        cstrike(sock, "malformed")
                    else:
                        if find_player_by_name(attackee) and not find_player_by_name(fromc).proposed:
                            find_player_by_name(fromc).attacking.append(attackee)
                            find_player_by_name(fromc).proposed = True
                            if attackee not in find_player_by_name(fromc).encounters:
                                find_player_by_name(fromc).encounters.append(attackee)
                            if fromc not in find_player_by_name(attackee).encounters:
                                find_player_by_name(attackee).encounters.append(fromc)
                        else:
                            find_player_by_name(fromc).proposed = False
                            cstrike(sock, "malformed")
                else:
                    cstrike(sock, "malformed")
            else:
                cstrike(sock, "malformed")
        except Exception as dog:
            cstrike(sock, "malformed")
            print str(dog)


def time_phase_diff():      #TODO: DO CHECK TO SEE IF EVERYONE RESPONDED, IF THEY HAVE, SKIP REST OF TIMER. (simple check for timeout flag)
    global phase_timer, phase, phase_timer_set

    all_done = True
    for player in players:
        if player.is_active and not player.proposed:
            all_done = False
    if all_done:
        phase += 1
        if debug_flag:
            print "PHASE CHANGED. Phase is current at {}.".format(phase)
        phase_timer_set = False
    elif ((time.time() - phase_timer) >= play_timeout) and phase_timer_set:
        phase += 1
        if debug_flag:
            print "PHASE CHANGED. Phase is current at {}.".format(phase)
        phase_timer_set = False


def game_init():
    global round_num, in_session, phase, lobby_timer, lobby_timer_set, phase_timer, phase_timer_set, dispatch_offers
    if not in_session:
        if current_in_lobby() >= min_players and not lobby_timer_set:
            lobby_timer_set = True
            lobby_timer = time.time()
        if current_in_lobby() >= min_players and ((time.time() - lobby_timer) > lobby_timeout):
            i = 0
            for person in players:
                i += 1
                if person.name != '':
                    person.current_troops = init_troops
                    person.in_lobby = False
                    person.is_active = True
            round_num = 1
            phase = 1
            broadstat("(sstat({}))".format(current_players_stats()))
            in_session = True
    else:
        lobby_timer_set = False

        if phase_timer_set:
            time_phase_diff()
        if phase == 1 and not phase_timer_set:
            broadcast("SERVER", "PLAN,{}".format(str(round_num)))
            phase_timer_set = True
            phase_timer = time.time()
            dispatch_offers = False
            print "IS PHASE 1 ###################################"
        elif phase == 2 and not phase_timer_set:
            timestrike()
            reset_proposed()
            phase_2_dispatcher()
            phase_timer_set = True
            phase_timer = time.time()
            print "IS PHASE 2 ###################################"
        elif phase == 3 and not phase_timer_set:
            ally_lack_strike()
            reset_proposed()
            broadcast("SERVER", "ACTION,{}".format(str(round_num)))
            phase_timer_set = True
            phase_timer = time.time()
            print "IS PHASE 3 ###################################"
        elif phase == 4 and not phase_timer_set:
            timestrike()
            if current_in_game() <= 1:
                in_session = False
                reset_master()
                phase = 0
            else:
                commence_battles()
                next_round()
                troop_aggregate()
                reset_proposed()
                phase = 1
                reset_active_players()


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
    # if debug_flag:
    #     print bcolors.WARNING + buffers + bcolors.ENDC
    # if len(buffers) > msglength:
    #     cstrike(sock, "toolong")
    #     buffers = ""
    #     find_player_by_sock(sock).buffer_string = buffers
    while i < msglength and i < len(buffers):
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
                    # if debug_flag:
                    #     print name
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
                # if debug_flag:
                #     print "Current Buffer: " + buffers
                i = 0
            else:
                reSync = True
                # if debug_flag:
                #     print "RESYNC AND STRIKE 3"
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
        global play_timeout, min_players, lobby_timeout, debug_flag, init_troops
        try:
            opts, args = getopt.getopt(argv, "t:l:m:f:hd", [])
        except getopt.GetoptError:
            print 'server.py -t <timeout> -l <lobby wait time> -m <min players>'
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print 'server.py -t <timeout> -l <lobby wait time> -m <min players>'
                sys.exit(1)
            elif opt == "-t":
                play_timeout = int(arg)
                print "Move timeout is set to: " + str(play_timeout)
            elif opt == "-m":
                min_players = int(arg)
                print "Min players is set to: " + str(min_players)
            elif opt == "-l":
                lobby_timeout = int(arg)
                print "Lobby timeout is set to: " + str(lobby_timeout)
            elif opt == "-d":
                debug_flag = True
                print "Debug Flag ON"
            elif opt == "-f":
                init_troops = int(arg)
                print "Troops per player set to: " + str(init_troops)
    arguments(sys.argv[1:])

    ################################################ 								BINDS AND SETS SOCKETS

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
        print bcolors.WARNING + "Failed to create socket. Error code: (), Error message: ({})".format(str(msg[0]), + msg[1]) + bcolors.ENDC
        sys.exit()

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
        game_init()
        #Select, yo.
        read_sockets, write_sockets, error_sockets = select.select(connections, [], [], 0)
        for sock in read_sockets:
            #incoming connection
            if sock == s:
                try:
                    csock, address = s.accept() #TODO: FIX THE PART WHERE THE CLINET JOINS BUT DOESN'T SEND A CJOIN. AND DISCONNECTS, STILL MAINTAINS IN PLAYERS. CAUSE NOTHING EVER GETS SENT TO THEM.
                    if current_num_players() == max_players:
                        send_this_stuff(csock, "(snovac)")
                        print bcolors.WARNING + "NO VACANCY. Client Rejected" + bcolors.ENDC
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
                    print bcolors.OKBLUE + "Client (%s, %s) disconnected" % address + bcolors.ENDC
                    sock.close()
                    connections.remove(sock)
                    remove_player(sock)
                    continue
    s.close()
