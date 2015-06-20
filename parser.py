import json
from pprint import pprint

# Ignored: meet, end_meet, kill, left
# ToDo: anonymous_plaeyrs, anonymous_reveal

# ToDo: unarchived game url: https://s3.amazonaws.com/em-gamerecords/xxxx
# ToDo: archived game url: https://s3.amazonaws.com/em-gamerecords-forever/xxxx

# ToDo: filter which messages to view

# ToDo: print to file

filename = input('File name?: ')
#filename = '3314762'
#filename = '4111588'
#filename = '4156324'

with open(filename) as data_file:
    gamedata = json.load(data_file)

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
    message = "DAY" if (day % 2 == 0) else "NIGHT"
    message = message + " " + str(num)
    if day < 0:
        print('-'*4 + "GAME OVER" + '-'*4)
    else:
        print('-'*4 + message + '-'*4)
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
    print("REVEAL: " + user + " as " + role)
    return

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

    elif action_type == '<':
        parse_speech(data)
    elif action_type == 'round':
        parse_round(data)
    elif action_type == 'reveal':
        parse_reveal(data)
    elif action_type == 'msg':
        parse_sysmsg(data)
    elif action_type == 'point':
        parse_vote(data)
    elif action_type == 'kick':
        parse_kick(data)
    elif action_type == 'options':
        parse_options(data)
    else:
        # Debug print
        print(action_type, end=" ")
        pprint(data)
    
else:
    print('-'*4 + " GAME END " + '-'*4)
       
