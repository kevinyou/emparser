import json
import sys
from pprint import pprint
from urllib.request import urlopen
from urllib.error import URLError

# Ignore for now: meet, end_meet, kill, left

# ToDo: filter which messages to view
# ToDo: allow command line arguments
# ToDo: change "votes" to "chooses" for individual meetings (minor)
# ToDo: write userID next to players
# ToDo: reorganize code layout


filename = input("Game number?: ")
print("Attempting to see if cached...")

gamedata = []

try:
    with open(filename) as data_file:
        gamedata = json.load(data_file)
        print("Success.")
except IOError:
    yn = input("Failed. Attempt to view game online? [Y/N]: ")
    if yn[0] == 'y' or yn[0] == 'Y':
        try:
            archived = input("Is the game archived? [Y/N]: ")
            if archived[0] == 'y' or yn[0] == 'Y':
                url = "https://s3.amazonaws.com/em-gamerecords-forever/" + filename
            else:
                url = "https://s3.amazonaws.com/em-gamerecords/" + filename
            request = urlopen(url)
            online_data = request.read().decode("utf-8")
            gamedata = json.loads(online_data)
            print("Success.")
            try:
                print("Attempting to save a copy...")
                file1 = open(filename, "w")
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

query = input("Write output to console? [Y/N]: ")
print_to_sys = True if (query[0] == 'y' or query[0] == 'Y') else False
query = input("Write output to file (" + filename + ".txt)? [Y/N]: ")
print_to_file = True if (query[0] == 'y' or query[0] == 'Y') else False

if print_to_file:
    try:
        file2 = open(filename + ".txt", "w")
    except IOError:
        print("Failed. IOError")
        print("Exiting")
        sys.exit()



def game_print(string):
    if print_to_sys:
        print(string)
    if print_to_file:
        file2.write(string + "\n")
    
    


def parse_options(data):
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
    game_print("Options: " + str(options))

def parse_speech(data):
    time = data['t']
    minutes = str(int(time/60))
    seconds = str(time%60)
    if len(seconds) < 2:
        seconds = '0' + seconds
    speaker = data['user']
    msg = data['msg']
    is_quote = 'quote' in data
    is_dead = 'dead' in data
    if is_quote and data['quote'] == True:
        msg = "\"" + data['target'] + " said | " + msg
    if is_dead and data['dead'] == True:
        game_print("{0:s}:{1:s} \t ({2:s}: {3:s})".format(minutes, seconds, speaker, msg))
    else:
        game_print("{0:s}:{1:s} \t {2:s}: {3:s}".format(minutes, seconds, speaker, msg))
    return

def parse_round(data):
    day = data['state']
    num = int(day/2) if (day % 2 == 0) else int((day + 1)/2)
    message = " DAY " if (day % 2 == 0) else " NIGHT "
    message = message + " " + str(num)
    if day < 0:
        game_print('-'*8 + " GAME OVER " + '-'*8)
    else:
        game_print('-'*8 + message + '-'*8)
    return

def parse_sysmsg(data):
    message = data['msg']
    has_action_type = 'type' in data
    if has_action_type:
        action_type = data['type']
    game_print(message)
    return

def parse_reveal(data):
    user = data['user']
    role = data['data']
    death = 'red' in data
    if death == True and data['red'] == False:
        game_print("DEATH: " + user + " as " + role)
    else:
        game_print("REVEAL: " + user + " as " + role)
    return

def parse_anon(data):
    user = data['user']
    mask = data['mask']
    game_print("MASK: " + mask + " is " + user)

def parse_vote(data):
    user = data['user']
    target = data['target']
    unvote = data['unpoint']
    meeting = data['meet']
    
    verb = "unvotes" if unvote else "votes"
    target = "no one" if (target == "*") else target
    if meeting == 'village':
        game_print(user + " " + verb + " " + target)
    else:
        game_print(user + " " + verb + " " + target + " (" + meeting + ")")

def parse_kick(data):
    user = data['user']
    game_print(user + " kicks")

def parse_disguise(data):
    exchange = data['exchange']
    for key in exchange.keys():
        disguiser = key
        disguisee = exchange[disguiser]
        game_print(disguiser + " was disguised as " + disguisee)

ignore_actions = ['meet', 'kill', 'left', 'end_meet', 'unmeet']

for line in gamedata:
    action_type = line[0]
    data = line[1]
    if action_type == 'auth':
        game_print('-'*8 + " GAME START "+'-'*8)
    elif action_type == 'users':
        game_print('-'*4 + " PLAYERS " + '-'*4)
        players = data['users']
        chatters = data["chatters"]
        for account in players:
            game_print(account)
        game_print('-'*4 + " CHATTERS " + '-'*4)
        for account in chatters:
            game_print(account)
        game_print('-'*4 + " PREGAME " + '-'*4)
    elif action_type == "anonymous_players":
        game_print('-'*4 + " ANONYMOUS MASKS " + '-'*4)
    elif action_type == '<':
        parse_speech(data)
    elif action_type == 'round':
        parse_round(data)
    elif action_type == 'reveal':
        parse_reveal(data)
    elif action_type == 'anonymous_reveal':
        parse_anon(data)
    elif action_type == 'msg':
        parse_sysmsg(data)
    elif action_type == 'point':
        parse_vote(data)
    elif action_type == 'kick':
        parse_kick(data)
    elif action_type == 'options':
        parse_options(data)
    elif action_type in ignore_actions:
        pass
    elif action_type == 'disguise':
        parse_disguise(data)
    else: 
       # Debug game_print
       print(action_type, end=" ")
       pprint(data)
    
else:
    game_print('-'*8 + " GAME END " + '-'*8)

if print_to_file:
    file2.close()

print("Success. Exiting")
sys.exit()
