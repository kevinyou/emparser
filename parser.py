#!/usr/bin/env python3
"""Self-contained python script that retrieves games, parses them, and then prints the output as text.  """
import json
import re
import sys
import argparse
from pprint import pprint
from urllib.request import urlopen
from urllib.error import URLError

def run_arg(settings):
    """Runs with command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?')
    parser.add_argument('--online', '-o', 
        action='store_true', help='get game online' )
    parser.add_argument('--archived', '-a', 
        action='store_true', help='archived game flag' )
    parser.add_argument('--write', '-w', 
        action='store_true', dest='write',
        help='write output to file flag (default)' )
    parser.add_argument('--no-write', '-no-w', 
        action='store_false', dest='write',
        help='don\'t write output to file flag' )
    parser.set_defaults(write=True)
    parser.add_argument('--mute', '-m', 
        action='store_false', help='mute output in system flag' )
    parser.add_argument('--graveyard', '-gy',
        action='store_true', dest='graveyard',
        help='print graveyard messages (default)')
    parser.add_argument('--no-graveyard', '-no-gy',
        action='store_false', dest='graveyard',
        help='don\'t print graveyard messages')
    parser.set_defaults(graveyard=True)
    parser.add_argument('--system', '-sys',
        action='store_true', dest='sys',
        help='print system messages (default)')
    parser.add_argument('--no-system', '-no-sys',
        action='store_false', dest='sys',
        help='don\'t print system messages')
    parser.set_defaults(sys=True)

    args = parser.parse_args()
    
    settings['filename'] = args.file
    settings['print_to_sys'] = args.mute
    settings['print_to_file'] = args.write
    settings['print_graveyard'] = args.graveyard
    settings['print_game_msg'] = args.sys
    
    if args.online:
        try:
            if args.archived:
                url = "https://s3.amazonaws.com/em-gamerecords-forever/" + settings['filename']
            else:
                url = "https://s3.amazonaws.com/em-gamerecords/" + settings['filename']
            request = urlopen(url)
            online_data = request.read().decode("utf-8")
            gamedata = json.loads(online_data)
        
            try:
                print("Attempting to save a copy...")
                file1 = open(settings['filename'], "wb")
                file1.write(online_data.encode("utf8"))
                file1.close()
                print("Success.")
            except IOError:
                print("Failed. IOError")
        
        except URLError:
            print("Failed. URLError")
            print("Exiting")
            sys.exit()
    
    else:
        try:
            with open(settings['filename']) as data_file:
                gamedata = json.load(data_file)
                print("Success.")
        except IOError:
            print("Failed to load file.")
            sys.exit()
    
    return gamedata

def yninput(string):
    """Converts yes or no into true or false"""
    yn = input(string)
    if len(yn) > 0 and (yn[0] == 'y' or yn[0] == 'Y'):
        return True
    return False

def run_cli(settings):
    """Runs in command line interface, prompting the user"""
    settings['filename'] = input("Game number?: ")
    print("Attempting to see if cached on disk...")
    
    try:
        with open(settings['filename']) as data_file:
            gamedata = json.load(data_file)
            print("Success.")
    except IOError:
        yn = yninput("Failed. Attempt to view game online? [Y/N]: ")
        if yn:
            try:
                archived = yninput("Is the game archived? [Y/N]: ")
                if archived:
                    url = "https://s3.amazonaws.com/em-gamerecords-forever/" + settings['filename']
                else:
                    url = "https://s3.amazonaws.com/em-gamerecords/" + settings['filename']
                request = urlopen(url)
                online_data = request.read().decode("utf-8")
                gamedata = json.loads(online_data)
                print("Success.")
                try:
                    print("Attempting to save a copy...")
                    file1 = open(settings['filename'], "w")
                    file1.write(online_data)
                    file1.close()
                    print("Success.")
                except IOError:
                    print("Failed. IOError")
                    
            except URLError:
                print("Failed. URLError")
                print("Exiting")
                sys.exit()
            except ValueError:
                print("Failed. ValueError")
                print("Exiting")
                sys.exit()
        else:
            print("Exiting")
            sys.exit()

    settings['print_to_sys'] = yninput("Write output to console? [Y/N]: ")
    settings['print_to_file'] = yninput("Write output to file? [Y/N]: ")
    return gamedata

def game_print(settings, string):
    if settings['print_to_sys']:
        print(string)
    if settings['print_to_file']:
        settings['output_file'].write(string + "\n")

def parse_options(settings, data):
    options_data = data['data']
    options = []
    for option in options_data.keys():
        if option == 'custom_meets' or option == 'custom_roles':
            pass
        elif option == 'time':
            time_day = options_data[option]['time_day']
            time_night = options_data[option]['time_night']
            if time_day != 600 or time_night != 120:
                options.append("faster_game")
        elif options_data[option] == 1:
            options.append(option)
    game_print(settings, "Options: " + str(options))

def parse_speech(settings, data):
    time = data['t']
    minutes = str(int(time/60))
    seconds = str(time%60)
    if len(seconds) < 2:
        seconds = '0' + seconds
    if len(minutes) < 2:
        minutes = '0' + minutes
    msg = data['msg']
    is_quote = 'quote' in data
    is_dead = 'dead' in data
    is_whisper = 'whisper' in data
    is_contact = 'contact' in data
    if is_quote and data['quote'] == True:
        speaker = data['user']
        msg = "\"" + data['target'] + " said | " + msg
    if is_dead and data['dead'] and settings['print_graveyard']:
        speaker = data['user']
        game_print(settings, "{0:s}:{1:s} \t ({2:s}: {3:s})".format(minutes, seconds, speaker, msg))
    elif is_whisper:
        speaker = data['user']
        target = data['whisper']
        printing = "{0:s}:{1:s} \t {2:s} whispers to {3:s}: {4:s}"
        game_print(settings, printing.format(minutes, seconds, speaker, target, msg))
    elif is_contact:
        role = data['role']
        printing = "{0:s}:{1:s} \t ({2:s}) You recieves a message: {3:s}"
        game_print(settings, printing.format(minutes, seconds, role.capitalize(), msg))

    else:
        speaker = data['user']
        game_print(settings, "{0:s}:{1:s} \t {2:s}: {3:s}".format(minutes, seconds, speaker, msg))
    return

def parse_round(settings, data):
    day = data['state']
    num = int(day/2) if (day % 2 == 0) else int((day + 1)/2)
    message = " DAY " if (day % 2 == 0) else " NIGHT "
    message = message + " " + str(num) + " "
    if day < 0:
        game_print(settings, '-'*8 + " GAME OVER " + '-'*8)
    else:
        game_print(settings, '-'*8 + message + '-'*8)
    return

def parse_sysmsg(settings, data):
    message = data['msg']
    has_action_type = 'type' in data
    if has_action_type:
        action_type = data['type']
    if settings['print_game_msg']:
        game_print(settings, message)
    return

def parse_reveal(roles, settings, data):
    user = data['user']
    role = data['data']
#    death = 'red' in data
#    if death == True and data['red'] == False:
#        game_print(settings, "DEATH: " + user + " as " + role)
#        pass
    if roles[user] != role:
        roles[user] = role
        game_print(settings, "ROLE CHANGE: " + user + " is now a " + role)
    return

#def parse_anon(data):
#    user = data['user']
#    mask = data['mask']
#    game_print(settings, "MASK: " + mask + " is " + user)

def parse_vote(settings, data):
    user = data['user']
    target = data['target']
    unvote = data['unpoint']
    meeting = data['meet']
    
    verb = "unvotes" if unvote else "votes"
    target = "no one" if (target == "*") else target
    if meeting == 'village':
        game_print(settings, user + " " + verb + " " + target)
    else:
        game_print(settings, user + " " + verb + " " + target + " (" + meeting + ")")

#def parse_kick(data):
#    user = data['user']
#    game_print(settings, user + " kicks")

def parse_disguise(settings, data):
    exchange = data['exchange']
    for key in exchange.keys():
        disguiser = key
        disguisee = exchange[disguiser]
        game_print(settings, disguiser + " was disguised as " + disguisee)

def parse_input(settings, data):
    player = data['user']
    meeting = data['meet']
    inputname = data['inputname']
    # yex/no
    if inputname == 'boolean':
        inputname = 'bool'
    # santa
    if inputname == 'setitem':
        inputname = 'item'
    # driver
    if inputname == 'pick':
        inputname = 'player'
    data_dict = data['data']
    try:
        input_data = data_dict[inputname]
    
        printing = "{0:s} chooses {1:s} ({2:s})"
        game_print(settings, printing.format(player, input_data, meeting))
    except:
        pprint(data)
    

def main():
    
    # Default settings
    settings = {'filename':"", 'print_to_sys':True, 
        'print_to_file':False, 'print_graveyard':True,
        'print_game_msg':True, 'output_file':None}
    gamedata = []

    if (len(sys.argv) > 1):
        gamedata = run_arg(settings)
    else:
        gamedata = run_cli(settings)

    if settings['print_to_file']:
        try:
            settings['output_file'] = open(settings['filename'] + ".txt", "w")
        except IOError:
            print("Failed. IOError")
            print("Exiting")
            sys.exit()




     # Default settings
    ignore_actions = ['meet', 'kill', 'left', 'end_meet', 'unmeet', 'event', 
    'anonymous_players', 'anonymous_reveal', 'kick']

    players = []
    roles = {}
    ids = {}
    masks = {}
    for line in gamedata:
        action_type = line[0]
        data = line[1]
        if action_type == 'auth':
            game_print(settings, '-'*8 + " GAME START "+'-'*8)
        elif action_type == 'users':
            game_print(settings, '-'*4 + " PLAYERS " + '-'*4)
            players = data['users']
            chatters = data["chatters"]
            for player in players:
                try:
                    ids[player] = str(players[player]['id'])
                except KeyError:
                    ids[player] = "N/A"
            for chatter in chatters:
                if not(chatter in ids):
                    avatar_url = chatters[chatter]['imgteeny']
                    if (avatar_url == '/images/avatar_teeny.jpg'):
                        ids[chatter] = "N/A"
                    else:
                        p = re.compile(".*?(\d+)_teeny.jpg")
                        m = p.match(avatar_url)
                        if m:
                            ids[chatter] = m.group(1)
                        else:
                            ids[chatter] = "N/A"
                for line1 in gamedata:
                    if line1[0] == 'options':
                        break
                    if line1[0] != 'reveal' and line1[0] != 'anonymous_reveal':
                        continue
                    if line1[0] == 'reveal':
                        user = line1[1]['user']
                        role = line1[1]['data']
                        roles[user] = role
                    if line1[0] == 'anonymous_reveal':
                        user = line1[1]['user']
                        mask = line1[1]['mask']
                        masks[user] = mask
            
            if len(masks) == 0:
                game_print(settings, "{0:20s} {1:10s} {2:20s}".format(
                    "PLAYERS", "IDS", "ROLES"))
            else:
                game_print(settings, "{0:20s} {1:10s} {2:20s} {3:s} ".format(
                    "PLAYERS", "IDS", "ROLES", "MASKS"))

            for account in players:
                if len(masks) == 0:
                    printing = "{0:20s} {1:10s} {2:s}"
                    game_print(settings, printing.format(account, "(" + ids[account] + ")", roles[account].capitalize()))
                else:
                    printing = "{0:20s} {1:10s} {2:20s} {3:s} "
                    game_print(settings, printing.format(account, "(" + ids[account] + ")", 
                        roles[masks[account]].capitalize(), masks[account]))
            if len(list(set(list(chatters)) - set(list(players)))) != 0:
                game_print(settings, '-'*4 + " OTHER CHATTERS " + '-'*4)
            for account in chatters:
                if not(account in players):
                    printing = "{0:20s} {1:10s}"
                    game_print(settings, printing.format(account, "(" + ids[account] + ")"))
            game_print(settings, '-'*4 + " PREGAME " + '-'*4)
    #    elif action_type == "anonymous_players":
    #        game_print(settings, '-'*4 + " ANONYMOUS MASKS " + '-'*4)
        elif action_type == '<':
            parse_speech(settings, data)
        elif action_type == 'round':
            parse_round(settings, data)
        elif action_type == 'reveal':
            parse_reveal(roles, settings, data)
    #    elif action_type == 'anonymous_reveal':
    #        parse_anon(data)
        elif action_type == 'msg':
            parse_sysmsg(settings, data)
        elif action_type == 'point':
            parse_vote(settings, data)
    #    elif action_type == 'kick':
    #        parse_kick(data)
        elif action_type == 'options':
            parse_options(settings, data)
        elif action_type in ignore_actions:
            pass
        elif action_type == 'disguise':
            parse_disguise(settings, data)
        elif action_type == 'inputed':
            parse_input(settings, data)
        else: 
           # Debug game_print
           print(action_type, end=" ")
           pprint(data)
        
    else:
        game_print(settings, '-'*8 + " GAME END " + '-'*8)

    if settings['print_to_file']:
        settings['output_file'].close()

    print("Success. Exiting")
    sys.exit()

if __name__ == "__main__":
        main()
