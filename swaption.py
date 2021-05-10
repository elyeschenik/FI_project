from product import *
from swap import *
from scipy.optimize import brentq, bisect

class Swaption(Product):

    def __init__(self, pricing_date, start_date, end_date, expiry, curve_1, curve_2, isPayer, strike, fixed_freq, float_freq, fixed_convention, float_convention, vol, forward_convention, discount_convention, notional = 1000):
        super(Swaption, self).__init__(pricing_date, start_date, end_date, curve_1, curve_2, forward_convention, discount_convention, notional)
        self.swap = Swap(pricing_date, start_date, end_date, curve_1, curve_2, isPayer, 0, fixed_freq, float_freq,
                         fixed_convention, float_convention, forward_convention, discount_convention, notional)
        self.spot_swap_rate = self.swap.Get_forward_rate()

        self.isPayer = isPayer
        self.fixed_freq = fixed_freq
        self.float_freq = float_freq

        self.strike = strike
        self.vol = vol
        self.expiry = expiry

        self.Level = None


    @abstractmethod
    def PV(self):
        pass

class Physical_Swaption(Swaption):
    def __init__(self, pricing_date, start_date, end_date, expiry, curve_1, curve_2, isPayer, strike, fixed_freq, float_freq, fixed_convention, float_convention, vol, forward_convention, discount_convention, notional = 1000):
        super(Physical_Swaption, self).__init__(pricing_date, start_date, end_date, expiry, curve_1, curve_2, isPayer, strike, fixed_freq, float_freq, fixed_convention, float_convention, vol, forward_convention, discount_convention, notional)


    def PV(self):
        self.Level = self.swap.Level
        T = self.forward_convention.coverage(self.pricing_date, self.expiry)
        if self.isPayer:
            return self.notional * self.Level * self.BSClosedForm(self.spot_swap_rate, self.strike, 0, self.vol, T, True)
        else:
            return -self.notional * self.Level * self.BSClosedForm(self.spot_swap_rate, self.strike, 0, self.vol, T, True)


class Cash_Settled_Swaption(Swaption):
    def __init__(self, pricing_date, start_date, end_date, expiry, curve_1, curve_2, isPayer, strike, fixed_freq, float_freq, fixed_convention, float_convention, vol, forward_convention, discount_convention, notional = 1000, spot_swap_rate = None, spot_swap_rate_level = None, dates = None):
        super(Cash_Settled_Swaption, self).__init__(pricing_date, start_date, end_date, expiry, curve_1, curve_2, isPayer, strike, fixed_freq, float_freq, fixed_convention, float_convention, vol, forward_convention, discount_convention, notional)

        self.Level_Cash = 0

        if spot_swap_rate is None:
            self.swap = Swap(pricing_date, start_date, end_date, curve_1, curve_2, isPayer, 0, fixed_freq, float_freq, fixed_convention, float_convention, forward_convention, discount_convention, notional)
            self.spot_swap_rate = self.swap.Get_forward_rate()
        else:
            self.spot_swap_rate = spot_swap_rate

        if spot_swap_rate_level is None:
            self.swap_level = Swap(expiry, start_date, end_date, curve_1, curve_2, isPayer, 0, fixed_freq, float_freq, fixed_convention, float_convention, forward_convention, discount_convention, notional)
            self.spot_swap_rate_level = self.swap_level.Get_forward_rate()
        else:
            self.spot_swap_rate_level = spot_swap_rate_level

        if dates is None:
            self.dates = self.swap_level.fixed_dates
        else:
            self.dates = dates

    """
    def Get_Level_bis(self, s = None):
        N = self.forward_convention.coverage(self.start_date, self.end_date)
        if s is None:
            s = self.spot_swap_rate_level

        Level = 0
        for i in range(1, int(N) + 1):
            Level += (1 + s/self.fixed_freq) ** (- i * self.fixed_freq)

        if s is not None:
            self.Level = Level
        return Level
    """


    def Get_Level_Cash(self, s = None):
        N = len(self.dates)
        f = self.fixed_freq
        if s is None:
            s = self.spot_swap_rate_level

        Level_Cash = sum([(1 + s/f)**(-i*f) for i in range(1, N)])

        self.Level_Cash = Level_Cash
        return Level_Cash

    @abstractmethod
    def Get_implied_SABR(self):
        pass

    def PV(self):
        Flag = False
        self.Get_Level_Cash()
        if self.vol is None:
            self.Get_implied_SABR()
            Flag = True
        T = self.forward_convention.coverage(self.pricing_date, self.expiry)
        if self.isPayer:
            out = self.notional * self.get_DF(self.expiry) * self.Level_Cash * self.BSClosedForm(self.spot_swap_rate, self.strike, 0, self.vol, T, True)
        else:
            out = -self.notional * self.get_DF(self.expiry) * self.Level_Cash * self.BSClosedForm(self.spot_swap_rate, self.strike, 0, self.vol, T, True)
        if Flag:
            self.vol = None
        return out

class Cash_Settled_Swaption_SABR(Cash_Settled_Swaption):
    def __init__(self, pricing_date, start_date, end_date, expiry, curve_1, curve_2, isPayer, strike, fixed_freq, float_freq, fixed_convention, float_convention, sigma_0, alpha, beta, rho, forward_convention, discount_convention, notional = 1000, spot_rate = None, spot_swap_rate_level = None, dates = None):
        super(Cash_Settled_Swaption_SABR, self).__init__(pricing_date, start_date, end_date, expiry, curve_1, curve_2, isPayer, strike, fixed_freq, float_freq, fixed_convention, float_convention, None, forward_convention, discount_convention, notional, spot_rate, spot_swap_rate_level, dates)

        self.sigma_0 = sigma_0
        self.alpha = alpha
        self.beta = beta
        self.rho = rho

    def Get_implied_SABR(self):
        #self.spot_swap_rate = 0.027
        T_ex = self.forward_convention.coverage(self.pricing_date, self.expiry)
        C = (self.spot_swap_rate * self.strike)**((1 - self.beta)/2)

        B = C *(1 + (1/24)*(1 - self.beta)**2 * np.log(self.spot_swap_rate/self.strike)**2
                + (1/1920)*(1 - self.beta)**4 * np.log(self.spot_swap_rate/self.strike)**4)

        A = self.sigma_0 * (1 + (((1 - self.beta)**2 * self.sigma_0**2)/(24 * C**2)
                                 + (self.rho * self.beta * self.alpha * self.sigma_0)/(4 * C)
                                 + ((2 - 3 * self.rho**2) * self.alpha**2)/24) * T_ex)

        z =(1/self.sigma_0) * self.alpha * C * np.log(self.spot_swap_rate/self.strike)

        x = np.log((np.sqrt(1 - 2 * self.rho * z + z **2) + z - self.rho)/(1 - self.rho))

        SABR_vol = (A * z)/(B * x)
        self.vol = SABR_vol
        return SABR_vol


    def Get_implied_SABR_approx(self):
        lbda = (self.alpha/self.sigma_0) * self.spot_swap_rate ** (1 - self.beta)
        part_1 = - 0.5 * (1 - self.beta - self.rho * lbda) * np.log(self.strike/self.spot_swap_rate)
        part_2 = (1/12) * ((1 - self.beta)**2 + (2 - 3 * self.rho**2)*lbda**2) * np.log(self.strike/self.spot_swap_rate)**2
        SABR_vol = (self.sigma_0/ (self.spot_swap_rate ** (1 - self.beta))) * (1 + part_1 + part_2)
        self.vol = SABR_vol
        return SABR_vol






  
    