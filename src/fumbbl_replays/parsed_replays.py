def determine_receiving_team_at_start(pd_replay):
    gameSetHomeFirstOffense = len(pd_replay.query('turnNr == 0 & turnMode == "startGame" & modelChangeId == "gameSetHomeFirstOffense"').index)

    if gameSetHomeFirstOffense == 1:
        receiving_team = 'teamHome'
    else: 
        receiving_team = 'teamAway'
    return receiving_team

def extract_coin_toss(pd_replay):
    for i in range(len(pd_replay)):
        if isinstance(pd_replay.iloc[i].modelChangeValue, dict):
            if 'choosingTeamId' in pd_replay.iloc[i].modelChangeValue:
                choosingTeamId = pd_replay.iloc[i].modelChangeValue['choosingTeamId']
                # PM compare this to receiving team: this is the choice
                return choosingTeamId
            else:
                pass
        else:
            pass
    return None