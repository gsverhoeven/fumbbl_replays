def parse_catchroll(obj):

    successful = obj['successful']
    roll = obj['roll']

    if successful:
        out_string = "Catch roll: " + str(roll) + \
             " | " + str(obj['playerId']) + " succesfully catches the ball"
    else:
        out_string = "Catch roll: " + str(roll) + \
             " | " + str(obj['playerId']) + " fails to catch the ball"

    return out_string