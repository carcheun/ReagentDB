import sqlite3
from datetime import datetime

def convert_client_date_format(client_date):
    """Convert string format of date into server format

    Arguments: 
        client_date: date and time as a string in YYMMDDTHHMM format
    
    Returns:
        formated datetime, timezone timestamp
    """
    year = int('20' + client_date[:2])
    month = int(client_date[2:4])
    day = int(client_date[4:6])
    hour = int(client_date[7:9])
    minute = int(client_date[9:11])
    # if length includes seconds, cut seconds in too
    if len(client_date) > 11:
        second = int(client_date[11:])
    else:
        second = 0

    dt = datetime(year=year, month=month, day=day, 
        hour=hour, minute=minute, second=second)
    return dt

# TODO: Remove this is a test function
def ReadFromSQLiteFile(sqlite_filepath):
    # convert file to proper header
    with open(sqlite_filepath, 'r+b') as f:
        data = f.read(16)
        f.seek(0)
        f.write(bytes('SQLite format 3', 'utf-8'))
        f.close()

    conn = sqlite3.connect(sqlite_filepath)
    conn.text_factory = bytes
    cur = conn.cursor()

    cur.execute('SELECT * FROM PA')
    rows = cur.fetchall()
    for row in rows:
        try:
            print(row[0].decode())
        except UnicodeDecodeError:
            print('>>>>>>>>>', row[0])

    # convert the file back
    with open(sqlite_filepath, 'r+b') as f:
        data = f.read(16)
        f.seek(0)
        f.write(bytes('=== pc data ===', 'utf-8'))
        f.close()

#ReadFromSQLiteFile('C:\\Users\\engineer\\source\\repos\\ReagentDB\\app\\reagents\\PA_fact8.d')