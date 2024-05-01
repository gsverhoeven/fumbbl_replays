import pandas as pd

from .fetch_replay import fetch_replay
from .parse_replay import parse_replay
from .add_header import add_header
from .structure_player_actions import structure_player_actions
from .from_steps_to_trajectories import from_steps_to_trajectories
from .extract_rosters_from_replay import extract_rosters_from_replay
from .condense_setup_formations import condense_setup_formations
from .replace_player_ids_with_shorthand import replace_player_ids_with_shorthand
from .write_to_excel import write_to_excel

def fumbbl2bbgn(replay_id):
    # load replay
    my_replay = fetch_replay(replay_id, dirname = "example_input/")
    
    ignoreList = pd.read_csv("resources/IgnoreModelChange.csv")
    # initial parse
    df = parse_replay(my_replay, ignoreList) 
    
    df = add_header(df, my_replay)

    # add state descriptions
    cl_state = pd.read_csv("resources/PlayerState.csv")
    df = pd.merge(left = df, right = cl_state, left_on = "SetPlayerState", right_on = "INT", how = "left", sort = False)
    df = df.drop(['DESCRIPTION'], axis = 1)

    # add location descriptions
    cl_location = pd.read_csv("resources/Coordinate.csv")
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
    
    # replace player IDs with shorthands
    df = replace_player_ids_with_shorthand(df, df_roster)

    write_to_excel(df, df_roster) 
    #write_to_excel(df, df_roster = pd.DataFrame([])) 

    return df