import pandas as pd
import os

from PIL import Image, ImageDraw, ImageFont
from urllib.request import urlopen

from .fetch_replay import fetch_replay
from .fetch_match import fetch_match
from .parse_replay import parse_replay
from .extract_rosters_from_replay import extract_rosters_from_replay

def add_tacklezones(pitch, positions, receiving_team, flip = False, horizontal = False):
    """Write a separate function that draws semi transparent tackle zones.
    """
    for i in range(len(positions)):
        if horizontal == False:
            x = 14 - positions.iloc[i]['PlayerCoordinateY']
            y = positions.iloc[i]['PlayerCoordinateX']
        else:
            x = positions.iloc[i]['PlayerCoordinateX']
            y = positions.iloc[i]['PlayerCoordinateY']
        
        if flip == True:
            y = 25 - y
        else:
            y = y
            
        team = positions.iloc[i]['home_away']
        icon_path = positions.iloc[i]['icon_path']

        icon = Image.open(urlopen(icon_path)).convert("RGBA")
        icon_w, icon_h = icon.size
        # select first icon
        icon = icon.crop((0,0,icon_w/4,icon_w/4))
        icon = icon.resize((28, 28))
        icon_w, icon_h = icon.size
        if team == receiving_team:
            tacklezone_color = (255, 0, 0) # RGB
        else:
            tacklezone_color = (0, 0, 255)
        box = (icon_w * x - 28, icon_h * y - 28, icon_w * x + 2*28, icon_h * y + 2*28)
        mask = Image.new("L", (3*28, 3*28), 0).convert("RGBA")
        mask.putalpha(50)
        pitch.paste(tacklezone_color, box, mask)
    return pitch

def add_players(pitch, positions, receiving_team, flip = False, horizontal = False):
    square_h = 28
    square_w = 28

    if horizontal == False:
        # sort the positions for drawing the lowest row on the board first
        # horizontal board, X from left to right is correct plotting order if we rotate CCW afterwards
        if flip == False:
            positions = positions.sort_values(by = 'PlayerCoordinateX', \
                                      ascending = True)
        else:
            positions = positions.sort_values(by = 'PlayerCoordinateX', \
                                      ascending = False)

    for i in range(len(positions)):
        #print(positions.iloc[i]['playerName'])
        if horizontal == False:
            x = 14 - positions.iloc[i]['PlayerCoordinateY']
            y = positions.iloc[i]['PlayerCoordinateX']
        else:
            x = positions.iloc[i]['PlayerCoordinateX']
            y = positions.iloc[i]['PlayerCoordinateY']
        
        if flip == True:
            y = 25 - y
        else:
            y = y        
            
        team = positions.iloc[i]['home_away']
        icon_path = positions.iloc[i]['icon_path']

        icon = Image.open(urlopen(icon_path)).convert("RGBA")
        icon_w, icon_h = icon.size

        if team == receiving_team:
            # select first icon
            icon = icon.crop((0,0,icon_w/4,icon_w/4))
        else:
            # select third icon
            icon = icon.crop((icon_w/2, 0, icon_w*3/4, icon_w/4))

        icon_w, icon_h = icon.size # bigger for big guys
        shift_w = icon_w - square_w
        shift_h = icon_h - square_h
        pitch.paste(im = icon, box = (square_w * x - int(shift_w/2), \
                                      square_h * y - shift_h), \
                                        mask = icon)
    return pitch

def pitch_select_lower_half(pitch):
    pitch = pitch.crop((0, 12*28, 15*28, 26*28))
    return pitch

def pitch_select_upper_half(pitch):
    pitch = pitch.crop((0, 0, 15*28, 13*28))
    return pitch

def create_horizontal_plot(replay_id, match_id, positions, receiving_team, refresh = False):

    append_string = "_kickoff_horizontal.png"
    fname = build_filename(replay_id, match_id, append_string)

    if not os.path.exists(fname) or refresh:
        plot = Image.open("resources/nice.jpg")
        plot = plot.resize((26 * 28, 15 * 28))
        plot = add_tacklezones(plot, positions, receiving_team, flip = False, horizontal = True)   
        plot = add_players(plot, positions, receiving_team, flip = False, horizontal = True)
        plot.save(fname,"PNG")
    else:
        plot = Image.open(fname)
    return plot


