from deposit import *
from fra import *
from swap import *
from convention import *

type_of_product = input("What product do you want to price (type \"Deposit\", \"FRA\" or \"Swap\")?")

pricing_date = datetime(2021,4,5)
start_date = datetime(2021,4,5)
end_date = datetime(2022,10,2)

curve_1 = pd.read_excel("curves.xlsx", sheet_name="OIS Curve for discounting", index_col=0)
curve_2 = pd.read_excel("curves.xlsx", sheet_name="USD3M - Curve for forwards", index_col=0)


convention = convention(365, "aasba", "aasba")

notional = 100

##############################DEPOSIT##############################
if type_of_product == "Deposit":
    deposit_rate = 0.01
    isFloating = False

    DEPOSIT = Deposit(pricing_date, start_date, end_date, curve_1, curve_2, deposit_rate, isFloating, convention, notional)
    print("The deposit present value is {:.2f}$".format(round(DEPOSIT.PV(), 2)))

##############################FORWARD##############################
if type_of_product == "FRA":

    isPayer = True

    FRA_1 = FRA(pricing_date, start_date, end_date, curve_1, curve_2, isPayer, convention, notional)
    print("The FRA present value is {:.2f}$".format(round(FRA_1.PV(), 2)))

###############################SWAP################################
if type_of_product == "Swap":

    isPayer = True
    #fixed_rate = 0.001935876
    fixed_rate = 0.012458899296689196
    fixed_freq = 1 #per year
    float_freq = 2

    SWAP = Swap(pricing_date, start_date, end_date, curve_1, curve_2, isPayer, fixed_rate, fixed_freq, float_freq, convention, notional)
    print("The swap present value is {:.2f}$".format(round(SWAP.PV(), 2)))
    print("The swap par rate is {}%".format(SWAP.Get_par_rate()))