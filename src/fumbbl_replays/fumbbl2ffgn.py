import pandas as pd
import os
import importlib.resources as resources
from fumbbl_replays import __name__ as pkg_name

from .fetch_match import fetch_match
from .fetch_replay import fetch_replay
from .parse_replay import parse_replay, write_to_excel
from .add_header import add_header
from .structure_player_actions import structure_player_actions
from .from_steps_to_trajectories import from_steps_to_trajectories
from .extract_rosters_from_replay import extract_rosters_from_replay
from .condense_setup_formations import condense_setup_formations
from .replace_player_ids_with_shorthand import replace_player_ids_with_shorthand

def fumbbl2ffgn(match_id, verbose = False):
    pd.options.mode.chained_assignment = None 
    # load replay
    raw_replay = fetch_replay(match_id, dirname = "raw/replay_files/", verbose = verbose)
    
    file_path = resources.files(pkg_name) / "resources" / "IgnoreModelChange.csv"
    ignoreList = pd.read_csv(file_path)
    # initial parse to pandas replay
    pd_replay = parse_replay(raw_replay, ignoreList) 
    
    pd_replay = add_header(pd_replay, raw_replay)

    # add state descriptions
    file_path = resources.files(pkg_name) / "resources" / "PlayerState.csv"
    cl_state = pd.read_csv(file_path)
    pd_replay = pd.merge(left = pd_replay, right = cl_state, left_on = "SetPlayerState", right_on = "INT", how = "left", sort = False)
    pd_replay = pd_replay.drop(['DESCRIPTION'], axis = 1)

    # add location descriptions
    file_path = resources.files(pkg_name) / "resources" / "Coordinate.csv"
    cl_location = pd.read_csv(file_path)
    pd_replay = pd.merge(left = pd_replay, right = cl_location, left_on = "PlayerCoordinateX", right_on = "VALUE", how = "left", sort = False)

    pd_replay = pd_replay.drop_duplicates(subset=pd_replay.columns.difference(['modelChangeValue']))

    pd_replay = structure_player_actions(pd_replay)
    
    pd_replay = from_steps_to_trajectories(pd_replay)

    # drop more rows that are by now no longer needed (either reportList or modelChangeId)
    pd_replay = pd_replay.query('~(modelChangeId in ["turnDataSetTurnNr", \
                  "turnDataSetFirstTurnAfterKickoff", \
                  "fumbblResultUpload"])')
    
    # extract rosters from raw replay
    df_roster = extract_rosters_from_replay(raw_replay)    

    pd_replay = condense_setup_formations(pd_replay, df_roster)
    
    # replace player IDs with shorthands, parse reportList messages
    pd_replay = replace_player_ids_with_shorthand(pd_replay, df_roster)

    write_to_excel(pd_replay, df_roster) 

    return pd_replay