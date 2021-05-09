#from workalendar.usa import NewYork
from datetime import datetime, timedelta


holidays_US = [(1, 1),
            (1, 18),
            (2, 12),
            (2, 15),
            (5, 31),
            (7, 4),
            (7, 5),
            (9, 6),
            (10, 11),
            (11, 2),
            (11, 11),
            (11, 25),
            (12, 24),
            (12, 25),
            (12, 31)]

class convention:

    def __init__(self, day_count_basis, calendar, fixing_lag):
        self.day_count_basis = day_count_basis
        if calendar == "US":
            self.holidays = holidays_US
        self.fixing_lag = fixing_lag

    @staticmethod
    def month_delta(date_1, date_2):
        return date_2.month - date_1.month + (date_2.year - date_1.year) * 12

    def coverage(self, date_1, date_2):
        if self.day_count_basis == "ACT/365":
            return (date_2 - date_1).days/365
        elif self.day_count_basis == "ACT/360":
            return (date_2 - date_1).days/360
        elif self.day_count_basis == "30/360":
            return (self.month_delta(date_1, date_2) * 30 + (date_2.day - date_1.day))/360
        else:
            raise Exception("Unexpected convention")
    """ 
    def add_date(self, initial_date, frequency):
        if self.day_count_basis == "ACT/365":
            return initial_date + timedelta(days = 365/frequency)
        elif self.day_count_basis == "ACT/360":
            return initial_date + timedelta(days=360 / frequency)
        elif self.day_count_basis == "30/360":
            return initial_date + timedelta(days=360 / frequency)
        else:
            raise Exception("Unexpected convention")
    """
    def add_date(self, initial_date, nb_days, up = True):
        out_date = initial_date + timedelta(days = nb_days)
        while (out_date.month, out_date.day) in self.holidays:
            if up:
                out_date = out_date + timedelta(days = 1)
            else:
                out_date = out_date + timedelta(days= -1)
        return out_date



