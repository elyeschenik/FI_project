from abc import abstractmethod
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.stats import norm

class Product:

    def __init__(self, pricing_date, start_date, end_date, curve_1, curve_2, forward_convention, discount_convention, notional):

        super(Product, self).__init__()

        self.pricing_date = pricing_date
        self.start_date = start_date
        self.end_date = end_date

        self.curve_1 = curve_1
        self.curve_2 = curve_2

        self.notional = notional

        self.forward_convention = forward_convention
        self.discount_convention = discount_convention

    """
    def coverage(self, date_1, date_2, convention = None):
        if convention is None:
            return (date_2 - date_1).days/self.convention.day_count_basis
        else:
            return (date_2 - date_1).days / convention.day_count_basis
    """


    def get_DF(self, date = None, curve_num = 1):

        if curve_num == 1:
            curve = self.curve_1
        elif curve_num == 2:
            curve = self.curve_2
        else:
            raise Exception('Please input 1 or 2')

        if date is None:
            date = self.end_date

        if date == self.pricing_date:
            return 1

        if date in curve.index:
            discount_factor = curve.loc[date].values[0]
        else:
            d_bottom = curve.loc[curve.index < date].index[-1]
            d_up = curve.loc[curve.index > date].index[0]

            curve.loc[date] = None

            discount_factor = curve.sort_index().loc[[d_bottom, date, d_up]].interpolate(method='time').loc[date].values[0]

            curve.drop(date, axis = 0, inplace = True)

        return discount_factor

    def get_Rate(self, date = None, curve_num = 2):

        DF = self.get_DF(date, curve_num)
        if curve_num == 1:
            conv = self.discount_convention
        elif curve_num == 2:
            conv = self.forward_convention
        else:
            raise Exception("Wrong curve number, input 1 or 2")
        forward_rate = -np.log(DF)/conv.coverage(self.pricing_date, date)
        return forward_rate

    def get_LIBOR(self, date_1, date_2, conv = None, curve_num = 2):
        if conv is None:
            conv = self.forward_convention
        date_2_adj = self.forward_convention.add_date(date_2, -conv.fixing_lag, False)
        delta = conv.coverage(date_1, date_2_adj)
        B_1 = self.get_DF(date_1, curve_num)
        B_2 = self.get_DF(date_2_adj, curve_num)

        return (1/delta) * ((B_1/B_2) - 1)

    def BSClosedForm(self, S_0, K, r, sigma, T, isCall):
        d1 = (np.log(S_0 / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        if isCall:
            return S_0 * norm.cdf(d1) - np.exp(-r * T) * K * norm.cdf(d2)
        else:
            return -S_0 * norm.cdf(-d1) + np.exp(-r * T) * K * norm.cdf(-d2)


   