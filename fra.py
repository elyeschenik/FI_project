from product import *

class FRA(Product):

    def __init__(self, pricing_date, start_date, end_date, curve_1, curve_2, isPayer, forward_convention, discount_convention, notional = 1000):
        super(FRA, self).__init__(pricing_date, start_date, end_date, curve_1, curve_2, forward_convention, discount_convention, notional)

        self.forward_rate = self.get_Rate(end_date, 2)
        self.isPayer = isPayer

    def PV(self):

        diff_rate = self.get_LIBOR(self.start_date, self.end_date) - self.forward_rate
        delta = self.forward_convention.coverage(self.start_date, self.end_date)

        CF =  self.notional * diff_rate * delta

        if self.isPayer:
            return self.get_DF(self.end_date) * CF
        else:
            return - self.get_DF(self.end_date) * CF
