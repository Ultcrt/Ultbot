from datetime import datetime
from datetime import timedelta

if __name__ == "__main__":
    print((datetime.now() + timedelta(days=3)).isocalendar())