import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import io

# DATES MUST BE IN FORMAT "DD/MM/YYYY HH:MM"
category = "index"  # 'stock', 'index', 'cryptocurrency', 'currency'
ticker = "djia"  # Use MarketWatch URL to get the ticker symbol
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


def downloadStockPrice(ticker: str, start_date="01/01/1971 0:00", end_date="01/01/2021 0:00"):
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
    
    # Convert 'Date' column to Unix time
    combined_data["Date"] = pd.to_datetime(combined_data["Date"], format="%m/%d/%Y").astype("int64") // 10**9

    # Save to a CSV file
    output_file = f"{ticker}_data.csv"
    combined_data.to_csv(output_file, index=False, quoting=1)  # Force minimal quoting
    print(f"Data for {ticker} saved to {output_file}.")

    # Sort the data by Unix time (earliest to latest)
    try:
        data = pd.read_csv(output_file)
        data["Date"] = data["Date"].astype(int)  # Ensure Unix time is treated as an integer
        sorted_data = data.sort_values(by="Date", ascending=True)  # Sort from earliest to latest
        sorted_data.to_csv(output_file, index=False)  # Overwrite the original file
        print(f"Data sorted by Unix time and saved to {output_file}.")
    except Exception as e:
        print(f"Error sorting or saving data: {e}")

    # Remove quotes from the sorted file
    with open(output_file, 'r') as file:
        lines = file.readlines()

    with open(output_file, 'w') as file:
        for line in lines:
            file.write(line.replace('"', ''))

    print(f"Quotes removed from {output_file}.")

# Execute the function
downloadStockPrice(ticker, start_date, end_date)
