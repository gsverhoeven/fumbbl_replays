def transform_setup(gamelog, df_roster, setup_id = 1):
    res = gamelog.query("set_up_id == @setup_id")

    res = res.sort_values('gameTime', ascending=False).drop_duplicates(['modelChangeKey']).sort_values('gameTime')

    #loop over X-axis
    # build up JSON
    setup = ['setup']
    for boardrow in range(12, -1, -1):
        positions = []
        tmp = res.query("PlayerCoordinateX == @boardrow")
        for r in range(len(tmp)):
            playerId = str(tmp.iloc[r]['modelChangeKey'])
            boardpos = parse_boardpos(tmp.iloc[r])
            positions.append(df_roster.query('playerId == @playerId')['short_name'].values[0] + ': ' + boardpos)
        #print(positions)
        if len(tmp) > 0:
            setup.append(positions)
    
    for boardrow in range(13, 26, 1):
        positions = []
        tmp = res.query("PlayerCoordinateX == @boardrow")
        for r in range(len(tmp)):
            playerId = str(tmp.iloc[r]['modelChangeKey'])
            boardpos = parse_boardpos(tmp.iloc[r])
            positions.append(df_roster.query('playerId == @playerId')['short_name'].values[0] + ': ' + boardpos)
        #print(positions)
        if len(tmp) > 0:
            setup.append(positions)

    return setup