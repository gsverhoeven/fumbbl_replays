import pandas as pd
import os
import importlib.resources as resources
from fumbbl_replays import __name__ as pkg_name

from .fetch_match import fetch_match
from .fetch_replay import fetch_replay
from .parse_replay import parse_replay
from .add_header import add_header
from .structure_player_actions import structure_player_actions
from .from_steps_to_trajectories import from_steps_to_trajectories
from .extract_rosters_from_replay import extract_rosters_from_replay
from .condense_setup_formations import condense_setup_formations
from .replace_player_ids_with_shorthand import replace_player_ids_with_shorthand
from .write_to_excel import write_to_excel

def fumbbl2ffgn(match_id, verbose = False):
    pd.options.mode.chained_assignment = None 
    # load replay
    my_replay = fetch_replay(match_id, dirname = "raw/replay_files/", verbose = verbose)
    
    file_path = resources.files(pkg_name) / "resources" / "IgnoreModelChange.csv"
    ignoreList = pd.read_csv(file_path)
    # initial parse
    df = parse_replay(my_replay, ignoreList) 
    
    df = add_header(df, my_replay)

    # add state descriptions
    file_path = resources.files(pkg_name) / "resources" / "PlayerState.csv"
    cl_state = pd.read_csv(file_path)
    df = pd.merge(left = df, right = cl_state, left_on = "SetPlayerState", right_on = "INT", how = "left", sort = False)
    df = df.drop(['DESCRIPTION'], axis = 1)

    # add location descriptions
    file_path = resources.files(pkg_name) / "resources" / "Coordinate.csv"
    cl_location = pd.read_csv(file_path)
    df = pd.merge(left = df, right = cl_location, left_on = "PlayerCoordinateX", right_on = "VALUE", how = "left", sort = False)

    df = df.drop_duplicates(subset=df.columns.difference(['modelChangeValue']))

    df = structure_player_actions(df)
    
    df = from_steps_to_trajectories(df)

    # drop more rows that are by now no longer needed (either reportList or modelChangeId)
    df = df.query('~(modelChangeId in ["turnDataSetTurnNr", \
                  "turnDataSetFirstTurnAfterKickoff", \
                  "fumbblResultUpload"])')
    
    # extract rosters
    df_roster = extract_rosters_from_replay(my_replay)    

    df = condense_setup_formations(df, df_roster)
    
    # replace player IDs with shorthands, parse reportList messages
    df = replace_player_ids_with_shorthand(df, df_roster)

    write_to_excel(df, df_roster) 
    #write_to_excel(df, df_roster = pd.DataFrame([])) 

    return df