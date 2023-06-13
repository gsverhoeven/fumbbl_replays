def fetch_replay(replay_id):

    #print('fetching replay data for replay_id ' + str(replay_id) + ' as JSON')

    dirname = "raw/replay_files/" 
    fname_string_gz = dirname + str(replay_id) + ".gz"        

    # check if file already exists, else scrape it
    try:
        f = open(fname_string_gz, mode = "rb")
    except OSError as e:
        # scrape it 
        api_string = "https://fumbbl.com/api/replay/get/" + str(replay_id) + "/gz" 

        replay = requests.get(api_string, stream = True)
        print("x",  end = '')
        with open(fname_string_gz, 'wb') as f:
            for chunk in replay.iter_content(None):
                f.write(chunk)
        time.sleep(0.3)
        with gzip.open(fname_string_gz, mode = "rb") as f:
            replay = json.load(f)
            
    else:
        # file already present
        print("o",  end = '')
        with gzip.open(fname_string_gz, mode = "rb") as f:
            replay = json.load(f)

    return replay

def parse_replay_file(my_replay, to_excel = False):
    modelChangeId = []
    modelChangeKey = []
    modelChangeValue = []
    SetPlayerCoordinate = []
    PlayerCoordinateX = []
    PlayerCoordinateY = []
    commandNr = []
    turnNr = []
    TurnCounter = 0
    turnMode = []
    Half = []

    my_gamelog = my_replay['gameLog']

    ignoreList = ['fieldModelAddPlayerMarker', 
                'fieldModelRemoveSkillEnhancements',
                'fieldModelAddDiceDecoration',
                'fieldModelRemoveDiceDecoration',
                'fieldModelAddPushbackSquare',
                'fieldModelRemovePushbackSquare',
                'playerResultSetTurnsPlayed', # we can ignore all playerResult* these are all in game statistic counters
                'playerResultSetBlocks',
                'actingPlayerSetStrength',
                'gameSetConcessionPossible'
                ]
    # N.b. We miss the kick-off event result, this is part of the `reportList` list element.

    for commandIndex in range(len(my_gamelog['commandArray'])):
        tmpCommand = my_gamelog['commandArray'][commandIndex]
        if tmpCommand['netCommandId'] == "serverModelSync":
            for modelChangeIndex in range(len(tmpCommand['modelChangeList']['modelChangeArray'])):
                tmpChange = tmpCommand['modelChangeList']['modelChangeArray'][modelChangeIndex]
                if str(tmpChange['modelChangeId']) not in ignoreList:
                    if str(tmpChange['modelChangeId']) == 'gameSetHalf':
                        Half.append(tmpChange['modelChangeValue'])
                    else:
                        if len(Half) == 0:
                            Half.append(0)
                        else:
                            Half.append(Half[-1])
                                           
                    if str(tmpChange['modelChangeId']) == 'gameSetTurnMode':
                        turnMode.append(tmpChange['modelChangeValue'])
                    else:
                        if len(turnMode) == 0:
                            turnMode.append('startGame')
                        else:
                            turnMode.append(turnMode[-1])

                    if str(tmpChange['modelChangeId']) == 'turnDataSetTurnNr':
                        TurnCounter = tmpChange['modelChangeValue']
                    turnNr.append(TurnCounter)
                    commandNr.append(tmpCommand['commandNr'])
                    modelChangeId.append(tmpChange['modelChangeId'])
                    modelChangeKey.append(tmpChange['modelChangeKey'])
                    modelChangeValue.append(tmpChange['modelChangeValue'])
                    if str(tmpChange['modelChangeId']) == "fieldModelSetPlayerCoordinate":
                        SetPlayerCoordinate.append(1)
                        PlayerCoordinateX.append(tmpChange['modelChangeValue'][0])
                        PlayerCoordinateY.append(tmpChange['modelChangeValue'][1])
                    else:
                        SetPlayerCoordinate.append(0)
                        PlayerCoordinateX.append(99)
                        PlayerCoordinateY.append(99)
        elif tmpCommand['netCommandId'] == "serverAddPlayer":
            pass
        else:
            # unknown netCommand: print it
            print(tmpCommand['netCommandId'])

    df = pd.DataFrame( {"commandNr": commandNr, 
                        "Half": Half,
                        "turnNr": turnNr,
                        "turnMode": turnMode,
                        "modelChangeId": modelChangeId,
                        "modelChangeKey": modelChangeKey,
                        "modelChangeValue": modelChangeValue,
                        "SetPlayerCoordinate": SetPlayerCoordinate,
                        "PlayerCoordinateX": PlayerCoordinateX,
                        "PlayerCoordinateY": PlayerCoordinateY})
    if to_excel:
        df.to_excel("output.xlsx")  
       
    return df

