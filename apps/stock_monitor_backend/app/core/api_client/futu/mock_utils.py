import random
import pickle
import os
from typing import List, Dict, Optional
import pandas as pd

# Akshare imports for getting stock lists
from akshare import stock_hk_spot_em, get_us_stock_name, stock_zh_a_spot_em

import json
import py_mini_racer
from akshare.stock.stock_us_sina import __get_us_page_count, js_hash_text, us_sina_stock_dict_payload, us_sina_stock_list_url

import requests
from functools import lru_cache
from tqdm import tqdm




@lru_cache()
def get_us_stock_name_with_cached_pages() -> pd.DataFrame:
    """
    u.s. stock's english name, chinese name and symbol
    you should use symbol to get apply into the next function
    https://finance.sina.com.cn/stock/usstock/sector.shtml
    :return: stock's english name, chinese name and symbol
    :rtype: pandas.DataFrame
    """
    cache_dir = os.path.dirname(__file__)
    us_stocks_cache_file = os.path.join(cache_dir, 'us_stocks_data.pkl')
    progress_cache_file = os.path.join(cache_dir, 'us_stocks_progress.pkl')
    
    # Try to load existing data and progress
    big_df = pd.DataFrame()
    completed_pages = set()
    
    if os.path.exists(us_stocks_cache_file):
        try:
            with open(us_stocks_cache_file, 'rb') as f:
                big_df = pickle.load(f)
            print(f"Loaded existing data with {len(big_df)} records")
        except Exception as e:
            print(f"Error loading cached data: {e}")
    
    if os.path.exists(progress_cache_file):
        try:
            with open(progress_cache_file, 'rb') as f:
                completed_pages = pickle.load(f)
            print(f"Loaded progress: {len(completed_pages)} pages completed")
        except Exception as e:
            print(f"Error loading progress: {e}")
    
    page_count = __get_us_page_count()
    print(f"Total pages to process: {page_count}")
    
    # Process pages that haven't been completed yet
    pages_to_process = [page for page in range(1, page_count + 1) if page not in completed_pages]
    
    if not pages_to_process:
        print("All pages already processed!")
        return big_df[["name", "cname", "symbol"]]
    
    print(f"Processing {len(pages_to_process)} remaining pages...")
    
    for page in tqdm(pages_to_process, leave=False):
        try:
            us_js_decode = (
                "US_CategoryService.getList?page={}&num=20&sort=&asc=0&market=&id=".format(
                    page
                )
            )
            js_code = py_mini_racer.MiniRacer()
            js_code.eval(js_hash_text)
            dict_list = js_code.call("d", us_js_decode)  # 执行js解密代码
            us_sina_stock_dict_payload.update({"page": "{}".format(page)})
            res = requests.get(
                us_sina_stock_list_url.format(dict_list),
                params=us_sina_stock_dict_payload,
            )
            data_json = json.loads(res.text[res.text.find("({") + 1 : res.text.rfind(");")])
            
            # Add new data to dataframe
            new_df = pd.DataFrame(data_json["data"])
            big_df = pd.concat([big_df, new_df], ignore_index=True)
            
            # Mark page as completed
            completed_pages.add(page)
            
            # Save progress every 10 pages to avoid losing too much work
            if page % 10 == 0:
                try:
                    with open(us_stocks_cache_file, 'wb') as f:
                        pickle.dump(big_df, f)
                    with open(progress_cache_file, 'wb') as f:
                        pickle.dump(completed_pages, f)
                    print(f"Saved progress at page {page}")
                except Exception as e:
                    print(f"Error saving progress at page {page}: {e}")
                    
        except Exception as e:
            print(f"Error processing page {page}: {e}")
            # Save current progress even on error
            try:
                with open(us_stocks_cache_file, 'wb') as f:
                    pickle.dump(big_df, f)
                with open(progress_cache_file, 'wb') as f:
                    pickle.dump(completed_pages, f)
                print(f"Saved progress after error at page {page}")
            except Exception as save_error:
                print(f"Error saving progress after error: {save_error}")
            continue
    
    # Final save
    try:
        with open(us_stocks_cache_file, 'wb') as f:
            pickle.dump(big_df, f)
        with open(progress_cache_file, 'wb') as f:
            pickle.dump(completed_pages, f)
        print(f"Final save completed. Total records: {len(big_df)}")
    except Exception as e:
        print(f"Error in final save: {e}")
    
    return big_df[["name", "cname", "symbol"]]





