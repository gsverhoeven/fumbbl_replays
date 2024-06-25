import pandas as pd
from .extract_players_from_replay import extract_players_from_replay

def extract_rosters_from_replay(my_replay):

    json_roster_home = my_replay['game']['teamHome']['roster']
    df_positions_home = json2pd_replay_roster(json_roster_home)

    json_roster_away = my_replay['game']['teamAway']['roster']
    df_positions_away = json2pd_replay_roster(json_roster_away)

    df_positions = pd.concat([df_positions_home, df_positions_away])

    df_positions.drop_duplicates(inplace = True, ignore_index = True)

    df_players = extract_players_from_replay(my_replay)

    df_roster = pd.merge(df_players, df_positions, on="positionId", how="left")
      
    df_roster['positionNr'] = df_roster.groupby(['home_away','positionName']).cumcount() + 1
    # create shorthand id
    df_roster['short_name'] = df_roster['shorthand'] + df_roster['positionNr'].astype(str)

    df_roster = add_learned_skill_col(df_roster)

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
