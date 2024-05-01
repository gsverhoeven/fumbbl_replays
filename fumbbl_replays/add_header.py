import pandas as pd

def add_header(df, my_replay):
    
    df_header = pd.DataFrame( {"commandNr": [0, 0], 
                        "gameTime": [0, 0],
                        "turnTime": [0, 0],
                        "Half": [0, 0],
                        "turnNr": [0, 0],
                        "turnMode": ["startGame", "startGame"],
                        "modelChangeId": ["homeCoachName", "awayCoachName"],
                        "modelChangeKey": [0, 0],
                        "modelChangeValue": [my_replay['game']['teamHome']['coach'], my_replay['game']['teamAway']['coach']],
                        "SetPlayerCoordinate": ["", ""],
                        "PlayerCoordinateX": [99, 99],
                        "PlayerCoordinateY": [99, 99],
                        "SetPlayerState": [0, 0]}, index = [0, 1])

    df = pd.concat([df_header, df], ignore_index=True)
    
    return df