def get_hk_stock_list() -> List[str]:
    """
    Get Hong Kong stock list using Akshare.
    Returns a list of HK stock codes (e.g., ['00700', '09988', ...])
    """
    if stock_hk_spot_em is None:
        return []
    
    try:
        # Get HK stock data from Akshare
        hk_stocks = stock_hk_spot_em()
        if hk_stocks is not None and not hk_stocks.empty:
            # Extract stock codes from the dataframe
            # Assuming the stock code column is named '代码' or 'code' or similar
            code_column = None
            for col in hk_stocks.columns:
                if any(keyword in col.lower() for keyword in ['代码', 'code', 'symbol']):
                    code_column = col
                    break
            
            if code_column:
                stock_codes = hk_stocks[code_column].dropna().tolist()
                # Clean up codes (remove any non-numeric characters except dots)
                cleaned_codes = []
                for code in stock_codes:
                    if isinstance(code, str):
                        # Remove any non-numeric characters except dots
                        cleaned_code = ''.join(c for c in code if c.isdigit() or c == '.')
                        if cleaned_code:
                            cleaned_codes.append(cleaned_code)
                return cleaned_codes
            else:
                # If we can't find the code column, try the first column
                stock_codes = hk_stocks.iloc[:, 0].dropna().tolist()
                return [str(code) for code in stock_codes if code]
    except Exception as e:
        print(f"Error getting HK stock list: {e}")
    
    return []

def get_a_stock_list() -> List[str]:
    """
    Get Chinese A-share stock list using Akshare.
    Returns a list of A-share stock codes (e.g., ['000001', '600000', ...])
    """
    if stock_zh_a_spot_em is None:
        return []
    
    try:
        # Get A-share stock data from Akshare
        a_stocks = stock_zh_a_spot_em()
        if a_stocks is not None and not a_stocks.empty:
            # Extract stock codes from the dataframe
            # Assuming the stock code column is named '代码' or 'code' or similar
            code_column = None
            for col in a_stocks.columns:
                if any(keyword in col.lower() for keyword in ['代码', 'code', 'symbol']):
                    code_column = col
                    break
            
            if code_column:
                stock_codes = a_stocks[code_column].dropna().tolist()
                # Clean up codes (remove any non-numeric characters except dots)
                cleaned_codes = []
                for code in stock_codes:
                    if isinstance(code, str):
                        # Remove any non-numeric characters except dots
                        cleaned_code = ''.join(c for c in code if c.isdigit() or c == '.')
                        if cleaned_code:
                            cleaned_codes.append(cleaned_code)
                return cleaned_codes
            else:
                # If we can't find the code column, try the first column
                stock_codes = a_stocks.iloc[:, 0].dropna().tolist()
                return [str(code) for code in stock_codes if code]
    except Exception as e:
        print(f"Error getting A-share stock list: {e}")
    
    return []

def get_us_stock_list() -> List[str]:
    """
    Get US stock list using Akshare with improved caching.
    Returns a list of US stock codes (e.g., ['AAPL', 'MSFT', ...])
    """
    try:
        # Use the improved cached function
        us_stocks_df = get_us_stock_name_with_cached_pages()
        if us_stocks_df is not None and not us_stocks_df.empty:
            # Extract stock codes from the 'symbol' column
            if 'symbol' in us_stocks_df.columns:
                stock_codes = us_stocks_df['symbol'].dropna().tolist()
                # Clean up codes (remove any non-alphanumeric characters except dots)
                cleaned_codes = []
                for code in stock_codes:
                    if isinstance(code, str):
                        # Remove any non-alphanumeric characters except dots
                        cleaned_code = ''.join(c for c in code if c.isalnum() or c == '.')
                        if cleaned_code:
                            cleaned_codes.append(cleaned_code)
                return cleaned_codes
            else:
                # If 'symbol' column not found, try the first column
                stock_codes = us_stocks_df.iloc[:, 0].dropna().tolist()
                return [str(code) for code in stock_codes if code]
    except Exception as e:
        print(f"Error getting US stock list: {e}")
    
    return []