def create_vertical_plot(replay_id, match_id, positions, receiving_team, refresh = False):

    append_string = "_kickoff_vertical.png"
    fname = build_filename(replay_id, match_id, append_string)

    if not os.path.exists(fname) or refresh:
        plot = Image.open("resources/nice.jpg")
        plot = plot.rotate(angle = 90, expand = True)
        plot = plot.resize((15 * 28, 26 * 28))
        
        if receiving_team == 'teamAway':
            doFlip = True
        else:
            doFlip = False

        plot = add_tacklezones(plot, positions, receiving_team, flip = doFlip)   
        plot = add_players(plot, positions, receiving_team, flip = doFlip)
        plot.save(fname,"PNG")
    else:
        plot = Image.open(fname)
    return plot

def build_filename(replay_id, match_id, append_string, race = None, base_path = 'kickoff_pngs/'):

    if race is not None:
        dirname = race + "/"
        dirname = dirname.lower()
        dirname = dirname.replace(' ', '_')

        if not os.path.exists(base_path + dirname):
            os.makedirs(base_path + dirname)

    image_name = str(replay_id) + "_" + str(match_id) + append_string

    if race is not None:
        fname = base_path + dirname + image_name
    else:
        fname = base_path + image_name

    return fname

def create_defense_plot(replay_id, match_id, positions, receiving_team, text, refresh = False, verbose = False):

    race = positions.iloc[0]['race']
    append_string = "_kickoff_lower_defense.png"
    fname = build_filename(replay_id, match_id, append_string, race)

    if not os.path.exists(fname) or refresh:  
        plot = Image.open("resources/nice.jpg")
        plot = plot.rotate(angle = 90, expand = True)
        plot = plot.resize((15 * 28, 26 * 28))
        
        if receiving_team == 'teamAway':
            doFlip = True
        else:
            doFlip = False

        plot = add_tacklezones(plot, positions.query('home_away != @receiving_team'), receiving_team, flip = doFlip)   
        plot = add_players(plot, positions.query('home_away != @receiving_team'), receiving_team, flip = doFlip)
        plot = pitch_select_lower_half(plot)

        draw = ImageDraw.Draw(plot) 
        font1 = ImageFont.truetype('LiberationMono-Regular.ttf', 22)
        font2 = ImageFont.truetype('LiberationMono-Regular.ttf', 16)

        text_line0 = "receiving team:" + text[6]
        text_line1 = text[0] + "(" + text[2] + ") vs."
        text_line2 = text[1] + "(" + text[3] + ")"
        text_line3 = "match nr. " + str(match_id) + " score:" + str(text[4]) + " - " + str(text[5])

        draw.text((5, 252), text[7], font=font1, fill='black')
        draw.text((5, 280), text_line0, font=font1, fill='black')
        draw.text((5, 307), text_line1, font=font1, fill='black')
        draw.text((5, 335), text_line2, font=font1, fill='black')
        draw.text((5, 366), text_line3, font=font2, fill='black')

        plot.save(fname, "PNG")
        if verbose:
            print("\n")
            print("wrote plot to ", fname)
    else:
        plot = Image.open(fname)
        if verbose:
            print(".", end = '')
            print("read plot from ", fname)
    return plot


def create_offense_plot(replay_id, match_id, positions, receiving_team, refresh = False):

    race = positions.iloc[0]['race']
    append_string = "_kickoff_lower_offense.png"
    fname = build_filename(replay_id, match_id, append_string, race)

    if not os.path.exists(fname) or refresh:  
        plot = Image.open("resources/nice.jpg")
        plot = plot.rotate(angle = 90, expand = True)
        plot = plot.resize((15 * 28, 26 * 28))
        
        if receiving_team == 'teamAway':
            doFlip = False
        else:
            doFlip = True

        plot = add_tacklezones(plot, positions.query('home_away == @receiving_team'), receiving_team, flip = doFlip)   
        plot = add_players(plot, positions.query('home_away == @receiving_team'), receiving_team, flip = doFlip)

        plot = pitch_select_lower_half(plot)
        plot.save(fname,"PNG")
    else:
        print(".", end = '')
        plot = Image.open(fname)
    return plot

