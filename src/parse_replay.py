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

    my_gamelog = my_replay['gameLog']

    ignoreList = pd.read_csv("resources/IgnoreModelChange.csv")

    ignoreList = ignoreList['modelChangeId'].values

    # extract rosters
    df_roster = extract_rosters_from_replay(my_replay)

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

   # add header (coaches, source etc)
    
    df_header = pd.DataFrame( {"commandNr": [0, 0], 
                        "gameTime": [0, 0],
                        "turnTime": [0, 0],
                        "Half": [0, 0],
                        "turnNr": [0, 0],
                        "turnMode": ["startGame", "startGame"],
                        "modelChangeId": ["homeCoachName", "awayCoachName"],
                        "modelChangeKey": [0, 0],
                        "modelChangeValue": [my_replay['game']['teamHome']['coach'], my_replay['game']['teamAway']['coach']],
                        "SetPlayerCoordinate": ["", ""],
                        "PlayerCoordinateX": [99, 99],
                        "PlayerCoordinateY": [99, 99],
                        "SetPlayerState": [0, 0]}, index = [0, 1])

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
    
    df = pd.concat([df_header, df], ignore_index=True)
    
    # from ms to s
    df['gameTime'] = df['gameTime']/1000
    df['turnTime'] = df['turnTime']/1000

    # here we can drop rows with gameSetTurnMode (needed for initial parsing above)
    df = df.query("modelChangeId != 'gameSetTurnMode'")
    # add state descriptions
    cl_state = pd.read_csv("resources/PlayerState.csv")
    df = pd.merge(left = df, right = cl_state, left_on = "SetPlayerState", right_on = "INT", how = "left", sort = False)
    df = df.drop(['DESCRIPTION'], axis = 1)
    # add location descriptions
    cl_location = pd.read_csv("resources/Coordinate.csv")
    df = pd.merge(left = df, right = cl_location, left_on = "PlayerCoordinateX", right_on = "VALUE", how = "left", sort = False)
  
    # transform sequences of moves into trajectories
    trajectory = []
    path = [] # 2d
    list_of_paths = []
    keep = []

    xy_mode = 0 # trajectory gather mode
    keep_setball = 0
    active_player_id = "0"
    trajectory_id = 0

    for r in range(len(df)):
        if (df.iloc[r]['modelChangeId'] == "fieldModelSetPlayerCoordinate") \
            & (df.iloc[r]['turnMode'] != "setup"):
            if xy_mode == 0:
                xy_mode = 1
                path = []
            if (active_player_id != df.iloc[r]['modelChangeKey']): # & (active_player_id > 0):
                trajectory_id += 1
                trajectory[-1] = trajectory_id
                path = []
            # do stuff
            trajectory.append(trajectory_id)
            path.append(df.iloc[r]['modelChangeValue'])  
            list_of_paths.append(path[:])          
            active_player_id = df.iloc[r]['modelChangeKey']
            keep.append(0)
        elif (df.iloc[r]['modelChangeId'] == "fieldModelSetBallCoordinate"):
            if(df.iloc[r+1]['modelChangeId'] == "fieldModelSetPlayerCoordinate"): # two step pattern matching: first check setball/setplayer combi
                if(df.iloc[r]['modelChangeValue'] == df.iloc[r+1]['modelChangeValue']): # then check if new positions are the same
                    keep.append(0)
                    keep_setball = 0
                else: # when positions differ we want to keep the setball as separate row
                    keep.append(0)
                    keep_setball = 1
            else:
                keep.append(0)
                keep_setball = 1
            trajectory.append(-1)    
            list_of_paths.append(path[:])                                    
        else:
            if(xy_mode == 1):
                keep.append(1)
            elif(keep_setball == 1):
                keep.append(1)
                keep_setball = 0
            else:
                keep.append(0)
            xy_mode = 0
            #print(path)
            path = []
            trajectory.append(-1)
            list_of_paths.append(path[:]) # by value, not by reference

    df['list_of_paths'] = list_of_paths
    keep.append(0) 
    df['keep'] = keep[1:] # shift all elements up to align with record we want to keep          
    
    # drop unnecessary move rows
    df = df.query('~(turnMode == "regular" & modelChangeId == "fieldModelSetPlayerCoordinate" & keep == 0)')
    df = df.query('~(turnMode == "regular" & modelChangeId == "fieldModelSetBallCoordinate" & keep == 0)')
    # cleanup last xy coordinate
    mask = (df.keep == 1)
    df.loc[mask, 'modelChangeValue'] = df.loc[mask, 'list_of_paths']
   
    playerAction = []
    defenderId = []
    keep = []
    current_active_player = 0
    current_defender_id = 0
    current_action = "none"

    for r in range(len(df)):
        if (df.iloc[r]['turnMode'] != "regular"):   # IE also during setup     
            # https://note.nkmk.me/en/python-pandas-at-iat-loc-iloc/
            str_orig =  str(df.iloc[r]['modelChangeValue'])
            replace_x = "_" + str(df.iloc[r]['DESCRIPTION'])
            if (replace_x == "_nan"):
                replace_x = ""
            df.iat[r, df.columns.get_loc('modelChangeValue')] = str_orig + replace_x          
            playerAction.append("none")
            defenderId.append(0)
            keep.append(1)           
        elif (df.iloc[r]['modelChangeId'] == "playerAction"):
            current_action = df.iloc[r]['modelChangeValue']['playerAction']
            current_active_player = df.iloc[r]['modelChangeValue']['actingPlayerId']
            df.iat[r, df.columns.get_loc('modelChangeKey')] = current_active_player
            defenderId.append(0)
            playerAction.append(current_action)
            if (current_action == "block"): 
                keep.append(0)
            else:
                keep.append(1)
        elif (df.iloc[r]['modelChangeId'] == "block"): 
            df.iat[r, df.columns.get_loc('modelChangeKey')] = current_active_player
            playerAction.append(current_action)
            current_defender_id = df.iloc[r]['modelChangeValue']['defenderId']
            defenderId.append(current_defender_id)
            keep.append(0)
        elif (df.iloc[r]['modelChangeId'] == "blockChoice"):
            df.iat[r, df.columns.get_loc('modelChangeKey')] = current_active_player
            playerAction.append(current_action)
            defenderId.append(current_defender_id)
            # final block record, so reset values
            current_active_player = 0
            current_defender_id = 0
            current_action = "none"
            keep.append(1)
        elif (df.iloc[r]['modelChangeId'] == "fieldModelSetPlayerCoordinate"):      
            str_orig =  str(df.iloc[r]['modelChangeValue'])
            replace_x = "_" + str(df.iloc[r]['DESCRIPTION'])
            if (replace_x == "_nan"):
                replace_x = ""
            df.iat[r, df.columns.get_loc('modelChangeValue')] = str_orig + replace_x  
            df.iat[r, df.columns.get_loc('modelChangeKey')] = current_active_player
            playerAction.append(current_action)
            defenderId.append(current_defender_id)
            keep.append(1)
        else:
            if current_active_player != 0:
                df.iat[r, df.columns.get_loc('modelChangeKey')] = current_active_player
            playerAction.append(current_action)
            defenderId.append(current_defender_id)
            keep.append(1)


    df['playerAction'] = playerAction
    df['defenderId'] = defenderId
    df['keep2'] = keep      

    # drop unnecessary rows
    df = df.query('keep2 == 1')
    df = df.query('~(modelChangeId == "blockRoll" & playerAction == "block")') # choosingTeam can be deduced from player info (roster)
    df = df.query('~(modelChangeId == "playerAction" & playerAction == "move")') # deduce movement action from actual movement

    # flag placing players in dugout during setup
    # needed to ID players that are initially placed on board but are moved to dugout later during setup
    row_sel = '(turnMode == "setup" & modelChangeId == "fieldModelSetPlayerCoordinate" & ((PlayerCoordinateX < 0) | (PlayerCoordinateX > 25)))'
    df['to_dugout'] = 0
    df.loc[df.eval(row_sel), 'to_dugout'] = 1
    
    # post processing ignoreList handcoded (either reportList or modelChangeId)
    df = df.query('~(modelChangeId in ["turnDataSetTurnNr", \
                  "turnDataSetFirstTurnAfterKickoff", \
                  "fumbblResultUpload"])')

    # compact setting up
    set_up_id = 0
    setupIdCol = []

    for r in range(len(df)):
        if df.iloc[r]['turnMode'] == 'setup':
            if df.iloc[r]['to_dugout'] == 0: # placing all players in dugout at end of half is not counted as setupFormation for the gamelog
                if df.iloc[r-1]['turnMode'] != 'setup': # entering setup mode
                    set_up_id += 1
                setupIdCol.append(set_up_id)
                if df.iloc[r]['modelChangeId'] == 'gameSetSetupOffense':
                    if df.iloc[r]['modelChangeValue'] == 'True':
                        set_up_id += 1
            else: 
                setupIdCol.append(set_up_id)
        else:
            setupIdCol.append(-1)
    
    df['set_up_id'] = setupIdCol

    # roll up, one row per setup
    df_setup = (df
    .query('set_up_id > 0 & modelChangeId == "fieldModelSetPlayerCoordinate"')
    .groupby(['turnTime', 'Half', 'turnNr', 'turnMode', 'set_up_id', 'playerAction'], as_index = False)
    .agg(
        gameTime = ('gameTime', 'max')
    )
    .sort_values(by=['set_up_id']) 
    )

    # generate compact setups, add to df_setup
    setup_list = []
    for cnt in df_setup['set_up_id']:
        setup_list.append(transform_setup(df, df_roster, setup_id = cnt))

    df_setup['modelChangeId'] = "gameSetupFormation"
    df_setup['modelChangeKey'] = 0
    df_setup['defenderId'] = 0
    df_setup['modelChangeValue'] = setup_list

    # drop setting up players one by one from gamelog
    df = df.query('~(turnMode == "setup" & modelChangeId == "fieldModelSetPlayerCoordinate")') 
   
    # add compact setups to gamelog df
    df = pd.concat([df, df_setup])
    df.index.name = 'MyIdx'
    df = df.sort_values(by = ['gameTime', 'MyIdx'], ascending = [True, True])
    df = df.reset_index()

    # replace player IDs with shorthands
    
    # occur in three columns: modelChangeKey, defenderId and reportList
    for playerId in df_roster['playerId'].values:
        short_hand = df_roster.loc[df_roster.eval("playerId == @playerId"), 'short_name']
        df.loc[df.eval("modelChangeKey == @playerId"), 'modelChangeKey'] = str(short_hand.values)
        df.loc[df.eval("defenderId == @playerId"), 'defenderId'] = str(short_hand.values)

    # finally fix all reportLists
    
    for r in range(len(df)):
        #print(r)
        # check if it is a reportList
        if 'reportId' in str(df.iloc[r]['modelChangeValue']):
            reportlist = df.iloc[r]['modelChangeValue']
            if not isinstance(reportlist, dict):
                # convert to valid JSON
                json_reportList = reportlist.replace("'", '"').replace("False", "false").replace("True", "true").replace("None", "null")
                # convert to dict
                reportlist = json.loads(json_reportList)
            if 'playerId' in reportlist:
                playerId = reportlist['playerId'] 
                short_hand = df_roster.loc[df_roster.eval("playerId == @playerId"), 'short_name'] 
                reportlist['playerId'] = str(short_hand.values)
                df.iat[r, df.columns.get_loc('modelChangeValue')] = reportlist
            if 'defenderId' in reportlist:
                playerId = reportlist['defenderId'] 
                short_hand = df_roster.loc[df_roster.eval("playerId == @playerId"), 'short_name'] 
                reportlist['defenderId'] = str(short_hand.values)
                df.iat[r, df.columns.get_loc('modelChangeValue')] = reportlist
            if 'attackerId' in reportlist:
                playerId = reportlist['attackerId'] 
                short_hand = df_roster.loc[df_roster.eval("playerId == @playerId"), 'short_name'] 
                reportlist['attackerId'] = str(short_hand.values)
                df.iat[r, df.columns.get_loc('modelChangeValue')] = reportlist   
            if 'catcherId' in reportlist:
                playerId = reportlist['catcherId'] 
                short_hand = df_roster.loc[df_roster.eval("playerId == @playerId"), 'short_name'] 
                reportlist['catcherId'] = str(short_hand.values)
                df.iat[r, df.columns.get_loc('modelChangeValue')] = reportlist                     
        else:
            pass


    if to_excel:
        path = 'output/output.xlsx'
        writer = pd.ExcelWriter(path, engine = 'openpyxl')

        cols = ['gameTime', 'turnTime', 'Half',  'turnNr', 'turnMode', 'set_up_id', \
                 'playerAction', 'modelChangeId', 'modelChangeKey', 'defenderId', 'modelChangeValue']
        
        df.to_excel(writer, sheet_name = 'gamelog', columns = cols) # define selection plus order
        df_roster.to_excel(writer, sheet_name = 'roster')
        writer.close()
       
    return df