def load_cached_stock_lists() -> Dict[str, List[str]]:
    """
    Load cached stock lists from pickle files.
    Returns a dictionary with 'HK', 'US', and 'A' keys containing stock lists.
    """
    cache_dir = os.path.dirname(__file__)
    hk_cache_file = os.path.join(cache_dir, 'hk_stock_list.pkl')
    us_cache_file = os.path.join(cache_dir, 'us_stock_list.pkl')
    a_cache_file = os.path.join(cache_dir, 'a_stock_list.pkl')
    
    stock_lists = {'HK': [], 'US': [], 'A': []}
    
    # Load HK stock list
    if os.path.exists(hk_cache_file):
        try:
            with open(hk_cache_file, 'rb') as f:
                stock_lists['HK'] = pickle.load(f)
        except Exception as e:
            print(f"Error loading cached HK stock list: {e}")
    
    # Load US stock list
    if os.path.exists(us_cache_file):
        try:
            with open(us_cache_file, 'rb') as f:
                stock_lists['US'] = pickle.load(f)
        except Exception as e:
            print(f"Error loading cached US stock list: {e}")
    
    # Load A-share stock list
    if os.path.exists(a_cache_file):
        try:
            with open(a_cache_file, 'rb') as f:
                stock_lists['A'] = pickle.load(f)
        except Exception as e:
            print(f"Error loading cached A-share stock list: {e}")
    
    return stock_lists

def save_stock_lists_to_cache(stock_lists: Dict[str, List[str]]):
    """
    Save stock lists to pickle files for caching.
    """
    cache_dir = os.path.dirname(__file__)
    hk_cache_file = os.path.join(cache_dir, 'hk_stock_list.pkl')
    us_cache_file = os.path.join(cache_dir, 'us_stock_list.pkl')
    a_cache_file = os.path.join(cache_dir, 'a_stock_list.pkl')
    
    # Save HK stock list
    if stock_lists['HK']:
        try:
            with open(hk_cache_file, 'wb') as f:
                pickle.dump(stock_lists['HK'], f)
        except Exception as e:
            print(f"Error saving HK stock list to cache: {e}")
    
    # Save US stock list
    if stock_lists['US']:
        try:
            with open(us_cache_file, 'wb') as f:
                pickle.dump(stock_lists['US'], f)
        except Exception as e:
            print(f"Error saving US stock list to cache: {e}")
    
    # Save A-share stock list
    if stock_lists['A']:
        try:
            with open(a_cache_file, 'wb') as f:
                pickle.dump(stock_lists['A'], f)
        except Exception as e:
            print(f"Error saving A-share stock list to cache: {e}")

def get_stock_lists(force_refresh: bool = False) -> Dict[str, List[str]]:
    """
    Get stock lists for HK, US, and A-share markets.
    Uses caching to avoid repeated API calls.
    
    Args:
        force_refresh: If True, force refresh the stock lists from API
    
    Returns:
        Dictionary with 'HK', 'US', and 'A' keys containing stock lists
    """
    if not force_refresh:
        stock_lists = load_cached_stock_lists()
        # If we have both lists cached, return them
        if stock_lists['HK'] and stock_lists['US'] and stock_lists['A']:
            return stock_lists
    
    # Get fresh data from APIs
    print("Fetching stock lists from Akshare APIs...")
    stock_lists = {
        'HK': get_hk_stock_list() if not stock_lists['HK'] else [],
        'US': get_us_stock_list() if not stock_lists['US'] else [],
        'A': get_a_stock_list() if not stock_lists['A'] else []
    }
    
    # Save to cache
    save_stock_lists_to_cache(stock_lists)
    
    print(f"Retrieved {len(stock_lists['HK'])} HK stocks, {len(stock_lists['US'])} US stocks, and {len(stock_lists['A'])} A-share stocks")
    return stock_lists

