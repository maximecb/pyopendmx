import datetime

def is_night():
    # Get the current local time
    now = datetime.datetime.now()
    #print(now)

    # Before 4:30AM
    if now.hour <= 4 or (now.hour == 4 and now.minute <= 30):
        return True

    # After 9:15PM
    if (now.hour >= 21 and now.minute >= 15) or (now.hour >= 22):
        return True

    return False

print(is_night())