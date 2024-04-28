def parse_injury(obj):

    if not obj['armorBroken']:
        out_string = "Armour roll: " + str(obj['armorRoll']) + \
             " | Armour of " + str(obj['defenderId']) + " is not broken"
    else: # armor broken
        out_string = "Armour roll: " + str(obj['armorRoll']) + \
             " | Armour of " + str(obj['defenderId']) + " broken"

        out_string = out_string + " | Injury roll: " + str(obj['injuryRoll']) +\
            " | new player State is " + str(obj['injury'])
        
        if obj['casualtyRoll'] is None:
            pass
        else:
            out_string = out_string + ' | Casualty Roll: ' + str(obj['casualtyRoll'])

    return out_string


#{'reportId': 'injury', 'defenderId': "['B2']", 'injuryType': 'block', 'armorBroken': True, 'armorRoll': [5, 4], 'injuryRoll': [5, 1], 'casualtyRoll': None, 'seriousInjury': None, 'casualtyRollDecay': None, 'seriousInjuryDecay': None, 'seriousInjuryOld': None, 'injury': 4, 'injuryDecay': None, 'attackerId': "['B4']", 'armorModifiers': ['Mighty Blow'], 'injuryModifiers': [], 'casualtyModifiers': [], 'skipInjuryParts': 'NONE'}

#{'reportId': 'injury', 'defenderId': "['L3']", 'injuryType': 'block', 'armorBroken': True, 'armorRoll': [4, 6], 'injuryRoll': [2, 5], 'casualtyRoll': None, 'seriousInjury': None, 'casualtyRollDecay': None, 'seriousInjuryDecay': None, 'seriousInjuryOld': None, 'injury': 5, 'injuryDecay': None, 'attackerId': "['B4']", 'armorModifiers': [], 'injuryModifiers': ['Mighty Blow'], 'casualtyModifiers': [], 'skipInjuryParts': 'NONE'}
