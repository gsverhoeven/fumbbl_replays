def from_steps_to_trajectories(df):
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
            if (active_player_id != df.iloc[r]['modelChangeKey']): 
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
    # write full trajectory over the last xy coordinate
    mask = (df.keep == 1)
    df.loc[mask, 'modelChangeValue'] = df.loc[mask, 'list_of_paths']
    return df