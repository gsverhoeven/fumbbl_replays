def extract_players_from_replay(my_replay):
    playerId = []
    playerNr = []
    positionId = []
    playerName = []
    playerType = []
    skillArray = []
    home_away = []
    teamId = []
    race = []

    tmpPlayers = my_replay['game']['teamAway']['playerArray']
    tmp_team_id = my_replay['game']['teamAway']['teamId']
    tmp_race = my_replay['game']['teamAway']['race']

    for playerIndex in range(len(tmpPlayers)):
        playerId.append(tmpPlayers[playerIndex]['playerId'])
        playerNr.append(tmpPlayers[playerIndex]['playerNr'])
        positionId.append(tmpPlayers[playerIndex]['positionId'])
        playerName.append(tmpPlayers[playerIndex]['playerName'])
        playerType.append(tmpPlayers[playerIndex]['playerType'])
        skillArray.append(tmpPlayers[playerIndex]['skillArray'])
        home_away.append('teamAway')
        teamId.append(tmp_team_id)
        race.append(tmp_race)

    tmpPlayers = my_replay['game']['teamHome']['playerArray']
    tmp_team_id = my_replay['game']['teamHome']['teamId']
    tmp_race = my_replay['game']['teamHome']['race']

    for playerIndex in range(len(tmpPlayers)):
        playerId.append(tmpPlayers[playerIndex]['playerId'])
        playerNr.append(tmpPlayers[playerIndex]['playerNr'])
        positionId.append(tmpPlayers[playerIndex]['positionId'])
        playerName.append(tmpPlayers[playerIndex]['playerName'])
        playerType.append(tmpPlayers[playerIndex]['playerType'])
        skillArray.append(tmpPlayers[playerIndex]['skillArray'])
        home_away.append('teamHome')
        teamId.append(tmp_team_id)
        race.append(tmp_race)

    df_players = pd.DataFrame( {"teamId": teamId,
                        "playerId": playerId, 
                        "playerNr": playerNr,
                        "positionId": positionId,
                        "playerName": playerName,
                        "playerType": playerType,
                        "skillArray": skillArray,
                        "home_away": home_away,
                        "race": race})
    
    return df_players

