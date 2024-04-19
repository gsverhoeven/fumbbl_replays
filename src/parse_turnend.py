def parse_turnend(obj):

    out_string = "End of Turn"
    if (obj['playerIdTouchdown'] is None) & (len(obj['knockoutRecoveryArray']) == 0):
        pass
    else:
        if obj['playerIdTouchdown'] is not None:
            out_string = " | Touchdown scored"
        if len(obj['knockoutRecoveryArray']) > 0:
            # print KO recovery
            out_string = out_string + " | " + \
                str(len(obj['knockoutRecoveryArray'])) + " players recovering"

    return out_string

#{'reportId': 'turnEnd', 'playerIdTouchdown': '16074189', 'knockoutRecoveryArray': [{'playerId': '16074191', 'recovering': True, 'roll': 6, 'bloodweiserBabes': 0, 'reason': None}, {'playerId': '16074192', 'recovering': True, 'roll': 5, 'bloodweiserBabes': 0, 'reason': None}], 'heatExhaustionArray': [], 'unzapArray': [], 'heatRoll': 0}
#{'reportId': 'turnEnd', 'playerIdTouchdown': '16106247', 'knockoutRecoveryArray': [{'playerId': '16074194', 'recovering': True, 'roll': 5, 'bloodweiserBabes': 0, 'reason': None}], 'heatExhaustionArray': [], 'unzapArray': [], 'heatRoll': 0}
#{'reportId': 'turnEnd', 'playerIdTouchdown': None, 'knockoutRecoveryArray': [], 'heatExhaustionArray': [], 'unzapArray': [], 'heatRoll': 0}
