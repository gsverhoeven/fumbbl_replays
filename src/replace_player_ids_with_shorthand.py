def replace_player_ids_with_shorthand(df, df_roster):
    
    # fix in columns modelChangeKey, defenderId
    for playerId in df_roster['playerId'].values:
        short_hand = df_roster.loc[df_roster.eval("playerId == @playerId"), 'short_name']

        df.loc[df.eval("modelChangeKey == @playerId"), 'modelChangeKey'] = str(short_hand.values)
        df.loc[df.eval("defenderId == @playerId"), 'defenderId'] = str(short_hand.values)

    # fix in column modelChangeValue (only for reportLists)
    
    for r in range(len(df)):
        # first check if it is a reportList
        if 'reportId' in str(df.iloc[r]['modelChangeValue']):
            reportlist = df.iloc[r]['modelChangeValue']
            if not isinstance(reportlist, dict):
                # convert to valid JSON
                json_reportList = reportlist.replace("'", '"').replace("False", "false").replace("True", "true").replace("None", "null")
                # convert to dict
                reportlist = json.loads(json_reportList)
            if 'playerId' in reportlist:
                playerId = reportlist['playerId'] 
                short_hand = df_roster.loc[df_roster.eval("playerId == @playerId"), 'short_name'] 
                reportlist['playerId'] = str(short_hand.values)
                df.iat[r, df.columns.get_loc('modelChangeValue')] = reportlist
            if 'defenderId' in reportlist:
                playerId = reportlist['defenderId'] 
                short_hand = df_roster.loc[df_roster.eval("playerId == @playerId"), 'short_name'] 
                reportlist['defenderId'] = str(short_hand.values)
                df.iat[r, df.columns.get_loc('modelChangeValue')] = reportlist
            if 'attackerId' in reportlist:
                playerId = reportlist['attackerId'] 
                short_hand = df_roster.loc[df_roster.eval("playerId == @playerId"), 'short_name'] 
                reportlist['attackerId'] = str(short_hand.values)
                df.iat[r, df.columns.get_loc('modelChangeValue')] = reportlist   
            if 'catcherId' in reportlist:
                playerId = reportlist['catcherId'] 
                short_hand = df_roster.loc[df_roster.eval("playerId == @playerId"), 'short_name'] 
                reportlist['catcherId'] = str(short_hand.values)
                df.iat[r, df.columns.get_loc('modelChangeValue')] = reportlist
            # if playerIdTouchdown in reportList / knockoutRecoveryArray playerId /add to parser function
            if reportlist['reportId'] == 'catchRoll':
                df.iat[r, df.columns.get_loc('modelChangeValue')] = parse_catchroll(reportlist)
            if reportlist['reportId'] == 'dodgeRoll':
                df.iat[r, df.columns.get_loc('modelChangeValue')] = parse_dodgeroll(reportlist)
            if reportlist['reportId'] == 'goForItRoll':
                df.iat[r, df.columns.get_loc('modelChangeValue')] = parse_GFIroll(reportlist)
            if reportlist['reportId'] == 'confusionRoll':
                df.iat[r, df.columns.get_loc('modelChangeValue')] = parse_confusionroll(reportlist)
            if reportlist['reportId'] == 'injury':
                df.iat[r, df.columns.get_loc('modelChangeValue')] = parse_injury(reportlist)
            if reportlist['reportId'] == 'turnEnd':
                df.iat[r, df.columns.get_loc('modelChangeValue')] = parse_turnend(reportlist)
        else:
            pass

    return df
    