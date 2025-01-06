import pricescraper as ps
from datetime import datetime

print("DATES MUST BE IN FORMAT \"DD/MM/YYYY HH:MM\"")
print("\n1. Open the link to the asset you want to download historical data for.")
print("2. You will need the category (found in url after 'investing/')")
print("3. Enter the category. e.g. 'stock', 'index', 'cryptocurrency', 'currency'")
ps.category = input("Category: ")  # 'stock', 'index', 'cryptocurrency', 'currency'

print("\n4. You will need the ticker symbol (found in url after the category)")
ps.ticker = input("Ticker: ")  # Use MarketWatch URL to get the ticker symbol

print("\n5. Enter the start date in the format \"DD/MM/YYYY HH:MM\"")
print("Press Enter for earliest available data.")
sd = input("Start Date: ")
if sd != "":
    ps.start_date = sd
else:
    ps.start_date = "01/01/1971 0:00"  # Leave unchanged for earliest available data

print("\n6. Enter the start date in the format \"DD/MM/YYYY HH:MM\"")
print("Press Enter for earliest available data.")
ed = input("End Date: ")
if ed != "":
    ps.end_date = ed
else:
    ps.end_date = datetime.now().strftime("%d/%m/%Y %H:%M")  # leave unchanged for latest available data

print("\nAttempting to download historical data ...")
ps.downloadStockPrice(ps.ticker, ps.start_date, ps.end_date)