def random_stock_id(market: Optional[str] = None) -> str:
    """
    Get a random stock ID from HK, US, or A-share markets.
    
    Args:
        market: 'HK' for Hong Kong stocks, 'US' for US stocks, 'A' for A-shares, None for random market
    
    Returns:
        Random stock ID (e.g., '00700' for HK, 'AAPL' for US, or '000001' for A-shares)
    """
    # Get stock lists
    stock_lists = get_stock_lists()
    
    if not stock_lists['HK'] and not stock_lists['US'] and not stock_lists['A']:
        # Fallback to some common stock codes if API fails
        fallback_stocks = {
            'HK': ['00700', '09988', '03690', '02318', '00941'],
            'US': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
            'A': ['000001', '600000', '000002', '600036', '000858']
        }
        stock_lists = fallback_stocks
        print("Using fallback stock lists due to API failure")
    
    # Determine which market to use
    if market is None:
        # Randomly choose between HK, US, and A-shares
        available_markets = [m for m in ['HK', 'US', 'A'] if stock_lists[m]]
        if not available_markets:
            return '00700'  # Default fallback
        market = random.choice(available_markets)
    elif market not in stock_lists or not stock_lists[market]:
        # If requested market is not available, try the other ones
        other_markets = [m for m in ['HK', 'US', 'A'] if m != market and stock_lists[m]]
        if other_markets:
            market = random.choice(other_markets)
        else:
            return '00700'  # Default fallback
    
    # Get random stock from the selected market
    stock_list = stock_lists[market]
    if stock_list:
        return random.choice(stock_list)
    else:
        return '00700'  # Default fallback

def random_hk_stock_id() -> str:
    """Get a random Hong Kong stock ID."""
    return random_stock_id('HK')

def random_us_stock_id() -> str:
    """Get a random US stock ID."""
    return random_stock_id('US')

def random_a_stock_id() -> str:
    """Get a random A-share stock ID."""
    return random_stock_id('A')

def clear_us_stocks_cache():
    """
    Clear the US stocks cache files to force a fresh download.
    Useful when you want to refresh the data or if the cache is corrupted.
    """
    cache_dir = os.path.dirname(__file__)
    us_stocks_cache_file = os.path.join(cache_dir, 'us_stocks_data.pkl')
    progress_cache_file = os.path.join(cache_dir, 'us_stocks_progress.pkl')
    
    try:
        if os.path.exists(us_stocks_cache_file):
            os.remove(us_stocks_cache_file)
            print("Cleared US stocks data cache")
        if os.path.exists(progress_cache_file):
            os.remove(progress_cache_file)
            print("Cleared US stocks progress cache")
    except Exception as e:
        print(f"Error clearing cache: {e}")

def get_us_stocks_cache_status():
    """
    Get the status of US stocks cache files.
    Returns information about what's cached and progress.
    """
    cache_dir = os.path.dirname(__file__)
    us_stocks_cache_file = os.path.join(cache_dir, 'us_stocks_data.pkl')
    progress_cache_file = os.path.join(cache_dir, 'us_stocks_progress.pkl')
    
    status = {
        'data_cache_exists': os.path.exists(us_stocks_cache_file),
        'progress_cache_exists': os.path.exists(progress_cache_file),
        'completed_pages': 0,
        'total_records': 0
    }
    
    if status['data_cache_exists']:
        try:
            with open(us_stocks_cache_file, 'rb') as f:
                data = pickle.load(f)
                status['total_records'] = len(data) if hasattr(data, '__len__') else 0
        except Exception as e:
            print(f"Error reading data cache: {e}")
    
    if status['progress_cache_exists']:
        try:
            with open(progress_cache_file, 'rb') as f:
                completed_pages = pickle.load(f)
                status['completed_pages'] = len(completed_pages) if hasattr(completed_pages, '__len__') else 0
        except Exception as e:
            print(f"Error reading progress cache: {e}")
    
    return status

# Example usage and testing
# python -m app.core.api_client.futu.mock_utils
if __name__ == "__main__":
    # Test the functions
    print("Testing US stocks caching system...")
    
    # Check cache status
    cache_status = get_us_stocks_cache_status()
    print(f"Cache status: {cache_status}")
    
    # Get US stock list (this will use the improved caching)
    print("\nFetching US stock list...")
    us_stocks = get_us_stock_list()
    print(f"Retrieved {len(us_stocks)} US stocks")
    
    # Show some examples
    if us_stocks:
        print(f"Sample US stocks: {us_stocks[:10]}")
    
    # Test random selection
    print("\nTesting random stock selection...")
    for i in range(5):
        random_stock = random_stock_id()
        print(f"Random stock {i+1}: {random_stock}")
    
    # Test specific markets
    hk_stock = random_hk_stock_id()
    us_stock = random_us_stock_id()
    a_stock = random_a_stock_id()
    print(f"\nRandom HK stock: {hk_stock}")
    print(f"Random US stock: {us_stock}")
    print(f"Random A-share stock: {a_stock}")
    
    # Uncomment the line below to clear cache if needed
    # clear_us_stocks_cache() 