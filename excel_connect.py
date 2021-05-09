from xlwings import Book, Range
from deposit import *
from fra import *
from swap import *
from swaption import *
from CMS import *
from convention import *
#from workalendar.usa import NewYork

import os



wb = Book('Input-Group7.xlsm')  # Creates a reference to the calling Excel file
sht = wb.sheets['Excel Connect']

os.chdir(wb.fullname[:-18])


def convert_to_bool(txt):
    if txt == "True":
        return True
    elif txt == "False":
        return False

type_of_product = sht.range('B2').value
notional = sht.range('B3').value

pricing_date = sht.range('B5').value
start_date = sht.range('B6').value
end_date = sht.range('B7').value

curve_1 = pd.read_excel("curves.xlsx", sheet_name="OIS Curve for discounting", index_col=0)
curve_2 = pd.read_excel("curves.xlsx", sheet_name="USD3M - Curve for forwards", index_col=0)


calendar = sht.range('B9').value

day_count_basis_discount = sht.range('B12').value

day_count_basis_forward = sht.range('B15').value
fixing_lag_forward = sht.range('B16').value

forward_convention = convention(day_count_basis_forward, calendar, fixing_lag_forward)
discount_convention = convention(day_count_basis_discount, calendar, 0)

def Read_Params():
    global type_of_product, notional, pricing_date, start_date, \
        end_date, forward_convention, discount_convention, calendar,\
        day_count_basis_discount, day_count_basis_forward, fixing_lag_forward

    type_of_product = sht.range('B2').value
    notional = sht.range('B3').value

    pricing_date = sht.range('B5').value
    start_date = sht.range('B6').value
    end_date = sht.range('B7').value

    calendar = sht.range('B9').value
    day_count_basis_discount = sht.range('B12').value
    day_count_basis_forward = sht.range('B15').value
    fixing_lag_forward = sht.range('B16').value
    forward_convention = convention(day_count_basis_forward, calendar, fixing_lag_forward)
    discount_convention = convention(day_count_basis_discount, calendar, 0)


##############################DEPOSIT##############################
def Compute_Deposit():
    Read_Params()
    deposit_rate = sht.range('F2').value
    isFloating = convert_to_bool(sht.range('F3').value)

    DEPOSIT = Deposit(pricing_date, start_date, end_date, curve_1, curve_2, deposit_rate, isFloating,  forward_convention, discount_convention,
                      notional)
    sht.range('F5').value = DEPOSIT.PV()


##############################FORWARD##############################
def Compute_FRA():
    Read_Params()
    isPayer = convert_to_bool(sht.range('I2').value)

    FRA_1 = FRA(pricing_date, start_date, end_date, curve_1, curve_2, isPayer,  forward_convention, discount_convention, notional)

    sht.range('I4').value = FRA_1.PV()

###############################SWAP################################
def Compute_Swap():
    Read_Params()
    isPayer = convert_to_bool(sht.range('L2').value)
    fixed_rate = sht.range('L5').value
    fixed_freq = sht.range('L4').value  # per year
    float_freq = sht.range('L8').value

    day_count_basis_fixed = sht.range('L6').value
    day_count_basis_float = sht.range('L9').value
    fixed_lag_float = sht.range('L10').value

    fixed_convention = convention(day_count_basis_fixed, calendar, 0)
    float_convention = convention(day_count_basis_float, calendar, fixed_lag_float)

    SWAP = Swap(pricing_date, start_date, end_date, curve_1, curve_2, isPayer, fixed_rate, fixed_freq, float_freq,
                fixed_convention, float_convention, forward_convention, discount_convention, notional)

    sht.range('L12').value = SWAP.PV()
    sht.range('L13').value = SWAP.Get_par_rate()
    return SWAP

###############################Physical SWAPTION################################
def Compute_PSwaption():
    Read_Params()
    isPayer = convert_to_bool(sht.range('F21').value)
    fixed_freq = sht.range('F23').value  # per year
    float_freq = sht.range('F26').value

    day_count_basis_fixed = sht.range('F24').value
    day_count_basis_float = sht.range('F27').value
    fixed_lag_float = sht.range('F28').value

    fixed_convention = convention(day_count_basis_fixed, calendar, 0)
    float_convention = convention(day_count_basis_float, calendar, fixed_lag_float)

    vol = sht.range('F29').value
    strike = sht.range('F30').value
    expiry = sht.range('F31').value

    PSWAPTION = Physical_Swaption(pricing_date, start_date, end_date, expiry, curve_1, curve_2, isPayer, strike,
                                  fixed_freq, float_freq, fixed_convention, float_convention, vol,  forward_convention, discount_convention, notional)

    sht.range('F33').value = PSWAPTION.PV()


