import datetime

def epoch_to_date(epoch: int):
  return datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d')