def parse_confusionroll(obj):

    successful = obj['successful']
    roll = obj['roll']

    if successful:
        out_string = "Confusion roll: " + str(roll) + \
             " | " + str(obj['playerId']) + " acts normally"
    else:
        out_string = "Confusion roll: " + str(roll) + \
             " | " + str(obj['playerId']) + " is confused"

    return out_string