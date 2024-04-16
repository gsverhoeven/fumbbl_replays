def parse_GFIroll(obj):

    successful = obj['successful']
    roll = obj['roll']

    if successful:
        out_string = "GFI roll: " + str(roll) + \
             " | " + str(obj['playerId']) + " succesfully goes for it"
    else:
        out_string = "GFI roll: " + str(roll) + \
             " | " + str(obj['playerId']) + " fails to go for it"

    return out_string