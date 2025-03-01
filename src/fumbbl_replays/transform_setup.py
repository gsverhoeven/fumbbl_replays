from .parse_boardpos import parse_boardpos

def transform_setup(gamelog, df_roster, setup_id = 1):
    res = gamelog.query("set_up_id == @setup_id")

    res = res.sort_values('gameTime', ascending=False).drop_duplicates(['modelChangeKey']).sort_values('PlayerCoordinateX')
    res = res.query("PlayerCoordinateX >= 0 & PlayerCoordinateX < 26")
    #loop over X-axis
    # build up JSON
    positions = []
    for r in range(len(res)):
        playerId = str(res.iloc[r]['modelChangeKey'])
        boardpos = parse_boardpos(res.iloc[r])
        positions.append(df_roster.query('playerId == @playerId')['short_name'].values[0] + ': ' + boardpos)

    setup = ['setup', positions]
    return setup