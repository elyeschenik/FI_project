from deposit import *
from fra import *
from swap import *

type_of_product = input("What product do you want to price (type \"Deposit\", \"FRA\" or \"Swap\")?")

pricing_date = datetime(2020,9,30)
start_date = datetime(2020,10,2)
end_date = datetime(2022,10,2)

curve_1 = pd.read_excel("curves.xlsx", sheet_name="curve_1", index_col=0)
curve_2 = pd.read_excel("curves.xlsx", sheet_name="curve_2", index_col=0)

convention = 365

notional = 100000000

##############################DEPOSIT##############################
if type_of_product == "Deposit":
    deposit_rate = 0.01
    isFloating = False

    DEPOSIT = Deposit(pricing_date, start_date, end_date, curve_1, curve_2, deposit_rate, isFloating, convention, notional)
    print("The deposit present value is {:.2f}$".format(round(DEPOSIT.PV(), 2)))

##############################FORWARD##############################
if type_of_product == "FRA":

    isPayer = True
    forward_rate = 0.0018

    FRA_1 = FRA(pricing_date, start_date, end_date, curve_1, curve_2, isPayer, forward_rate, convention, notional)
    print("The FRA present value is {:.2f}$".format(round(FRA_1.PV(), 2)))

###############################SWAP################################
if type_of_product == "Swap":

    isPayer = True
    fixed_rate = 0.001935876
    fixed_freq = 1 #per year
    float_freq = 2

    SWAP = Swap(pricing_date, start_date, end_date, curve_1, curve_2, isPayer, fixed_rate, fixed_freq, float_freq, convention, notional)
    print("The swap present value is {:.2f}$".format(round(SWAP.PV(), 2)))