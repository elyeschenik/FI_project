from xlwings import Book, Range
import matplotlib.pyplot as plt
from deposit import *
from fra import *
from swap import *
from convention import *
from swaption import *
from CMS import *
from workalendar.usa import NewYork


type_of_product = input("What product do you want to price (type \"Deposit\", \"FRA\" \"Swap\", \"PSwaption\", \"CSSwaption\" or \"CSSwaption SABR\")?")



pricing_date = datetime(2021,4,5)
start_date = datetime(2021,9,5)
end_date = datetime(2023,9,5)

curve_1 = pd.read_excel("curves.xlsx", sheet_name="OIS Curve for discounting", index_col=0)
curve_2 = pd.read_excel("curves.xlsx", sheet_name="USD3M - Curve for forwards", index_col=0)


convention = convention(365, NewYork(), 2)

notional = 1000000


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
    fixed_rate = 0.017390935752700898
    fixed_freq = 1 #per year
    float_freq = 2

    SWAP = Swap(pricing_date, start_date, end_date, curve_1, curve_2, isPayer, fixed_rate, fixed_freq, float_freq, convention, notional)
    print("The swap present value is {:.2f}$".format(round(SWAP.PV(), 2)))
    print("The swap par rate is {}%".format(SWAP.Get_par_rate() * 100))
    
###############################Physical SWAPTION################################
if type_of_product == "PSwaption":

    isPayer = True
    fixed_freq = 1 #per year
    float_freq = 2

    vol = 0.06
    strike = 0.01
    expiry = start_date

    PSWAPTION = Physical_Swaption(pricing_date, start_date, end_date, expiry, curve_1, curve_2, isPayer, strike, fixed_freq, float_freq, vol, convention, notional)
    print("The physical swaption present value is {:.2f}$".format(round(PSWAPTION.PV(), 2)))

###############################Cash-Settled SWAPTION################################
if type_of_product == "CSSwaption":

    isPayer = True
    fixed_freq = 1 #per year
    float_freq = 2

    vol = 0.06
    strike = 0.01
    expiry = start_date
    

    CSSWAPTION = Cash_Settled_Swaption(pricing_date, start_date, end_date, expiry, curve_1, curve_2, isPayer, strike, fixed_freq, float_freq, vol, convention, notional)
    print("The cash settled swaption present value is {:.2f}$".format(round(CSSWAPTION.PV(), 2)))

###############################Cash-Settled SWAPTION using SABR################################
if type_of_product == "CSSwaption SABR":

    isPayer = True
    fixed_freq = 1 #per year
    float_freq = 2

    strike = 0.01
    expiry = start_date  
    
    sigma_0 = 0.35
    alpha = 0.15
    beta = 0.4
    rho = -0.3

    CSSWAPTION_SABR = Cash_Settled_Swaption_SABR(pricing_date, start_date, end_date, expiry, curve_1, curve_2, isPayer, strike, fixed_freq, float_freq, sigma_0, alpha, beta, rho, convention, notional)
    print("The cash settled swaption using SABR present value is {:.2f}$".format(round(CSSWAPTION_SABR.PV(), 2)))
    print("The SABR implied volatility is {:.2f}".format(CSSWAPTION_SABR.Get_implied_SABR()))

############################### CMS ################################
if type_of_product == "CMS":
    isPayer = True
    fixed_freq = 1  # per year
    float_freq = 2

    nb_strikes = 100
    vol = 0.06
    strike = 0.01

    MyCMS = CMS(pricing_date, start_date, end_date, curve_1, curve_2, isPayer, strike, nb_strikes, fixed_freq, float_freq, vol, convention, notional)
    print("The CMS present value is {:.2f}$".format(round(MyCMS.PV(), 2)))