def extract_rosters_from_replay(my_replay):
    positionId = []
    positionName = []
    shorthand = []
    icon_path = []

    tmpRosters = my_replay['game']['teamAway']['roster']

    for positionIndex in range(len(tmpRosters['positionArray'])):
        tmpPosition = tmpRosters['positionArray'][positionIndex]
        positionId.append(tmpPosition['positionId'])
        positionName.append(tmpPosition['positionName'])
        shorthand.append(tmpPosition['shorthand'])
        icon_path.append(tmpRosters['baseIconPath'] + tmpPosition['urlIconSet'])

    tmpRosters = my_replay['game']['teamHome']['roster']

    for positionIndex in range(len(tmpRosters['positionArray'])):
        tmpPosition = tmpRosters['positionArray'][positionIndex]
        positionId.append(tmpPosition['positionId'])
        positionName.append(tmpPosition['positionName'])
        shorthand.append(tmpPosition['shorthand'])        
        icon_path.append(tmpRosters['baseIconPath'] + tmpPosition['urlIconSet'])

    df_positions = pd.DataFrame( {"positionId": positionId,
                                "positionName": positionName,
                                "shorthand": shorthand,
                                "icon_path": icon_path
                                })
    df_positions.drop_duplicates(inplace = True, ignore_index = True)

    df_players = extract_players_from_replay(my_replay)

    df_roster = pd.merge(df_players, df_positions, on="positionId", how="left")
    df_roster = df_roster.drop(['teamId', 'positionId', 'playerName', 'playerType', 'icon_path'], axis=1)    
    df_roster['positionNr'] = df_roster.groupby(['home_away','positionName']).cumcount() + 1
    # create shorthand id
    df_roster['short_name'] = df_roster['shorthand'] + df_roster['positionNr'].astype(str)
    return df_roster
