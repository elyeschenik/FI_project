from xlwings import Book, Range
from deposit import *
from fra import *
from swap import *
from convention import *
from swaption import *
from workalendar.usa import NewYork



wb = Book('Input-Group7.xlsm')  # Creates a reference to the calling Excel file
sht = wb.sheets['Excel Connect']# Write desired dimensions into Cell B1
#pricing_date = sht.range('D2').value

type_of_product = sht.range('B2').value
#sht.range('B2').value = 10

pricing_date = datetime(2021,4,5)
start_date = datetime(2021,9,5)
end_date = datetime(2023,9,5)

curve_1 = pd.read_excel("curves.xlsx", sheet_name="OIS Curve for discounting", index_col=0)
curve_2 = pd.read_excel("curves.xlsx", sheet_name="USD3M - Curve for forwards", index_col=0)


convention = convention(365, NewYork(), 2)

notional = 1000000