def parse_dodgeroll(obj):

    successful = obj['successful']
    roll = obj['roll']

    if successful:
        out_string = "Dodge roll: " + str(roll) + \
             " | " + str(obj['playerId']) + " succesfully dodges away"
    else:
        out_string = "Dodge roll: " + str(roll) + \
             " | " + str(obj['playerId']) + " fails to dodge"

    return out_string