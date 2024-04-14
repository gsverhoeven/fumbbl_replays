def from_steps_to_trajectories(df):
    # transform sequences of moves into trajectories
    trajectory = []
    path = [] # 2d
    list_of_paths = []
    keep = []

    xy_mode = 0 # trajectory gather mode
    active_player_id = "0"
    trajectory_id = 0

    for r in range(len(df)):
        if (df.iloc[r]['modelChangeId'] == "fieldModelSetPlayerCoordinate") \
            & (df.iloc[r]['turnMode'] != "setup"): # grow trajectory
            if xy_mode == 0:
                xy_mode = 1
                active_player_id = df.iloc[r]['modelChangeKey']
                trajectory_id += 1
                trajectory[-1] = trajectory_id                
                path = []
            else: # xy_mode == 1
                if (active_player_id != df.iloc[r]['modelChangeKey']): # switch naar nieuwe player
                    active_player_id = df.iloc[r]['modelChangeKey']
                    trajectory_id += 1
                    trajectory[-1] = trajectory_id
                    path = []
            # do stuff
            trajectory.append(trajectory_id)
            boardpos = parse_boardpos(df.iloc[r])
            path.append(boardpos)  
            list_of_paths.append(path[:])
            # check for end of trajectory
            if (df.iloc[r+1]['modelChangeId'] != "fieldModelSetPlayerCoordinate"):
                if (df.iloc[r+1]['modelChangeId'] != "fieldModelSetBallCoordinate"):
                    xy_mode = 0
                    keep.append(1)
                else:
                    if (df.iloc[r+1]['modelChangeKey'] == active_player_id):
                        keep.append(0)
                    else:
                        xy_mode = 0
                        keep.append(1)
            elif ( df.iloc[r+1]['modelChangeKey'] != active_player_id):
                xy_mode = 0
                keep.append(1)
            else:
                keep.append(0)
        elif (df.iloc[r]['modelChangeId'] == "fieldModelSetBallCoordinate"): # BALL MOVES BEFORE PLAYER
            if(df.iloc[r+1]['modelChangeId'] == "fieldModelSetPlayerCoordinate"): # two step pattern matching: first check setball/setplayer combi
                if(str(df.iloc[r]['modelChangeValue']) == str(df.iloc[r+1]['modelChangeValue'])): # then check if new positions are the same
                    keep.append(0)
                else: # when positions differ we want to keep the setball as separate row
                    keep.append(1)
            else:
                keep.append(0)
            boardpos = parse_boardpos(df.iloc[r])
            df.iat[r, df.columns.get_loc('modelChangeValue')] = [boardpos]
            trajectory.append(-1)    
            list_of_paths.append(path[:])                                    
        else:
            keep.append(0)
            path = []
            trajectory.append(-1)
            list_of_paths.append(path[:]) # by value, not by reference

    df['list_of_paths'] = list_of_paths
    df['keep'] = keep
    # drop unnecessary move rows
    df = df.query('~(turnMode == "regular" & modelChangeId == "fieldModelSetPlayerCoordinate" & keep == 0)')
    df = df.query('~(turnMode == "regular" & modelChangeId == "fieldModelSetBallCoordinate" & keep == 0)')
    # write full trajectory over the last xy coordinate
    mask = (df.keep == 1)
    df.loc[mask, 'modelChangeValue'] = df.loc[mask, 'list_of_paths']
    return df