import datetime as dt
from zoneinfo import ZoneInfo
user_tz = 'Europe/Paris'
server_tz = 'Europe/Moscow'


now = dt.datetime.now(ZoneInfo(user_tz))
midnight_in_paris = dt.datetime(year=now.year, month=now.month, day=now.day, tzinfo=ZoneInfo(user_tz))
midnight_in_minsk = dt.datetime(year=now.year, month=now.month, day=now.day, tzinfo=ZoneInfo(server_tz))
print(midnight_in_paris.timestamp())
print(midnight_in_minsk.timestamp())