from product import *
from swap import *
from scipy.optimize import brentq, bisect

class Swaption(Product):

    def __init__(self, pricing_date, start_date, end_date, expiry, curve_1, curve_2, isPayer, strike, fixed_freq, float_freq, vol, convention, notional = 1000):
        super(Swaption, self).__init__(pricing_date, start_date, end_date, curve_1, curve_2, convention, notional)

        self.isPayer = isPayer
        self.fixed_freq = fixed_freq
        self.float_freq = float_freq

        self.strike = strike
        self.vol = vol
        self.expiry = expiry

        self.Level = None

    @abstractmethod
    def Get_Level(self):
        pass

    @abstractmethod
    def PV(self):
        pass

class Physical_Swaption(Swaption):
    def __init__(self, pricing_date, start_date, end_date, expiry, curve_1, curve_2, isPayer, strike, fixed_freq, float_freq, vol, convention, notional = 1000):
        super(Physical_Swaption, self).__init__(pricing_date, start_date, end_date, expiry, curve_1, curve_2, isPayer, strike, fixed_freq, float_freq, vol, convention, notional)
        self.swap = Swap(pricing_date, start_date, end_date, curve_1, curve_2, isPayer, 0, fixed_freq, float_freq, convention, notional)
        self.spot_swap_rate = self.swap.Get_par_rate()

    def Get_Level(self):
        delta = 1/self.fixed_freq
        Level = 0
        T_i = self.start_date
        #TODO vérifier pk mettre < ou <=
        while T_i < self.end_date:
            Level += delta * self.get_DF(T_i, 1)
            T_i += timedelta(days = delta * self.convention.day_count_basis)
        self.Level = Level
        return Level

    def Get_Level_Approx(self):
        delta = 1 / self.fixed_freq
        N = self.coverage(self.start_date, self.end_date) * self.fixed_freq
        self.Level = N * delta
        return N * delta

    def PV(self):
        self.Get_Level()
        T = self.coverage(self.pricing_date, self.expiry)
        if self.isPayer:
            return self.notional * self.Level * self.BSClosedForm(self.spot_swap_rate, self.strike, 0, self.vol, T, True)
        else:
            return -self.notional * self.Level * self.BSClosedForm(self.spot_swap_rate, self.strike, 0, self.vol, T, True)


class Cash_Settled_Swaption(Swaption):
    def __init__(self, pricing_date, start_date, end_date, expiry, curve_1, curve_2, isPayer, strike, fixed_freq, float_freq, vol, convention, notional = 1000):
        super(Cash_Settled_Swaption, self).__init__(pricing_date, start_date, end_date, expiry, curve_1, curve_2, isPayer, strike, fixed_freq, float_freq, vol, convention, notional)
        self.swap = Swap(start_date, start_date, end_date, curve_1, curve_2, isPayer, 0, fixed_freq, float_freq, convention, notional)
        self.spot_swap_rate = self.swap.Get_par_rate()

    def Get_Level(self):
        N = self.coverage(self.start_date, self.end_date) * self.fixed_freq

        Level = 0
        for i in range(int(N)):
            Level += (1 + self.spot_swap_rate/self.fixed_freq) ** (- i * self.fixed_freq)
        self.Level = Level
        return Level

    def PV(self):
        self.Get_Level()
        T = self.coverage(self.pricing_date, self.start_date)
        if self.isPayer:
            return self.notional * self.get_DF(self.start_date) * self.Level * self.BSClosedForm(self.spot_swap_rate, self.strike, 0, self.vol, T, True)
        else:
            return -self.notional * self.get_DF(self.start_date) * self.Level * self.BSClosedForm(self.spot_swap_rate, self.strike, 0, self.vol, T, True)



