def extract_rosters_from_replay(my_replay):
    positionId = []
    positionName = []
    icon_path = []

    tmpRosters = my_replay['game']['teamAway']['roster']

    for positionIndex in range(len(tmpRosters['positionArray'])):
        tmpPosition = tmpRosters['positionArray'][positionIndex]
        positionId.append(tmpPosition['positionId'])
        positionName.append(tmpPosition['positionName'])
        icon_path.append(tmpRosters['baseIconPath'] + tmpPosition['urlIconSet'])

    tmpRosters = my_replay['game']['teamHome']['roster']

    for positionIndex in range(len(tmpRosters['positionArray'])):
        tmpPosition = tmpRosters['positionArray'][positionIndex]
        positionId.append(tmpPosition['positionId'])
        positionName.append(tmpPosition['positionName'])
        icon_path.append(tmpRosters['baseIconPath'] + tmpPosition['urlIconSet'])

    df_positions = pd.DataFrame( {"positionId": positionId,
                                "positionName": positionName,
                                "icon_path": icon_path
                                })
    df_positions.drop_duplicates(inplace = True, ignore_index = True)

    df_players = extract_players_from_replay(my_replay)

    df_roster = pd.merge(df_players, df_positions, on="positionId", how="left")
    df_roster = df_roster.drop(['teamId', 'positionId', 'playerName', 'playerType', 'icon_path'], axis=1)    

    # create shorthand id
    short_name = []

    for r in range(len(df_roster)):
        input = str(df_roster.iloc[r]['positionName'])
        output = "".join(item[0].upper() for item in input.split()) + str(df_roster.iloc[r]['playerNr'])
        short_name.append(output)

    df_roster['short_name'] = short_name

    return df_roster
