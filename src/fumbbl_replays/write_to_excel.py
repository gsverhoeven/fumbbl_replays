import pandas as pd

def write_to_excel(pd_replay, df_roster, path = 'output/output.xlsx'):
    writer = pd.ExcelWriter(path, engine = 'openpyxl')

    cols = ['commandNr', 'gameTime', 'turnTime', 'Half',  'turnNr', 'turnMode', 'set_up_id', \
                'playerAction', 'modelChangeId', 'modelChangeKey', 'defenderId', 'modelChangeValue']

    # intersection of two lists   
    cols_sel = [value for value in cols if value in  pd_replay.columns]
    
    pd_replay.to_excel(writer, sheet_name = 'gamelog', columns = cols_sel) # define selection plus order
    df_roster.to_excel(writer, sheet_name = 'roster')
    writer.close()
