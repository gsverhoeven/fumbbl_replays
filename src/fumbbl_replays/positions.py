import re
import string
import pandas as pd
from .parse_boardpos import parse_boardpos

def create_position(roster, setup, home_away = 'teamHome'):
    boardpos = []
    piece = []
    position_code = []
    CoordinateX = []
    CoordinateY = []
    PlayerCoordinateY = []
    PlayerState = []
    PlayerNr = []

    if setup[0] != 'setup':
        print("not a setup list")
        return -1
    if len(setup[1]) > 11:
        print("too many pieces")
        return -1
    for p in range(len(setup[1])):
        PlayerNr.append(p + 1)
        if setup[1][p][-1] == 'X':
            PlayerState.append("Stunned")
            setup[1][p] = setup[1][p][:-1]
        elif setup[1][p][-1] == '/':
            PlayerState.append("Prone")
            setup[1][p] = setup[1][p][:-1]
        elif setup[1][p][-1] == 'o':
            PlayerState.append("HasBall")
            setup[1][p] = setup[1][p][:-1]            
        else:
            PlayerState.append("Standing")
        move_code = setup[1][p].split() # split on :
        piece.append(move_code[0][:-1])
        new_pos = move_code[1]
        boardpos.append(new_pos)
        CoordinateX.append(int(new_pos[1:]))
        CoordinateY.append(new_pos[0])
        PlayerCoordinateY.append(string.ascii_lowercase.index(new_pos[0]))
        # player position code
        position_code.append(re.split(r'([\d]+)', move_code[0][:-1], 1)[0])
        
    positions = pd.DataFrame( {"PlayerNr": PlayerNr,
                    "boardpos": boardpos,
                    "short_name": piece,
                    "position_code": position_code,
                    "CoordinateX": CoordinateX,
                    "CoordinateY": CoordinateY,
                    "PlayerCoordinateY": PlayerCoordinateY,
                    "PlayerState": PlayerState
                    })
    
    positions = pd.merge(positions, roster, left_on='position_code', right_on='shorthand', how="left")

    positions['home_away'] = home_away
    positions['PlayerCoordinateX'] = positions['CoordinateX'] - 1
    positions['learned_skills'] = [[] for _ in range(len(positions))]
    positions['skill_colors'] = [[] for _ in range(len(positions))]
    positions.rename({'skillArray':'skillArrayRoster'}, axis=1, inplace = True)
    
    return positions

def print_position(positions, home_away = 'both'):
    res = (positions
    #.query("home_away == 'teamAway'")
    .assign(boardpos = lambda x: x.CoordinateY + x.CoordinateX.astype(str))
    .sort_values(['CoordinateX', 'CoordinateY'])
    .filter(['home_away', 'race', 'short_name', 'positionName', 'boardpos', 'PlayerState']) 
    )
    if home_away != 'both':
        if home_away in ['teamHome', 'teamAway']:
           res = res.query("home_away == @home_away")
        else:
            print("error, cannot select team")
    return res

def move_piece(positions, home_away, short_name, new_pos):
    coord_y = new_pos[0]
    coord_x = int(new_pos[1:])
    mask = (positions.short_name == short_name) & (positions.home_away == home_away)
    if sum(mask) == 0:
        print("piece not on board")
        return positions
    positions.loc[mask, 'PlayerCoordinateX'] = coord_x - 1
    positions.loc[mask, 'PlayerCoordinateY'] = string.ascii_lowercase.index(coord_y)
    positions.loc[mask, 'CoordinateX'] = coord_x
    positions.loc[mask, 'CoordinateY'] = coord_y
    positions.loc[mask, 'modelChangeValue'] = '[' + str(coord_x - 1) + ',' + str(string.ascii_lowercase.index(coord_y) - 1) + ']'

    return positions

def set_piece_state(positions, home_away, short_name, new_state):
    mask = (positions.short_name == short_name) & (positions.home_away == home_away)
    if sum(mask) == 0:
        print("piece not on board")
        return positions
    if new_state in ['Standing', 'HasBall', 'Prone', 'Stunned']:
        positions.loc[mask, 'PlayerState'] = new_state
    else:
        print("unknown state")
    return positions
        
def put_position(positions, setup, home_away):
    if setup[0] != 'setup':
        print("not a setup list")
        return(positions)
    if len(setup[1]) > 11:
        print("too many pieces")
        return(positions)
    for p in range(len(setup[1])):
        move_code = setup[1][p].split()
        piece = move_code[0][:-1]
        new_pos = move_code[1]
        move_piece(positions, home_away, piece, new_pos)
    return positions

def get_position(positions, home_away = 'teamHome'):
    positions = positions.query("home_away == @home_away")
    position = []
    for r in range(len(positions)):
        PlayerNr = str(positions.iloc[r]['PlayerNr'])
        boardpos = parse_boardpos(positions.iloc[r])
        if positions.iloc[r]['PlayerState'] == 'Prone':
            boardpos = boardpos + '/'
        elif positions.iloc[r]['PlayerState'] == 'Stunned':
            boardpos = boardpos + 'X'
        elif positions.iloc[r]['PlayerState'] == 'HasBall':
            boardpos = boardpos + 'o'
        else:
            pass
        position.append(positions.query('PlayerNr.astype("str") == @PlayerNr')['short_name'].values[0] + ': ' + boardpos)

    setup = ['setup', position]
    return print(setup)