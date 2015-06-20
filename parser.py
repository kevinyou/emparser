import json
from pprint import pprint


with open('4111588') as data_file:
    data = json.load(data_file)

for line in data:
    type = line[0]
    data = line[1]
    if type == 'auth':
        print('-'*8 + " GAME START "+'-'*8)
    elif type == 'users':
        print('-'*4 + " PLAYERS " + '-'*4)
        players = data['users']
        chatters = data["chatters"]
        for account in players:
            print(account)
        print('-'*4 + " CHATTERS " + '-'*4)
        for account in chatters:
            print(account)
        print('-'*4 + " PREGAME " + '-'*4)
    elif type == '<':
        time = data['t']
        minutes = str(int(time/60))
        seconds = str(time%60)
        if len(seconds) < 2:
            seconds = '0' + seconds
        speaker = data['user']
        msg = data['msg']
        print("%s:%s \t %s: %s" % (minutes, seconds, speaker, msg))
    elif type == 'round':
        day = data['state']
        num = int(day/2) if (day % 2 == 0) else int((day + 1)/2)
        message = "DAY" if (day % 2 == 0) else "NIGHT"
        message = message + " " + str(num)
        if day < 0:
            print('-'*4 + "GAME OVER" + '-'*4)
        else:
            print('-'*4 + message + '-'*4)
