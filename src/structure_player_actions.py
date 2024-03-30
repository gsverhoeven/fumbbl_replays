def structure_player_actions(df):
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
                keep.append(0) # not keeping these rows
            else:
                keep.append(1)
        elif (df.iloc[r]['modelChangeId'] == "block"): # not keeping these rows
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

    # drop unnecessary rows:
    #
    df = df.query('keep2 == 1')
    # choosingTeam can be deduced from player info (roster)
    df = df.query('~(modelChangeId == "blockRoll" & playerAction == "block")') 
    # deduce movement action from actual movement
    df = df.query('~(modelChangeId == "playerAction" & playerAction == "move")') 

    return df