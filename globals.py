
from datetime import datetime

TODAY = datetime.today().replace(hour = 0, minute = 0, second = 0, microsecond = 0)
START_OF_DAY = TODAY.replace(hour = 8)
END_OF_DAY = START_OF_DAY.replace(hour=17)
SECONDS_IN_DAY = (END_OF_DAY - START_OF_DAY).total_seconds()
INCORRECT_ADDRESS_UPDATE_TIME = TODAY.replace(hour = 10, minute = 20)


MPH = 18