###############################Cash-Settled SWAPTION################################

def Compute_CSSwaption():
    Read_Params()
    isPayer = convert_to_bool(sht.range('I21').value)
    fixed_freq = sht.range('I23').value  # per year
    float_freq = sht.range('I26').value

    day_count_basis_fixed = sht.range('L24').value
    day_count_basis_float = sht.range('L27').value
    fixed_lag_float = sht.range('L28').value

    fixed_convention = convention(day_count_basis_fixed, calendar, 0)
    float_convention = convention(day_count_basis_float, calendar, fixed_lag_float)

    vol = sht.range('I29').value
    strike = sht.range('I30').value
    expiry = sht.range('I31').value

    CSSWAPTION = Cash_Settled_Swaption(pricing_date, start_date, end_date, expiry, curve_1, curve_2, isPayer, strike,
                                  fixed_freq, float_freq, fixed_convention, float_convention, vol,  forward_convention, discount_convention, notional)

    sht.range('I33').value = CSSWAPTION.PV()


###############################Cash-Settled SWAPTION using SABR################################
def Compute_CSSwaption_SABR():
    Read_Params()
    isPayer = convert_to_bool(sht.range('L21').value)
    fixed_freq = sht.range('L23').value  # per year
    float_freq = sht.range('L26').value

    day_count_basis_fixed = sht.range('L24').value
    day_count_basis_float = sht.range('L27').value
    fixed_lag_float = sht.range('L28').value

    fixed_convention = convention(day_count_basis_fixed, calendar, 0)
    float_convention = convention(day_count_basis_float, calendar, fixed_lag_float)

    strike = sht.range('L33').value
    expiry = sht.range('L34').value

    sigma_0 = sht.range('L29').value
    alpha = sht.range('L30').value
    beta = sht.range('L31').value
    rho = sht.range('L32').value

    CSSWAPTION_SABR = Cash_Settled_Swaption_SABR(pricing_date, start_date, end_date, expiry, curve_1, curve_2, isPayer,
                                                 strike, fixed_freq, float_freq, fixed_convention, float_convention, sigma_0, alpha, beta, rho,  forward_convention, discount_convention,
                                                 notional)

    sht.range('L36').value = CSSWAPTION_SABR.PV()

############################### CMS ################################
def Compute_CMS():
    Read_Params()
    isPayer = convert_to_bool(sht.range('O2').value)
    fixed_freq = sht.range('O4').value  # per year
    float_freq = sht.range('O7').value

    day_count_basis_fixed = sht.range('O5').value
    day_count_basis_float = sht.range('O8').value
    fixed_lag_float = sht.range('O9').value

    fixed_convention = convention(day_count_basis_fixed, calendar, 0)
    float_convention = convention(day_count_basis_float, calendar, fixed_lag_float)

    nb_strikes = int(sht.range('O12').value)
    vol = sht.range('O10').value
    strike = sht.range('O11').value

    MyCMS = CMS(pricing_date, start_date, end_date, curve_1, curve_2, isPayer, strike, nb_strikes,
                fixed_freq, float_freq, fixed_convention, float_convention, vol,  forward_convention, discount_convention, notional)

    sht.range('O14').value = MyCMS.PV()


############################### CMS SABR ################################
def Compute_CMS_SABR():
    Read_Params()
    isPayer = convert_to_bool(sht.range('O21').value)
    fixed_freq = sht.range('O23').value  # per year
    float_freq = sht.range('O26').value

    day_count_basis_fixed = sht.range('O24').value
    day_count_basis_float = sht.range('O27').value
    fixed_lag_float = sht.range('O28').value

    fixed_convention = convention(day_count_basis_fixed, calendar, 0)
    float_convention = convention(day_count_basis_float, calendar, fixed_lag_float)

    nb_strikes = int(sht.range('O34').value)
    strike = sht.range('O33').value

    sigma_0 = sht.range('O29').value
    alpha = sht.range('O30').value
    beta = sht.range('O31').value
    rho = sht.range('O32').value

    MyCMS_SABR = CMS_SABR(pricing_date, start_date, end_date, curve_1, curve_2, isPayer, strike, nb_strikes,
                fixed_freq, float_freq, fixed_convention, float_convention, sigma_0, alpha, beta, rho,  forward_convention, discount_convention, notional)

    sht.range('O36').value = MyCMS_SABR.PV()

test = Compute_PSwaption()
#test_bis = Compute_CSSwaption()
#test_bis = Compute_CSSwaption_SABR()


if __name__ == '__main__':
    # Expects the Excel file next to this source file, adjust accordingly.
    wb.set_mock_caller()



