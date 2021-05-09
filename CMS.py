from swaption import *


class CMS_Mother(Product):
    def __init__(self, pricing_date, start_date, end_date, curve_1, curve_2, isPayer, strike, nb_strikes, fixed_freq, float_freq, fixed_convention, float_convention, vol, forward_convention, discount_convention, notional):
        super(CMS_Mother, self).__init__(pricing_date, start_date, end_date, curve_1, curve_2, forward_convention, discount_convention, notional)

        self.isPayer = isPayer
        self.fixed_freq = fixed_freq
        self.float_freq = float_freq

        self.fixed_convention = fixed_convention
        self.float_convention = float_convention

        self.nb_strikes = nb_strikes
        self.strike = strike
        self.vol = vol
        self.expiry = start_date


        self.strikes = np.zeros(nb_strikes)
        self.weights = np.zeros(nb_strikes)
        self.swaptions = []
        self.swaption_prices = np.zeros(nb_strikes)


    def Get_Strikes(self):
        for j in range(self.nb_strikes):
            self.strikes[j] = self.strike + j**2 * (4*self.strike)/(self.nb_strikes**2)

    @abstractmethod
    def Build_Swaption(self, j , spot_rate, spot_rate_level, dates):
        pass

    def Get_Swaptions(self):
        spot_rate = None
        spot_rate_level = None
        dates = None
        for j in range(self.nb_strikes):
            MySwaption = self.Build_Swaption(j , spot_rate, spot_rate_level, dates)
            self.swaptions.append(MySwaption)
            self.swaption_prices[j] = self.swaptions[j].PV()
            if spot_rate is None:
                spot_rate = MySwaption.spot_swap_rate
                spot_rate_level = MySwaption.spot_swap_rate_level
                dates = MySwaption.dates



    def Get_Weights(self):
        self.weights[0] = 1/self.swaptions[1].Get_Level(self.strikes[1])
        for j in range(1,self.nb_strikes - 1):
            K_j_1 = self.strikes[j+1]
            K_j = self.strikes[j]
            L_K_j_1 = self.swaptions[j+1].Get_Level(K_j_1)
            self.weights[j] = (1/(K_j_1 - K_j))*(((K_j_1 - self.strike)/L_K_j_1) - np.dot(self.weights[:j], K_j_1 - self.strikes[:j]))

        self.weights = self.weights/self.weights.sum()


    def PV(self):
        self.Get_Strikes()
        self.Get_Swaptions()
        self.Get_Weights()
        out = np.dot(self.weights, self.swaption_prices)
        if self.isPayer:
            return out
        else:
            return -out


class CMS(CMS_Mother):
    def __init__(self, pricing_date, start_date, end_date, curve_1, curve_2, isPayer, strike, nb_strikes, fixed_freq, float_freq, fixed_convention, float_convention, vol, forward_convention, discount_convention, notional = 1000):
        super(CMS, self).__init__(pricing_date, start_date, end_date, curve_1, curve_2, isPayer, strike, nb_strikes, fixed_freq, float_freq, fixed_convention, float_convention, vol, forward_convention, discount_convention, notional)

    def Build_Swaption(self, j , spot_rate, spot_rate_level, dates):
        return Cash_Settled_Swaption(self.pricing_date, self.start_date, self.end_date, self.start_date, self.curve_1,
                              self.curve_2, self.isPayer, self.strikes[j], self.fixed_freq, self.float_freq, self.fixed_convention,
                              self.float_convention ,self.vol, self.forward_convention, self.discount_convention, self.notional, spot_rate, spot_rate_level, dates)


class CMS_SABR(CMS_Mother):
    def __init__(self, pricing_date, start_date, end_date, curve_1, curve_2, isPayer, strike, nb_strikes, fixed_freq, float_freq, fixed_convention, float_convention, sigma_0, alpha, beta, rho, forward_convention, discount_convention, notional = 1000):
        super(CMS_SABR, self).__init__(pricing_date, start_date, end_date, curve_1, curve_2, isPayer, strike, nb_strikes, fixed_freq, float_freq, fixed_convention, float_convention, None, forward_convention, discount_convention,  notional)

        self.sigma_0 = sigma_0
        self.alpha = alpha
        self.beta = beta
        self.rho = rho

    def Build_Swaption(self, j , spot_rate, spot_rate_level, dates):
        return Cash_Settled_Swaption_SABR(self.pricing_date, self.start_date, self.end_date, self.start_date, self.curve_1,
                              self.curve_2, self.isPayer, self.strikes[j], self.fixed_freq, self.float_freq, self.fixed_convention,
                              self.float_convention , self.sigma_0, self.alpha, self.beta, self.rho, self.forward_convention,
                              self.fixed_convention, self.notional, spot_rate, spot_rate_level, dates)

        
