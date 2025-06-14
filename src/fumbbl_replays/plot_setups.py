import os
import pandas as pd

from .fetch_replay import fetch_replay
from .fetch_match import fetch_match
from .parse_replay import parse_replay, extract_receiving_team_at_start, extract_coin_toss, extract_receive_choice
from .extract_rosters_from_replay import extract_rosters_from_replay
from .plot import add_tacklezones, add_players, add_skill_bands, pitch_select_lower_half

import importlib.resources as resources
from fumbbl_replays import __name__ as pkg_name

from PIL import Image, ImageDraw, ImageFont

def fetch_data(match_id):
    pd.options.mode.chained_assignment = None
    my_match = fetch_match(match_id)
    team1_score = my_match['team1']['score']
    team2_score = my_match['team2']['score']

    replay_id = my_match['replayId']
    my_replay = fetch_replay(match_id)

    coachHome = my_replay['game']['teamHome']['coach']
    coachAway = my_replay['game']['teamAway']['coach']
    
    raceHome = my_replay['game']['teamHome']['race']
    raceAway = my_replay['game']['teamAway']['race']

    df_players = extract_rosters_from_replay(my_replay)
    
    # board state at kick-off
    pd_replay = parse_replay(my_replay)
    positions = pd_replay.query('turnNr == 0 & turnMode == "setup" & Half == 1 & \
                         modelChangeId == "fieldModelSetPlayerCoordinate"').groupby('modelChangeKey').tail(1)

    positions = pd.merge(positions, df_players, left_on='modelChangeKey', right_on='playerId', how="left")
    
    # select only players on the board at kick-off, i.e. not in reserve
    positions = positions.query('PlayerCoordinateX != [-1, 30]').copy()
    # add required columns
    positions['CoordinateX'] = positions['PlayerCoordinateX'] + 1
    positions['PlayerState'] = 'Standing'
    positions['PlayerNr'] = positions['modelChangeKey']
    # expect a setup with 22 players
    if len(positions) != 22:
        print("warning: expected 22 players")
    
    # determine who is receiving: the home or the away team
    receiving_team = extract_receiving_team_at_start(pd_replay)

    if receiving_team == "teamHome":
        raceOffense = raceHome
        raceDefense = raceAway
    else:
        raceOffense = raceAway
        raceDefense = raceHome
    
    team_id_offensive = df_players.query('home_away == @receiving_team')['teamId'].unique()[0]

    choosing_team = extract_coin_toss(pd_replay)
    receive_choice = extract_receive_choice(pd_replay)

    text = [coachHome, coachAway, raceHome, raceAway, \
        raceDefense, raceOffense, team1_score, team2_score, \
            receiving_team, receive_choice, choosing_team] # 1 home # 2 away
    return match_id, replay_id, positions, receiving_team, text

def build_filename(replay_id, match_id, append_string, race = None, base_path = 'kickoff_pngs/'):
    # PM use get cache_dir
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
    positions = positions.query('home_away != @receiving_team')
    race = positions.iloc[0]['race']
    append_string = "_kickoff_lower_defense.png"
    fname = build_filename(replay_id, match_id, append_string, race)

    if not os.path.exists(fname) or refresh:
        file_path = resources.files(pkg_name) / "resources" / "nice.jpg"
        plot = Image.open(file_path)
        plot = plot.rotate(angle = 90, expand = True)
        plot = plot.resize((15 * 28, 26 * 28))
        
        if receiving_team == 'teamAway':
            doFlip = True
        else:
            doFlip = False

        plot = add_tacklezones(plot, positions, receiving_team, flip = doFlip)   
        plot = add_players(plot, positions, receiving_team, flip = doFlip)
        plot = add_skill_bands(plot, positions, flip = doFlip, horizontal = False)
        plot = pitch_select_lower_half(plot)
        plot = add_text(plot, text, match_id)

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


def create_offense_plot(replay_id, match_id, positions, receiving_team, text, refresh = False, verbose = False):
    positions = positions.query('home_away == @receiving_team')
    race = positions.iloc[0]['race']
    append_string = "_kickoff_lower_offense.png"
    fname = build_filename(replay_id, match_id, append_string, race)

    if not os.path.exists(fname) or refresh:
        file_path = resources.files(pkg_name) / "resources" / "nice.jpg"
        plot = Image.open(file_path)
        plot = plot.rotate(angle = 90, expand = True)
        plot = plot.resize((15 * 28, 26 * 28))
        
        # only part where offense plot differs from defense plot?
        if receiving_team == 'teamAway':
            doFlip = False
        else:
            doFlip = True

        plot = add_tacklezones(plot, positions, receiving_team, flip = doFlip)   
        plot = add_players(plot, positions, receiving_team, flip = doFlip)
        plot = add_skill_bands(plot, positions, flip = doFlip, horizontal = False)        
        plot = pitch_select_lower_half(plot)
        plot = add_text(plot, text, match_id)

        plot.save(fname,"PNG")
    else:
        if verbose:
            print(".", end = '')
        plot = Image.open(fname)
    return plot

def add_text(plot, text, match_id):
    draw = ImageDraw.Draw(plot) 
    font1 = ImageFont.truetype('LiberationMono-Regular.ttf', 22)
    font2 = ImageFont.truetype('LiberationMono-Regular.ttf', 16)

    if(len(text)) == 11: # move to pytest
        if text[8] == "teamHome":
            text_line0 = "receiving coach:" + text[0]
        elif text[8] == "teamAway":
            text_line0 = "receiving coach:" + text[1]
        else:
            text_line0 = " error"
        text_line1 = text[0] + "(" + text[2] + ") vs."
        text_line2 = text[1] + "(" + text[3] + ")"
        text_line3 = "match nr. " + str(match_id) + " score:" + str(text[6]) + " - " + str(text[7])

        draw.text((5, 252), text[9], font=font1, fill='black')
        draw.text((5, 280), text_line0, font=font1, fill='black')
        draw.text((5, 307), text_line1, font=font1, fill='black')
        draw.text((5, 335), text_line2, font=font1, fill='black')
        draw.text((5, 366), text_line3, font=font2, fill='black')
    elif (len(text)) == 0: 
        return plot
    else:
        print("metadata unexpected length")
        return plot

    return plot