import pandas as pd

def extract_players_from_replay(my_replay):
 
    df_players_home = json2pd_replay_players(my_replay['game']['teamHome'], home_away_str = 'teamHome')
    df_players_away = json2pd_replay_players(my_replay['game']['teamAway'], home_away_str = 'teamAway')

    df_players = pd.concat([df_players_home, df_players_away])
 
    return df_players

def json2pd_replay_players(json_players, home_away_str):
    playerId = []
    playerNr = []
    positionId = []
    playerName = []
    playerType = []
    skillArray = []
    home_away = []
    teamId = []
    race = []
    recoveringInjury = []

    tmpPlayers = json_players['playerArray']
    tmp_team_id = json_players['teamId']
    tmp_race = json_players['race']

    for playerIndex in range(len(tmpPlayers)):
        playerId.append(tmpPlayers[playerIndex]['playerId'])
        playerNr.append(tmpPlayers[playerIndex]['playerNr'])
        positionId.append(tmpPlayers[playerIndex]['positionId'])
        playerName.append(tmpPlayers[playerIndex]['playerName'])
        playerType.append(tmpPlayers[playerIndex]['playerType'])
        skillArray.append(tmpPlayers[playerIndex]['skillArray'])
        home_away.append(home_away_str)
        teamId.append(tmp_team_id)
        race.append(tmp_race)
        recoveringInjury.append(tmpPlayers[playerIndex]['recoveringInjury'])

    df_players = pd.DataFrame( {"teamId": teamId,
                "playerId": playerId, 
                "playerNr": playerNr,
                "positionId": positionId,
                "playerName": playerName,
                "playerType": playerType,
                "skillArray": skillArray,
                "home_away": home_away,
                "race": race,
                "recoveringInjury": recoveringInjury})
    
    return df_players