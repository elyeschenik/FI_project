from abc import abstractmethod
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class Product:

    def __init__(self, pricing_date, start_date, end_date, curve_1, curve_2, convention, notional):

        super(Product, self).__init__()

        self.pricing_date = pricing_date
        self.start_date = start_date
        self.end_date = end_date

        self.curve_1 = curve_1
        self.curve_2 = curve_2

        self.notional = notional

        self.convention = convention


    def coverage(self, date_1, date_2):
        return (date_2 - date_1).days/self.convention.day_count_basis


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

    def get_Forward(self, date = None, curve_num=1):

        DF = self.get_DF(date, curve_num)
        forward_rate = -np.log(DF)/self.coverage(self.pricing_date, date)
        return forward_rate

    def get_LIBOR(self, date_1, date_2, curve_num=1):

        delta = self.coverage(date_1, date_2)
        B_1 = self.get_DF(date_1, curve_num)
        B_2 = self.get_DF(date_2, curve_num)

        return (1/delta) * ((B_1/B_2) - 1)

    """
    def get_DF_bis(self, date = None):

        discount_rate = self.get_rate(date)
        delta = self.coverage(self.pricing_date, date)

        return np.exp(-discount_rate * delta)
    """

    """
        def get_rate(self, date = None):

        if date is None:
            date = self.end_date

        if date == self.pricing_date:
            return 0

        if date in self.curve_1.index:
            discount_rate = self.curve_1.loc[date].values[0]
        else:
            d_bottom = self.curve_1.loc[self.curve_1.index < date].index[-1]
            d_up = self.curve_1.loc[self.curve_1.index > date].index[0]

            self.curve_1.loc[date] = None

            discount_rate = self.curve_1.sort_index().loc[[d_bottom, date, d_up]].interpolate(method='time').loc[date].values[0]

            self.curve_1.drop(date, axis = 0, inplace = True)

        return discount_rate
    """