from product import *
from scipy.optimize import brentq, bisect

class Swap(Product):

    def __init__(self, pricing_date, start_date, end_date, curve_1, curve_2, isPayer, fixed_rate, fixed_freq, float_freq, convention, notional = 1000):
        super(Swap, self).__init__(pricing_date, start_date, end_date, curve_1, curve_2, convention, notional)

        self.isPayer = isPayer
        self.fixed_rate = fixed_rate
        self.fixed_freq = fixed_freq
        self.float_freq = float_freq

        self.fixed_dates = [self.start_date + timedelta(days = int(i * self.convention.day_count_basis/self.fixed_freq)) for i in range(((end_date - start_date)/(self.convention.day_count_basis/self.fixed_freq)).days)] + [self.end_date]
        self.float_dates = [self.start_date + timedelta(days = int(i * self.convention.day_count_basis/self.float_freq)) for i in range(((end_date - start_date)/(self.convention.day_count_basis/self.float_freq)).days)] + [self.end_date]

    def PV(self, f_rate = np.nan):
        if np.isnan(f_rate):
            f_rate = self.fixed_rate
        fixed_leg_val = self.notional * sum([self.get_DF(date) * self.coverage(self.fixed_dates[self.fixed_dates.index(date) - 1], date) * f_rate for date in self.fixed_dates[1:]])
        float_leg_val = self.notional * sum([self.get_DF(date) * self.coverage(self.float_dates[self.float_dates.index(date) - 1], date) * self.get_LIBOR(self.float_dates[self.float_dates.index(date) - 1], date) for date in self.float_dates[1:]])

        if self.isPayer:
            return float_leg_val - fixed_leg_val
        else:
            return fixed_leg_val - float_leg_val

    def Get_par_rate(self):
        f = lambda r: self.PV(r)
        min_rate, max_rate = -0.5, 0.5
        par_rate = bisect(f, min_rate, max_rate)
        return par_rate



        #for date in self.float_dates[1:]:
        #    print("Date =", date)
        #    print("Coverage =",self.coverage(self.float_dates[self.float_dates.index(date) - 1], date))
        #    print("Rate =", (1/self.coverage(self.float_dates[self.float_dates.index(date) - 1], date)) * (self.get_DF(self.float_dates[self.float_dates.index(date) - 1])/self.get_DF(date) - 1))
        #    print("CF=", self.notional * self.get_DF(date) * self.coverage(self.float_dates[self.float_dates.index(date) - 1], date) *((1/self.coverage(self.float_dates[self.float_dates.index(date) - 1], date)) * (self.get_DF(self.float_dates[self.float_dates.index(date) - 1])/self.get_DF(date) - 1)))