def extract_players_from_replay(my_replay):
    playerId = []
    playerNr = []
    positionId = []
    playerName = []
    playerType = []
    skillArray = []
    home_away = []
    teamId = []
    race = []

    tmpPlayers = my_replay['game']['teamAway']['playerArray']
    tmp_team_id = my_replay['game']['teamAway']['teamId']
    tmp_race = my_replay['game']['teamAway']['race']

    for playerIndex in range(len(tmpPlayers)):
        playerId.append(tmpPlayers[playerIndex]['playerId'])
        playerNr.append(tmpPlayers[playerIndex]['playerNr'])
        positionId.append(tmpPlayers[playerIndex]['positionId'])
        playerName.append(tmpPlayers[playerIndex]['playerName'])
        playerType.append(tmpPlayers[playerIndex]['playerType'])
        skillArray.append(tmpPlayers[playerIndex]['skillArray'])
        home_away.append('teamAway')
        teamId.append(tmp_team_id)
        race.append(tmp_race)

    tmpPlayers = my_replay['game']['teamHome']['playerArray']
    tmp_team_id = my_replay['game']['teamHome']['teamId']
    tmp_race = my_replay['game']['teamHome']['race']

    for playerIndex in range(len(tmpPlayers)):
        playerId.append(tmpPlayers[playerIndex]['playerId'])
        playerNr.append(tmpPlayers[playerIndex]['playerNr'])
        positionId.append(tmpPlayers[playerIndex]['positionId'])
        playerName.append(tmpPlayers[playerIndex]['playerName'])
        playerType.append(tmpPlayers[playerIndex]['playerType'])
        skillArray.append(tmpPlayers[playerIndex]['skillArray'])
        home_away.append('teamHome')
        teamId.append(tmp_team_id)
        race.append(tmp_race)

    df_players = pd.DataFrame( {"teamId": teamId,
                        "playerId": playerId, 
                        "playerNr": playerNr,
                        "positionId": positionId,
                        "playerName": playerName,
                        "playerType": playerType,
                        "skillArray": skillArray,
                        "home_away": home_away,
                        "race": race})
    
    return df_players

def extract_rosters_from_replay(my_replay):
    positionId = []
    positionName = []
    icon_path = []

    tmpRosters = my_replay['game']['teamAway']['roster']

    for positionIndex in range(len(tmpRosters['positionArray'])):
        tmpPosition = tmpRosters['positionArray'][positionIndex]
        positionId.append(tmpPosition['positionId'])
        positionName.append(tmpPosition['positionName'])
        icon_path.append(tmpRosters['baseIconPath'] + tmpPosition['urlIconSet'])

    tmpRosters = my_replay['game']['teamHome']['roster']

    for positionIndex in range(len(tmpRosters['positionArray'])):
        tmpPosition = tmpRosters['positionArray'][positionIndex]
        positionId.append(tmpPosition['positionId'])
        positionName.append(tmpPosition['positionName'])
        icon_path.append(tmpRosters['baseIconPath'] + tmpPosition['urlIconSet'])

    df_positions = pd.DataFrame( {"positionId": positionId,
                                "positionName": positionName,
                                "icon_path": icon_path
                                })
    df_positions.drop_duplicates(inplace = True, ignore_index = True)

    return df_positions

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
        if team == receiving_team:
            # select first icon
            icon = icon.crop((0,0,icon_w/4,icon_w/4))
        else:
            # select third icon
            icon = icon.crop((icon_w/2, 0, icon_w*3/4, icon_w/4))
        icon = icon.resize((28, 28))
        icon_w, icon_h = icon.size
        pitch.paste(icon, (icon_w * x,icon_h * y), icon)
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
    image_path = 'kickoff_pngs/'
    image_name = str(replay_id) + "_" + str(match_id) + "_kickoff_lower_defense.png"
    fname = image_path + image_name

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

        draw.text((5, 280), text_line0, font=font1, fill='black')
        draw.text((5, 307), text_line1, font=font1, fill='black')
        draw.text((5, 335), text_line2, font=font1, fill='black')
        draw.text((5, 366), text_line3, font=font2, fill='black')

        pitch.save(image_path + image_name,"PNG")
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

def process_replay(replay_id, df_matches, refresh = False):
    my_replay = fetch_replay(replay_id)
    match_id = df_matches.query("replay_id == @replay_id")['match_id'].values[0]

    df_players = extract_players_from_replay(my_replay)
    df_positions = extract_rosters_from_replay(my_replay)
    # roster
    df_players2 = pd.merge(df_players, df_positions, on="positionId", how="left")

    df = parse_replay_file(my_replay)
    #df['coin_choice'] = df.modelChangeValue.str.contains('coinChoice')
    #print(df.query("coin_choice == True"))

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

    # team_home_id = df_matches.query("replay_id == @replay_id")['team1_id'].values[0]
    # team_away_id = df_matches.query("replay_id == @replay_id")['team2_id'].values[0]

    # team_home_id = df_matches.query("replay_id == @replay_id")['team1_id'].values[0]
    # team_away_id = df_matches.query("replay_id == @replay_id")['team2_id'].values[0]

    team1_score = df_matches.query("replay_id == @replay_id")['team1_score'].values[0]
    team2_score = df_matches.query("replay_id == @replay_id")['team2_score'].values[0]

    # if receiving_team == "teamHome":
    #     if int(team_id_offensive) != int(team_home_id):
    #         print("Err")
    #     if int(team_id_defensive) != int(team_away_id):
    #         print("Err")
    # else: 
    #     if int(team_id_offensive) != int(team_away_id):
    #         print("Err")
    #     if int(team_id_defensive) != int(team_home_id):
    #         print("Err")   

    
    coach1 = my_replay['game']['teamHome']['coach']
    coach2 = my_replay['game']['teamAway']['coach']
    
    race1 = my_replay['game']['teamHome']['race']
    race2 = my_replay['game']['teamAway']['race']

    receiving_coach = my_replay['game'][receiving_team]['coach']

    text = [coach1, coach2, race1, race2, team1_score, team2_score, receiving_team] # 1 home # 2 away
    # create the plots
    create_defense_plot(replay_id, match_id, positions, receiving_team, text, refresh)

    #create_offense_plot(replay_id, match_id, positions, receiving_team, refresh)

    #create_vertical_plot(replay_id, match_id, positions, receiving_team)

    #create_horizontal_plot(replay_id, match_id, positions, receiving_team)
    return replay_id, match_id, team_id_defensive, race_defensive, team_id_offensive, race_offensive
