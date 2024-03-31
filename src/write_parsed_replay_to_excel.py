def write_parsed_replay_to_excel(df, df_roster, path = 'output/output.xlsx'):
    writer = pd.ExcelWriter(path, engine = 'openpyxl')

    cols = ['commandNr', 'gameTime', 'turnTime', 'Half',  'turnNr', 'turnMode', 'set_up_id', \
                'playerAction', 'modelChangeId', 'modelChangeKey', 'defenderId', 'modelChangeValue']
    
    df.to_excel(writer, sheet_name = 'gamelog', columns = cols) # define selection plus order
    df_roster.to_excel(writer, sheet_name = 'roster')
    writer.close()
