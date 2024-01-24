def parse_replay(my_replay, to_excel = False):
    modelChangeId = []
    modelChangeKey = []
    modelChangeValue = []
    SetPlayerCoordinate = []
    SetPlayerState = []
    PlayerCoordinateX = []
    PlayerCoordinateY = []
    commandNr = []
    turnNr = []
    TurnCounter = 0
    turnMode = []
    Half = []
    gameTime = []
    turnTime = []
    reportValue = []

    my_gamelog = my_replay['gameLog']

    ignoreList = pd.read_csv("resources/IgnoreModelChange.csv")

    ignoreList = ignoreList['modelChangeId'].values

    ignoreList2 = pd.read_csv("resources/IgnoreDialog.csv")

    ignoreList2 = ignoreList2['dialogId'].values

    ignoreList3 = pd.read_csv("resources/IgnoreReport.csv")

    ignoreList3 = ignoreList3['reportId'].values    

    for commandIndex in range(len(my_gamelog['commandArray'])):
        tmpCommand = my_gamelog['commandArray'][commandIndex]
        if tmpCommand['netCommandId'] == "serverModelSync":
            for modelChangeIndex in range(len(tmpCommand['modelChangeList']['modelChangeArray'])):

                tmpChange = tmpCommand['modelChangeList']['modelChangeArray'][modelChangeIndex]
                
                if str(tmpChange['modelChangeId']) not in ignoreList:              
                    if (str(tmpChange['modelChangeId']) == 'gameSetDialogParameter') & \
                    (tmpChange['modelChangeValue'] == None):
                        pass
                    elif (str(tmpChange['modelChangeId']) == 'gameSetDialogParameter') & \
                    (isinstance(tmpChange['modelChangeValue'], dict)):
                        #print(tmpChange['modelChangeValue']['dialogId'])                    
                        pass
                    else:
                        if str(tmpChange['modelChangeId']) == 'gameSetHalf':
                            Half.append(tmpChange['modelChangeValue'])
                        else:
                            if len(Half) == 0:
                                Half.append(0)
                            else:
                                Half.append(Half[-1])
                                            
                        if str(tmpChange['modelChangeId']) == 'gameSetTurnMode':
                            turnMode.append(tmpChange['modelChangeValue'])
                        else:
                            if len(turnMode) == 0:
                                turnMode.append('startGame')
                            else:
                                turnMode.append(turnMode[-1])

                        if str(tmpChange['modelChangeId']) == 'turnDataSetTurnNr':
                            TurnCounter = tmpChange['modelChangeValue']

                        turnNr.append(TurnCounter)
                        commandNr.append(tmpCommand['commandNr'])
                        modelChangeId.append(tmpChange['modelChangeId'])
                        modelChangeKey.append(tmpChange['modelChangeKey'])
                        modelChangeValue.append(tmpChange['modelChangeValue'])
                        turnTime.append(tmpCommand['turnTime'])
                        gameTime.append(tmpCommand['gameTime'])

                        if str(tmpChange['modelChangeId']) == "fieldModelSetPlayerCoordinate":
                            SetPlayerCoordinate.append(1)
                            PlayerCoordinateX.append(tmpChange['modelChangeValue'][0])
                            PlayerCoordinateY.append(tmpChange['modelChangeValue'][1])
                        else:
                            SetPlayerCoordinate.append(0)
                            PlayerCoordinateX.append(99)
                            PlayerCoordinateY.append(99)

                        if str(tmpChange['modelChangeId']) == "fieldModelSetPlayerState":
                            # so first 8 bits (0-255) are reserved to encode mutually exclusive stuff, and then we have the BIT section
                            # so we convert to bits, then use the first 8 bits for the unique state, and then decorate the player using bits 9 to 14
                            SetPlayerState.append(tmpChange['modelChangeValue'] & 255)
                        else:
                            SetPlayerState.append(0)

            for reportListIndex in range(len(tmpCommand['reportList']['reports'])):                     
                tmpReport = tmpCommand['reportList']['reports'][reportListIndex]

                turnNr.append(TurnCounter)
                commandNr.append(tmpCommand['commandNr'])
                modelChangeId.append("reportList")
                modelChangeKey.append(reportListIndex)
                modelChangeValue.append(tmpReport)
                turnTime.append(tmpCommand['turnTime'])
                gameTime.append(tmpCommand['gameTime'])
                SetPlayerCoordinate.append(0)
                PlayerCoordinateX.append(99)
                PlayerCoordinateY.append(99)
                SetPlayerState.append(0)     
                turnMode.append(turnMode[-1])    
                Half.append(Half[-1])                      

        elif tmpCommand['netCommandId'] == "serverAddPlayer":
            pass
        else:
            # unknown netCommand: print it
            print(tmpCommand['netCommandId'])

    df = pd.DataFrame( {"commandNr": commandNr, 
                        "gameTime": gameTime,
                        "turnTime": turnTime,
                        "Half": Half,
                        "turnNr": turnNr,
                        "turnMode": turnMode,
                        "modelChangeId": modelChangeId,
                        "modelChangeKey": modelChangeKey,
                        "modelChangeValue": modelChangeValue,
                        "SetPlayerCoordinate": SetPlayerCoordinate,
                        "PlayerCoordinateX": PlayerCoordinateX,
                        "PlayerCoordinateY": PlayerCoordinateY,
                        "SetPlayerState": SetPlayerState})
    
    # from ms to s
    df['gameTime'] = df['gameTime']/1000
    df['turnTime'] = df['turnTime']/1000

    # drop rows with gameSetTurnMode
    df = df.query("modelChangeId != 'gameSetTurnMode'")
    # add state descriptions
    cl_state = pd.read_csv("resources/PlayerState.csv")
    df = pd.merge(left = df, right = cl_state, left_on = "SetPlayerState", right_on = "INT", how = "left", sort = False)
    df = df.drop(['DESCRIPTION'], axis = 1)
    # add location descriptions
    cl_location = pd.read_csv("resources/Coordinate.csv")
    df = pd.merge(left = df, right = cl_location, left_on = "PlayerCoordinateX", right_on = "VALUE", how = "left", sort = False)
    df = df.drop(['INT', 'VALUE', 'SetPlayerCoordinate', 'PlayerCoordinateX', 'PlayerCoordinateY', 'SetPlayerState'], axis = 1)

    # transform sequences of moves into trajectories
    xy_mode = []
    trajectory = []
    path = [] # 2d
    list_of_paths = []

    toggle_xy_mode = 0
    active_player_id = "0"
    trajectory_id = 0

    
    for r in range(len(df)):
        if df.iloc[r]['modelChangeId'] == "fieldModelSetPlayerCoordinate":
            # need to fix: ignore fieldModelSetBallCoordinate for player carrier the ball (maybe drop this field?)
            if toggle_xy_mode == 0:
                toggle_xy_mode = 1
                path = []
            if (active_player_id != df.iloc[r]['modelChangeKey']): # & (active_player_id > 0):
                trajectory_id += 1
                trajectory[-1] = trajectory_id
                path = []
            # do stuff
            trajectory.append(trajectory_id)
            path.append(df.iloc[r]['modelChangeValue'])  
            list_of_paths.append(path)          
            active_player_id = df.iloc[r]['modelChangeKey']
        else:
            toggle_xy_mode = 0
            #print(path)
            path = []
            trajectory.append(-1)
            list_of_paths.append(path)
        xy_mode.append(toggle_xy_mode)

        
    df['xy_mode'] = xy_mode
    df['trajectory'] = trajectory
    df['list_of_paths'] = list_of_paths            

    if to_excel:
        path = 'output/output.xlsx'
        writer = pd.ExcelWriter(path, engine = 'openpyxl')
        df.to_excel(writer, sheet_name = 'gamelog')
        df_players = extract_players_from_replay(my_replay)
        df_positions = extract_rosters_from_replay(my_replay)

        df2 = pd.merge(df_players, df_positions, on="positionId", how="left")
        df2 = df2.drop(['teamId', 'positionId', 'playerName', 'playerType', 'icon_path'], axis=1)
        df2.to_excel(writer, sheet_name = 'roster')
        writer.close()
       
    return df

