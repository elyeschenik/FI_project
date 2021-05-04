from product import *

class Deposit(Product):

    def __init__(self, pricing_date, start_date, end_date, curve_1, curve_2, deposit_rate, isFloating, convention = 360, notional = 1000):
        super(Deposit, self).__init__(pricing_date, start_date, end_date, curve_1, curve_2, convention, notional)

        self.deposit_rate = deposit_rate
        self.isFloating = isFloating

    def PV(self):
        delta = self.coverage(self.start_date, self.end_date)

        if self.isFloating:
            r = self.get_LIBOR(self.start_date, self.end_date)
        else:
            r = self.deposit_rate

        if delta <= 1:
            return self.get_DF(self.end_date) * self.notional * (1 + r * delta)
        else:
            return self.get_DF(self.end_date) * self.notional * (1 + r) ** delta