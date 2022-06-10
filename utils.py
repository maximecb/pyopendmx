import datetime

def is_night():
    # Get the current local time
    now = datetime.datetime.now()
    #print(now)

    # Before 4:45AM
    if now.hour <= 4 or (now.hour == 4 and now.minute <= 45):
        return True

    # After 9:00PM
    if (now.hour >= 21 and now.minute >= 0) or (now.hour >= 22):
        return True

    return False

#print(is_night())
