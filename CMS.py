from product import *


class CMS(Product):
    def __init__(self,pricing_date, start_date, end_date, expiry, curve_1, curve_2, isPayer, strike, fixed_freq, float_freq, vol, convention, notional):
        super(Product, self).__init__()