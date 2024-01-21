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

    return df_positions
