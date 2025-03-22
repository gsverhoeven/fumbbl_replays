import pandas as pd
from .fetch_match import fetch_team_matches
from .fetch_replay import fetch_replay
from .extract_rosters_from_replay import extract_rosters_from_replay
from .fetch_roster import fetch_roster
from plotnine import *

def fetch_team_development_data(team_id, n_matches = 15):
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

    cell_color = []
    learned_skill = []

    for i in range(len(res)):
        n_skills = len(res.iloc[i]['learned_skills'])
        if n_skills == 0:
            cell_color.append("grey")
            learned_skill.append("-")
        elif n_skills == 1:
            cell_color.append(res.iloc[i]['skill_colors'][n_skills - 1])
            learned_skill.append(res.iloc[i]['learned_skills'][n_skills - 1])
        else:
            cell_color.append("black")
            learned_skill.append(">1")        

    res['cell_color'] = cell_color
    res['learned_skill'] = learned_skill
    res = res.drop(columns = ['short_name'])

    res = res.query('learned_skill != "Loner" & recoveringInjury == "None" ')

    rosterName = res['rosterName'].unique()[0]
    roster = fetch_roster(rosterName).filter(['positionName', 'shorthand'])

    player_list = (res
        .groupby(['playerName', 'positionName'], as_index = False)
        .agg(count = ('index', 'count'), first_match = ('match_count', 'min'))
        .merge(roster, on = 'positionName')
        .sort_values(['positionName', 'first_match'])
    )

    player_list['positionNr'] = player_list.groupby(['positionName']).cumcount() + 1
    # create shorthand id
    player_list['short_name'] = player_list['shorthand'] + player_list['positionNr'].astype(str)

    res = res.merge(player_list.filter(['playerName', 'shorthand', 'short_name', 'positionNr']), on = 'playerName')
    return res

def make_team_development_plot(res):      
    (
        ggplot(res, aes(x="factor(match_count)", y="reorder(short_name, cost)"))
        + geom_tile(aes(fill = "cell_color", width=0.95, height=0.95))
        + geom_text(aes(label="learned_skill"), size=6)
        + scale_fill_identity()
        #+ coord_equal(expand=False)  # new
        + theme(figure_size=(12, 6))  # new
        + theme(legend_position='none')
        + labs(x="League game number", y="Players", title= rosterName + " team development BBT")
    )