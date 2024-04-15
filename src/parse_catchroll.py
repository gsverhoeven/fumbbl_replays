def parse_catchroll(obj):

    successful = obj['successful']
    catch_roll = obj['roll']

    if successful:
        out_string = "Catch roll: " + str(catch_roll) + \
             " | " + str(obj['playerId']) + " succesfully catches the ball"
    else:
        out_string = "Catch roll: " + str(catch_roll) + \
             " | " + str(obj['playerId']) + " fails to catch the ball"

    return out_string