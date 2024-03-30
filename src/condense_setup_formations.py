def condense_setup_formations(df): 
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
    return df