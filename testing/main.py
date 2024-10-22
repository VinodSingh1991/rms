import os
import shutil
import sqlite3
import pandas as pd
import requests

dv_url = os.path.join('databse-sqllite/travel2.sqlite')
local_file = "databse-sqllite/travel2.sqlite"
backup_file = "databse-sqllite/travel2.backup.sqlite"


def update_dates(file):
    shutil.copy(backup_file, file)
    conn = sqlite3.connect(file)
    cursor = conn.cursor()
    
    tables = pd.read_sql('SELECT name FROM sqlite_master WHERE type="table"', conn).name.tolist()   
    
    tdf = {}
    
    for table in tables:
        tdf[table] = pd.read_sql(f'SELECT * FROM {table}', conn)
        
    for table_name, df in tdf.items():
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    del df
    del tdf
    conn.commit()
    conn.close()

    return file
        

#print(update_dates(local_file))

import re
import numpy as np
import openai
from langchain_core.tools import tool