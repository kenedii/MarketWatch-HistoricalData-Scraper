import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import io
import numpy as np

# DATES MUST BE IN FORMAT "DD/MM/YYYY HH:MM"
category = "cryptocurrency"  # 'stock', 'index', 'cryptocurrency', 'currency'
ticker = "btcusd"  # Use MarketWatch URL to get the ticker symbol
start_date = "01/01/1971 0:00"  # Leave unchanged for earliest available data
end_date = datetime.now().strftime("%d/%m/%Y %H:%M")  # leave unchanged for latest available data

# Custom headers and cookies to avoid status code 401 upon request
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "DNT": "1",
    "Host": "www.marketwatch.com",
    "Priority": "u=0, i",
    "Referer": "https://www.marketwatch.com/investing/stock/rblx/download-data",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Sec-GPC": "1",
    "TE": "trailers",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"
}

# Custom cookies
cookies = {
    "ab_uuid": "1293e0b4-888g-487c-0192-a7a1ff0cc999",
    "fullcss-quote": "quote-0ac6b20339.min.css",
    "gdprApplies": "false",
    "icons-loaded": "true",
    "letsGetMikey": "enabled",
    "mw_loc": '{"Region":"ON","Country":"CA","Continent":"NA","ApplicablePrivacy":0}',
    "recentqsmkii": "Stock-US-RBLX|Stock-US-CSV|Index-US-VIX|Index-US-SPX|Index-US-COMP",
    "refresh": "off"
}

def downloadStockPrice(ticker: str, start_date="01/01/1971 0:00", end_date="01/01/2021 0:00", returns=True, logreturns=True):
    start_dt = datetime.strptime(start_date, "%d/%m/%Y %H:%M")
    end_dt = datetime.strptime(end_date, "%d/%m/%Y %H:%M")
    
    combined_data = pd.DataFrame()
    current_end_dt = end_dt
    one_year = timedelta(days=365)
    base_url = f"https://www.marketwatch.com/investing/{category}/{ticker}/downloaddatapartial"

    while current_end_dt > start_dt:
        current_start_dt = max(current_end_dt - one_year, start_dt)
        start_date_str = current_start_dt.strftime("%m/%d/%Y %H:%M:%S")
        end_date_str = current_end_dt.strftime("%m/%d/%Y %H:%M:%S")
        
        params = {
            "startdate": start_date_str,
            "enddate": end_date_str,
            "daterange": "d30",
            "frequency": "p1d",
            "csvdownload": "true",
            "downloadpartial": "false",
            "newdates": "false"
        }
        response = requests.get(base_url, params=params, headers=headers, cookies=cookies)
        
        if response.status_code != 200 or not response.text.strip():
            print(f"No more data available for {ticker} after {current_start_dt.strftime('%Y-%m-%d')}.")
            break
        
        try:
            csv_data = io.StringIO(response.text)
            df = pd.read_csv(csv_data)
            if df.empty:
                print(f"No data for {ticker} in the period {current_start_dt} to {current_end_dt}.")
                break
            
            combined_data = pd.concat([df, combined_data], ignore_index=True)
        except Exception as e:
            print(f"Error processing data for {ticker}: {e}")
            break
        
        current_end_dt = current_start_dt - timedelta(seconds=1)

    if combined_data.empty:
        print(f"No data retrieved for {ticker}.")
        return
    
    # Remove commas from numbers before removing quotes
    combined_data = combined_data.replace({r',': ''}, regex=True)

    # Convert 'Date' column to Unix time
    combined_data["Date"] = pd.to_datetime(combined_data["Date"], format="%m/%d/%Y").astype("int64") // 10**9

    # Initialize the columns for returns and log returns
    combined_data['Returns'] = np.nan
    combined_data['LogReturns'] = np.nan

    # Calculate returns and log returns if required
    if returns:
        for i in range(1, len(combined_data)):
            p1 = int(combined_data.iloc[i - 1]["Close"])
            p2 = int(combined_data.iloc[i]["Close"])
            t1 = int(combined_data.iloc[i - 1]["Date"])
            t2 = int(combined_data.iloc[i]["Date"])
            # Calculate returns
            if p1 != 0 and p2 != 0:
                returns_value = (p2 / p1) / ((t2 - t1) / 86400)  # Convert time difference from seconds to days
                combined_data.at[i, 'Returns'] = -1*returns_value
    
    if logreturns:
        for i in range(1, len(combined_data)):
            returns_value = combined_data.iloc[i]["Returns"]
            if returns_value > 0:
                log_return = np.log(returns_value)
                combined_data.at[i, 'LogReturns'] = log_return

    # Save the data with returns and log returns to CSV
    output_file = f"{ticker}_data.csv"
    combined_data.to_csv(output_file, index=False) 
    print(f"Data for {ticker} with returns and log returns saved to {output_file}.")

# Execute the function
if __name__ == "__main__":
    downloadStockPrice(ticker, start_date, end_date)
