import json
from pprint import pprint
from urllib.request import urlopen
from urllib.error import URLError

# Ignore for now: meet, end_meet, kill, left

# ToDo: anonymous_plaeyrs, anonymous_reveal

# ToDo: unarchived game url: https://s3.amazonaws.com/em-gamerecords/xxxx
# ToDo: archived game url: https://s3.amazonaws.com/em-gamerecords-forever/xxxx

# ToDo: filter which messages to view

# ToDo: print to file

# def get_data():


filename = input("Game number?: ")
print("Attempting to see if cached...")

gamedata = []

try:
    with open(filename) as data_file:
        gamedata = json.load(data_file)
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
            try:
                print("Attempting to save a copy...")
                file1 = open(filename, "w")
                file1.write(online_data)
                file1.close()
            except IOError:
                print("Failed. IOError")
                
        except URLError:
            print("Failed. URLError")
            exit()
        except ValueError:
            print("Failed. ValueError")
            exit()
    else:
        exit()

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
    print("Options: " + str(options))

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
        print("%s:%s \t (%s: %s)" % (minutes, seconds, speaker, msg))
    else:
        print("%s:%s \t %s: %s" % (minutes, seconds, speaker, msg))
    return

def parse_round(data):
    day = data['state']
    num = int(day/2) if (day % 2 == 0) else int((day + 1)/2)
    message = " DAY " if (day % 2 == 0) else " NIGHT "
    message = message + " " + str(num)
    if day < 0:
        print('-'*8 + " GAME OVER " + '-'*8)
    else:
        print('-'*8 + message + '-'*8)
    return

def parse_sysmsg(data):
    message = data['msg']
    has_action_type = 'type' in data
    if has_action_type:
        action_type = data['type']
    print(message)
    return

def parse_reveal(data):
    user = data['user']
    role = data['data']
    death = 'red' in data
    if death == True and data['red'] == False:
        print("DEATH: " + user + " as " + role)
    else:
        print("REVEAL: " + user + " as " + role)
    return

def parse_anon(data):
    user = data['user']
    mask = data['mask']
    print("MASK: " + mask + " is " + user)

def parse_vote(data):
    user = data['user']
    target = data['target']
    unvote = data['unpoint']
    meeting = data['meet']
    
    verb = "unvotes" if unvote else "votes"
    target = "no one" if (target == "*") else target
    if meeting == 'village':
        print(user + " " + verb + " " + target)
    else:
        print(user + " " + verb + " " + target + " (" + meeting + ")")

def parse_kick(data):
    user = data['user']
    print(user + " kicks")

def parse_disguise(data):
    exchange = data['exchange']
    for key in exchange.keys():
        disguiser = key
        disguisee = exchange[disguiser]
        print(disguiser + " was disguised as " + disguisee)


for line in gamedata:
    action_type = line[0]
    data = line[1]
    if action_type == 'auth':
        print('-'*8 + " GAME START "+'-'*8)
    elif action_type == 'users':
        print('-'*4 + " PLAYERS " + '-'*4)
        players = data['users']
        chatters = data["chatters"]
        for account in players:
            print(account)
        print('-'*4 + " CHATTERS " + '-'*4)
        for account in chatters:
            print(account)
        print('-'*4 + " PREGAME " + '-'*4)
    elif action_type == "anonymous_players":
        print('-'*4 + " ANONYMOUS MASKS " + '-'*4)
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
    elif (action_type == 'meet' or action_type == 'kill' or 
         action_type == 'left' or action_type == 'end_meet'):
        pass
    elif action_type == 'disguise':
        parse_disguise(data)
    else: 
       # Debug print
       print(action_type, end=" ")
       pprint(data)
    
else:
    print('-'*8 + " GAME END " + '-'*8)
       
