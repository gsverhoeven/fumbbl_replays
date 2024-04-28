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

def create_horizontal_plot(replay_id, match_id, positions, receiving_team):
    image_path = 'kickoff_pngs/'
    image_name = str(replay_id) + "_" + str(match_id) + "_kickoff_horizontal.png"
    fname = image_path + image_name

    if not os.path.exists(fname):
        # make plot
        pitch = Image.open("resources/nice.jpg")
        pitch = pitch.resize((26 * 28, 15 * 28))
        pitch = add_tacklezones(pitch, positions, receiving_team, flip = False, horizontal = True)   
        pitch = add_players(pitch, positions, receiving_team, flip = False, horizontal = True)
        pitch.save(fname,"PNG")



def create_vertical_plot(replay_id, match_id, positions, receiving_team):
    image_path = 'kickoff_pngs/'
    image_name = str(replay_id) + "_" + str(match_id) + "_kickoff_vertical.png"
    fname = image_path + image_name

    if not os.path.exists(fname):
        pitch = Image.open("resources/nice.jpg")
        pitch = pitch.rotate(angle = 90, expand = True)
        pitch = pitch.resize((15 * 28, 26 * 28))
        
        if receiving_team == 'teamAway':
            doFlip = True
        else:
            doFlip = False

        pitch = add_tacklezones(pitch, positions, receiving_team, flip = doFlip)   
        pitch = add_players(pitch, positions, receiving_team, flip = doFlip)
        pitch.save(image_path + image_name,"PNG")

def create_defense_plot(replay_id, match_id, positions, receiving_team, text, refresh):
    base_path = 'kickoff_pngs/'

    dirname = positions.iloc[0]['race'] + "/"
    dirname = dirname.lower()
    dirname = dirname.replace(' ', '_')

    if not os.path.exists(base_path + dirname):
        os.makedirs(base_path + dirname)

    image_name = str(replay_id) + "_" + str(match_id) + "_kickoff_lower_defense.png"
    fname = base_path + dirname + image_name

    if not os.path.exists(fname) or refresh:  
        pitch = Image.open("resources/nice.jpg")
        pitch = pitch.rotate(angle = 90, expand = True)
        pitch = pitch.resize((15 * 28, 26 * 28))
        
        if receiving_team == 'teamAway':
            doFlip = True
        else:
            doFlip = False

        pitch = add_tacklezones(pitch, positions.query('home_away != @receiving_team'), receiving_team, flip = doFlip)   
        pitch = add_players(pitch, positions.query('home_away != @receiving_team'), receiving_team, flip = doFlip)
        pitch = pitch_select_lower_half(pitch)

        draw = ImageDraw.Draw(pitch) 
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

        pitch.save(base_path + dirname + image_name,"PNG")
    else:
        print(".", end = '')


def create_offense_plot(replay_id, match_id, positions, receiving_team):
    image_path = 'kickoff_pngs/'
    image_name = str(replay_id) + "_" + str(match_id) + "_kickoff_lower_offense.png"
    fname = image_path + image_name

    if not os.path.exists(fname):  
        pitch = Image.open("resources/nice.jpg")
        pitch = pitch.rotate(angle = 90, expand = True)
        pitch = pitch.resize((15 * 28, 26 * 28))
        
        if receiving_team == 'teamAway':
            doFlip = False
        else:
            doFlip = True

        pitch = add_tacklezones(pitch, positions.query('home_away == @receiving_team'), receiving_team, flip = doFlip)   
        pitch = add_players(pitch, positions.query('home_away == @receiving_team'), receiving_team, flip = doFlip)

        pitch = pitch_select_lower_half(pitch)
        pitch.save(image_path + image_name,"PNG")
    else:
        print(".", end = '')

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

def process_replay(replay_id, df_matches, refresh = False):
    my_replay = fetch_replay(replay_id)
    match_id = df_matches.query("replay_id == @replay_id")['match_id'].values[0]

    df_players = extract_players_from_replay(my_replay)
    df_positions = extract_rosters_from_replay(my_replay)
    # roster
    df_players2 = pd.merge(df_players, df_positions, on="positionId", how="left")

    df = parse_replay_file(my_replay)

    # board state at kick-off
    positions = df.query('turnNr == 0 & turnMode == "setup" & Half == 1 & \
                         modelChangeId == "fieldModelSetPlayerCoordinate"').groupby('modelChangeKey').tail(1)

    positions = pd.merge(positions, df_players2, left_on='modelChangeKey', right_on='playerId', how="left")
    # check if we have 22 players
    # len(positions.query('PlayerCoordinateX != [-1, 30]'))

    # select only players on the board at kick-off, i.e. not in reserve
    positions = positions.query('PlayerCoordinateX != [-1, 30]').copy()

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

    team1_score = df_matches.query("replay_id == @replay_id")['team1_score'].values[0]
    team2_score = df_matches.query("replay_id == @replay_id")['team2_score'].values[0]

    coach1 = my_replay['game']['teamHome']['coach']
    coach2 = my_replay['game']['teamAway']['coach']
    
    race1 = my_replay['game']['teamHome']['race']
    race2 = my_replay['game']['teamAway']['race']

    text = [coach1, coach2, race1, race2, team1_score, team2_score, receiving_team, toss_choice] # 1 home # 2 away
    # create the plots
    create_defense_plot(replay_id, match_id, positions, receiving_team, text, refresh)

    #create_offense_plot(replay_id, match_id, positions, receiving_team, refresh)

    #create_vertical_plot(replay_id, match_id, positions, receiving_team)

    #create_horizontal_plot(replay_id, match_id, positions, receiving_team)
    return replay_id, match_id, team_id_defensive, race_defensive, team_id_offensive, race_offensive

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