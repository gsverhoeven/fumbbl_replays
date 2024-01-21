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
                        print(tmpChange['modelChangeValue']['dialogId'])                    
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
    
    df['gameTime'] = df['gameTime']/1000
    df['turnTime'] = df['turnTime']/1000
    # add state descriptions
    cl_state = pd.read_csv("resources/PlayerState.csv")
    df = pd.merge(left = df, right = cl_state, left_on = "SetPlayerState", right_on = "INT", how = "left", sort = False)
    # add location descriptions
    cl_location = pd.read_csv("resources/Coordinate.csv")
    df = pd.merge(left = df, right = cl_location, left_on = "PlayerCoordinateX", right_on = "VALUE", how = "left", sort = False)
    df = df.drop(['INT', 'VALUE'], axis=1)

    if to_excel:
        df.to_excel("output.xlsx")  
       
    return df

