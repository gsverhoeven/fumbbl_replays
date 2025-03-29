import pandas as pd
from .fetch_match import fetch_team_matches
from .fetch_replay import fetch_replay
from .extract_rosters_from_replay import extract_rosters_from_replay
from .fetch_roster import fetch_roster
from plotnine import *

def fetch_team_development_data(team_id, n_matches = 15):
    team_id = str(team_id)
    team_matches = fetch_team_matches(int(team_id))

    matches = []
    for i in range(len(team_matches)):
        matches.append(team_matches[i]['id'])

    matches.sort()

    # fetch rosters from replays
    i = 0

    for match_id in matches[0:n_matches]:
        print(".", end = '')
        my_replay = fetch_replay(match_id)
        df_positions = extract_rosters_from_replay(my_replay) 
        df_positions = (df_positions
                        .query("teamId == @team_id")
                        .filter(['short_name', 'rosterName' , 'positionName', 'playerName', 'skillArrayRoster', 'learned_skills', 'skill_colors', 'cost', 'recoveringInjury'])
                        .reset_index()
                        )
        df_positions['match_count'] = i+1
        if i == 0:
            res = df_positions
        else:
            res = pd.concat([res, df_positions])
        i = i + 1

    first_skill = []
    second_skill = []
    first_skill_color = []
    second_skill_color = []

    for i in range(len(res)):
        n_skills = len(res.iloc[i]['learned_skills'])
        if n_skills == 0:
            first_skill.append("-")
            second_skill.append("-")
            first_skill_color.append("grey")
            second_skill_color.append("NA")            
        elif n_skills == 1:
            first_skill.append(res.iloc[i]['learned_skills'][n_skills - 1])
            second_skill.append("-")
            first_skill_color.append(res.iloc[i]['skill_colors'][n_skills - 1])
            second_skill_color.append("NA")          
        elif n_skills == 2:
            first_skill.append(res.iloc[i]['learned_skills'][n_skills - 2])
            second_skill.append(res.iloc[i]['learned_skills'][n_skills - 1])
            first_skill_color.append(res.iloc[i]['skill_colors'][n_skills - 2])
            second_skill_color.append(res.iloc[i]['skill_colors'][n_skills - 1])            
        else:
            first_skill.append(">2")
            second_skill.append(">2")
            first_skill_color.append("black")
            second_skill_color.append("black")            

    res['first_skill'] = first_skill
    res['second_skill'] = second_skill
    res['first_skill_color'] = first_skill_color
    res['second_skill_color'] = second_skill_color
    res = res.drop(columns = ['short_name'])

    res = res.query('first_skill != "Loner" & recoveringInjury == "None" ')

    rosterName = res['rosterName'].unique()[0]
    roster = fetch_roster(rosterName).filter(['positionName', 'shorthand'])

    player_list = (res
        .groupby(['playerName', 'positionName', 'cost'], as_index = False)
        .agg(count = ('index', 'count'), first_match = ('match_count', 'min'))
        .merge(roster, on = 'positionName')
        .sort_values(['positionName', 'first_match'])
    )

    player_list['positionNr'] = player_list.groupby(['positionName']).cumcount() + 1
    # create shorthand id
    player_list['short_name'] = player_list['shorthand'] + player_list['positionNr'].astype(str)
    
    player_list = player_list.sort_values(['cost', 'first_match'])
    player_list['plotPosition'] = range(1, len(player_list) + 1)

    res = res.merge(player_list.filter(['playerName', 'shorthand', 'short_name', 'positionNr', 'plotPosition']), on = 'playerName')
    return res

def make_team_development_plot(res):
    rosterName = res['rosterName'].unique()[0]
    p = (
        ggplot(res)
        + geom_tile(aes(x="match_count", y="plotPosition", fill = "first_skill_color"), width=0.95, height=0.95)
        + geom_tile(data = res.query('second_skill_color != "NA"'), mapping = aes(x="match_count+0.5", y="plotPosition-0.5", fill = "second_skill_color"), width=0.95, height=0.95)
        + geom_text(aes(x="match_count", y="plotPosition", label="first_skill"), size=6)
        + geom_text(data = res.query('second_skill_color != "NA"'), mapping = aes(x="match_count+0.5", y="plotPosition-0.5", label="second_skill"), size = 6)
        + scale_fill_identity(na_value = "NA")
        #+ coord_equal(expand=False)  # new
        + theme(figure_size=(12, 6))  # new
        + theme(legend_position='none')
        + labs(x="League game number", y="Players", title= rosterName + " team development BBT")
    )
    p.draw(show = True)