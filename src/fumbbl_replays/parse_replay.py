import pandas as pd
import string

def parse_replay(my_replay, ignoreList = None):
    my_gamelog = my_replay['gameLog']

    if ignoreList is not None:
        ignoreList = ignoreList['modelChangeId'].values
    else:
        ignoreList = []
        
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

    # parse gamelog
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
                        elif (str(tmpChange['modelChangeId']) == "fieldModelSetBallCoordinate") \
                            and hasattr(tmpChange['modelChangeValue'], "__len__"): # contents can also be int 0 or None
                            SetPlayerCoordinate.append(0)
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
                modelChangeId.append(tmpReport['reportId'])
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


    # here we can drop rows with gameSetTurnMode (needed for initial parsing above)
    df = df.query("modelChangeId != 'gameSetTurnMode'")   
    # from ms to s
    df['gameTime'] = df['gameTime']/1000
    df['turnTime'] = df['turnTime']/1000     

    changesel = ["fieldModelSetPlayerCoordinate", "fieldModelSetBallCoordinate"]
    row_sel = '(modelChangeId in @changesel & ((PlayerCoordinateY >= 0) & (PlayerCoordinateY <= 14)))'
    df['CoordinateY'] = 0
    df.loc[df.eval(row_sel), 'CoordinateY'] = [string.ascii_lowercase[element] for element in df.loc[df.eval(row_sel), 'PlayerCoordinateY'].astype(int).values]  
    
    # flag placing players in dugout during setup
    # needed to ID players that are initially placed on board but are moved to dugout later during setup
    row_sel = '(turnMode == "setup" & modelChangeId == "fieldModelSetPlayerCoordinate" & ((PlayerCoordinateX < 0) | (PlayerCoordinateX > 25)))'
    df['to_dugout'] = 0
    df.loc[df.eval(row_sel), 'to_dugout'] = 1
                    
    return df
