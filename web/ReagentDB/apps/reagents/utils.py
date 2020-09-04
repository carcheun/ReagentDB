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




#    '200814T150929'