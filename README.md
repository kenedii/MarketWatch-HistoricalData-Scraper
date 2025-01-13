# MarketWatch-HistoricalData-Scraper
Get more than 1 year of historical stock data from MarketWatch. Gives the data for Date,Open,High,Low,Close,Returns,LogReturns.

**Dependencies:**

`pip install requests`

`pip install pandas`

run `python download-cli.py` to get a cli that walks you through instructions on how to download historical data.

Instructions (for working with pricescraper.py directly) :
1. Edit the file and change the variables from lines 7-11 to what you need

**DATES MUST BE IN FORMAT "DD/MM/YYYY HH:MM"**

category = "index"  # 'stock', 'index', 'cryptocurrency', 'currency' (the category is in the URL to the asset on MarketWatch)

ticker = "djia"  # Use MarketWatch URL to get the exact ticker symbol

start_date = "01/01/1971 0:00"  # Leave unchanged for earliest available data

end_date = datetime.now().strftime("%d/%m/%Y %H:%M")  # leave unchanged for latest available data

**Parameters of def downloadStockPrice():**

returns=True, logreturns=True # Whether to include the returns and LogReturns columns in the dataset, true by default

2. **Run the file and wait for your csv!**