def determine_receiving_team_at_start(df):
    gameSetHomeFirstOffense = len(df.query('turnNr == 0 & turnMode == "startGame" & modelChangeId == "gameSetHomeFirstOffense"').index)

    if gameSetHomeFirstOffense == 1:
        receiving_team = 'teamHome'
    else: 
        receiving_team = 'teamAway'
    return receiving_team

def extract_coin_toss(df):
    for i in range(len(df)):
        if isinstance(df.iloc[i].modelChangeValue, dict):
            if 'choosingTeamId' in df.iloc[i].modelChangeValue:
                choosingTeamId = df.iloc[i].modelChangeValue['choosingTeamId']
                # PM compare this to receiving team: this is the choice
                return choosingTeamId
            else:
                pass
        else:
            pass
    return None

def create_plot(match_id, refresh = False, verbose = False, plot_type = 'D'):
    my_match = fetch_match(match_id)
    team1_score = my_match['team1']['score']
    team2_score = my_match['team2']['score']

    replay_id = my_match['replayId']
    my_replay = fetch_replay(replay_id)
    df_players = extract_rosters_from_replay(my_replay)
    
    # board state at kick-off
    df = parse_replay(my_replay)
    positions = df.query('turnNr == 0 & turnMode == "setup" & Half == 1 & \
                         modelChangeId == "fieldModelSetPlayerCoordinate"').groupby('modelChangeKey').tail(1)

    positions = pd.merge(positions, df_players, left_on='modelChangeKey', right_on='playerId', how="left")
    
    # select only players on the board at kick-off, i.e. not in reserve
    positions = positions.query('PlayerCoordinateX != [-1, 30]').copy()

    # expect a setup with 22 players
    if len(positions) != 22:
        print("warning: expected 22 players")

    # determine who is receiving: the home or the away team
    receiving_team = determine_receiving_team_at_start(df)
    
    team_id_defensive = df_players.query('home_away != @receiving_team')['teamId'].unique()[0]
    team_id_offensive = df_players.query('home_away == @receiving_team')['teamId'].unique()[0]
    
    race_defensive = df_players.query('teamId == @team_id_defensive')['race'].unique()[0]
    race_offensive = df_players.query('teamId == @team_id_offensive')['race'].unique()[0]

    choosing_team = extract_coin_toss(df)
    if str(choosing_team) == str(team_id_offensive):
        toss_choice = "toss choice is play offense"
    else:
        toss_choice = "toss choice is play defense"

    coach1 = my_replay['game']['teamHome']['coach']
    coach2 = my_replay['game']['teamAway']['coach']
    
    race1 = my_replay['game']['teamHome']['race']
    race2 = my_replay['game']['teamAway']['race']

    text = [coach1, coach2, race1, race2, team1_score, team2_score, receiving_team, toss_choice] # 1 home # 2 away
    # create the plots
    if plot_type == 'D':
        plot = create_defense_plot(replay_id, match_id, positions, receiving_team, text, refresh, verbose)
    elif plot_type == 'V':
        plot = create_vertical_plot(replay_id, match_id, positions, receiving_team)
    elif plot_type == 'H':
        plot = create_horizontal_plot(replay_id, match_id, positions, receiving_team)
    elif plot_type == 'O':
        plot = create_offense_plot(replay_id, match_id, positions, receiving_team, refresh)
    else:
        plot = print("unknown plot type")
    # replay_id, match_id, team_id_defensive, race_defensive, team_id_offensive, race_offensive
    return plot

def sort_defensive_plots(df_replays):
    """Sort defense setups in folders by race"""
    current_dirname = "kickoff_pngs/"

    for row in range(len(df_replays)):
        dirname = df_replays.iloc[row]['raceDefense'] + "/"
        dirname = dirname.lower()
        dirname = dirname.replace(' ', '_')
        if not os.path.exists(current_dirname + dirname):
            os.makedirs(current_dirname + dirname)
        fname = str(df_replays.iloc[row]['replayId']) + "_" + str(df_replays.iloc[row]['matchId']) + "_kickoff_lower_defense.png"
        os.rename(current_dirname + fname, current_dirname + dirname + fname)