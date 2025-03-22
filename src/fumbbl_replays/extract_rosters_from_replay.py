import pandas as pd
import importlib.resources as resources
from fumbbl_replays import __name__ as pkg_name

from .extract_players_from_replay import extract_players_from_replay

def extract_rosters_from_replay(my_replay, cl_file_location = None):
    if cl_file_location == None:
        file_path = resources.files(pkg_name) / "resources" / "230218 bb_skill_colors.csv"
    else:
        file_path = cl_file_location

    json_roster_home = my_replay['game']['teamHome']['roster']
    df_positions_home = json2pd_replay_roster(json_roster_home)
    df_positions_home['rosterName'] = json_roster_home['rosterName']

    json_roster_away = my_replay['game']['teamAway']['roster']
    df_positions_away = json2pd_replay_roster(json_roster_away)
    df_positions_away['rosterName'] = json_roster_away['rosterName']

    df_positions = pd.concat([df_positions_home, df_positions_away])

    df_positions.drop_duplicates(inplace = True, ignore_index = True)

    df_players = extract_players_from_replay(my_replay)

    df_roster = pd.merge(df_players, df_positions, on="positionId", how="left")
      
    df_roster['positionNr'] = df_roster.groupby(['home_away','positionName']).cumcount() + 1
    # create shorthand id
    df_roster['short_name'] = df_roster['shorthand'] + df_roster['positionNr'].astype(str)

    df_roster = add_learned_skill_col(df_roster)
    df_roster = add_skill_colors_col(df_roster, file_path)

    return df_roster

def json2pd_replay_roster(json_roster):
    positionId = []
    positionName = []
    shorthand = []
    icon_path = []
    cost = []
    skillArrayRoster = []

    for positionIndex in range(len(json_roster['positionArray'])):
        tmpPosition = json_roster['positionArray'][positionIndex]
        positionId.append(tmpPosition['positionId'])
        positionName.append(tmpPosition['positionName'])
        shorthand.append(tmpPosition['shorthand'])
        icon_path.append(json_roster['baseIconPath'] + tmpPosition['urlIconSet'])
        cost.append(tmpPosition['cost'])
        if "skillArray" in tmpPosition.keys():
            skillArrayRoster.append(str(tmpPosition['skillArray']))
        else:
            skillArrayRoster.append(str(['None']))
            

    df_positions = pd.DataFrame( {"positionId": positionId,
                        "positionName": positionName,
                        "shorthand": shorthand,
                        "icon_path": icon_path,
                        "cost": cost,
                        "skillArrayRoster": skillArrayRoster})
    return df_positions

def add_learned_skill_col(df_roster):
    df_roster = df_roster.copy()
    learned_skill_col = []
    base_skill_col = []
    for r in range(len(df_roster)):
        learned_skills = []
        base_skills = []
        skill_list = df_roster.iloc[r]['skillArray']
        base_skill_List = df_roster.iloc[r]['skillArrayRoster']
        for s in skill_list:
            if s not in base_skill_List:
                learned_skills.append(s)
            else:
                base_skills.append(s)
        learned_skill_col.append(learned_skills)
        base_skill_col.append(base_skills)
    df_roster['learned_skills'] = learned_skill_col
    df_roster['skillArrayRoster'] = base_skill_col
    return df_roster

def add_skill_colors_col(obj, cl_file_location):
    cl_skill = get_skill_list(cl_file_location)
    skill_colors = []
    for r in range(len(obj)):
        color_list = []
        skill_array = obj.iloc[r]['learned_skills']
        for skill in skill_array:
            if skill in cl_skill['skill_name'].values:
                i = cl_skill.query('skill_name == @skill').index[0]
                color_list.append(cl_skill.loc[i, 'Pcolor'])
            else:
                color_list.append('none')
        skill_colors.append(color_list)
    obj['skill_colors'] = skill_colors
    return obj

def get_skill_list(file_location):
    skill_list = pd.read_csv(file_location, sep = ';', dtype='str', keep_default_na=False)
    skill_list['n'] = skill_list['n'].astype(int)
    skill_list = skill_list.sort_values("n", ascending = False)
    return skill_list

def add_skill_to_player(positions, short_name, skill_name, cl_file_location = None):
    if cl_file_location == None:
        file_path = resources.files(pkg_name) / "resources" / "230218 bb_skill_colors.csv"
    else:
        file_path = cl_file_location

    if short_name in positions['short_name'].values:
        cl_skill = get_skill_list(file_path)
        i = positions.query('short_name == @short_name').index[0]
        skill_list = positions.loc[i, 'learned_skills']
        skillArrayRoster = positions.loc[i, 'skillArrayRoster']
        color_list = positions.loc[i, 'skill_colors']
        if skill_name not in skill_list + skillArrayRoster:
            skill_list.append(skill_name)
            if skill_name in cl_skill['skill_name'].values:
                    i = cl_skill.query('skill_name == @skill_name').index[0]
                    color_list.append(cl_skill.loc[i, 'Pcolor'])
        else:
            print("Skill already present")
    else:
        print("Player not found")
    return

def remove_skill_from_player(positions, short_name, skill_name):
    if short_name in positions['short_name'].values:
        i = positions.query('short_name == @short_name').index[0]
        skill_list = positions.loc[i, 'learned_skills']
        skillArrayRoster = positions.loc[i, 'skillArrayRoster']
        color_list = positions.loc[i, 'skill_colors']

        if skill_name in skill_list:
            i = skill_list.index(skill_name)
            skill_list.pop(i)
            color_list.pop(i)
        else:
            print("Skill not present")
    else:
        print("Player not found")
    return