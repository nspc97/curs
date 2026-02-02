import requests
import xml.etree.ElementTree as ET
import json
import datetime
import time
import re
from bs4 import BeautifulSoup

# Use a real user agent
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

BNM_URL = "https://www.bnm.md/en/official_exchange_rates?get_xml=1"
MICB_URL = "https://www.micb.md/"
OTP_URL = "https://otpbank.md/"
EXIM_URL = "https://eximbank.md/"
FINCOM_URL = "https://fincombank.com/"

ECB_URL = "https://ecb.md/ru"
PROCREDIT_URL = "https://www.procreditbank.md/ru"

def get_bnm_rates():
    """Fetches official rates from BNM XML"""
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    url = f"{BNM_URL}&date={today}"
    
    try:
        print(f"Fetching BNM rates from {url}...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        rates = {"mdl": 1.0}
        
        for valute in root.findall('Valute'):
            char_code = valute.find('CharCode').text.lower()
            nominal = float(valute.find('Nominal').text)
            value = float(valute.find('Value').text)
            
            # Normalize to 1 unit
            rate_per_unit = value / nominal
            rates[char_code] = rate_per_unit

        return {
            "name": "Banca Națională (BNM)",
            "type": "official",
            "rates": rates
        }

    except Exception as e:
        print(f"Error fetching BNM rates: {e}")
        return None

def get_curs_md_rates(bank_slug, bank_display_name):
    """Fetches rates from curs.md for a specific bank"""
    url = f"https://www.curs.md/ru/office/{bank_slug}"
    print(f"Fetching {bank_display_name} rates from {url}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        table = soup.select_one('table.table-hover')
        if not table:
            # Fallback for dynamic layout or error
            return None
        
        rates = {}
        rows = table.find_all('tr')
        # Skip header
        for tr in rows[1:]: 
            tds = tr.find_all('td')
            if len(tds) < 5:
                continue
            
            # Structure: 0:Code, 1:Name, 2:Nominal, 3:Buy, 4:Sell
            code_text = tds[0].get_text(strip=True).upper()
            code = None
            if code_text in ['EUR', 'USD', 'RON', 'GBP', 'UAH', 'RUB', 'CHF']:
                code = code_text.lower()
            
            if code:
                try:
                    buy_text = tds[3].get_text(strip=True).replace(',', '.')
                    sell_text = tds[4].get_text(strip=True).replace(',', '.')
                    
                    # Curs.md sometimes has empty strings or dashes
                    if not buy_text or not sell_text or buy_text == '-' or sell_text == '-':
                        continue

                    buy = float(buy_text)
                    sell = float(sell_text)
                    rates[code] = {"buy": buy, "sell": sell}
                except:
                    continue
        
        if rates:
             return {
                "name": bank_display_name,
                "type": "commercial",
                "rates": rates
            }
        return None
    except Exception as e:
        print(f"Error fetching {bank_display_name}: {e}")
        return None

def get_ecb_rates():
    """Fetches rates from EuroCreditBank (Official)"""
    print(f"Fetching EuroCreditBank rates from {ECB_URL}...")
    try:
        response = requests.get(ECB_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        container = soup.select_one('#fast-calculators .sector-1')
        if not container:
            return None
        
        # The structure is seemingly flat divs or spans? 
        # Dump showed: EUR|19.90|20.17...
        # Let's interact with children
        
        # Based on dump, it seems to be text content separated? 
        # Actually proper HTML parsing is safer.
        # Assuming .currname, .currval classes (from Subagent analysis)
        
        rates = {}
        # Let's iterate through .exchange-row or similar if it exists, OR
        # just find all elements with known currency names and next siblings.
        
        # Refing parsing based on generic strategy:
        # Find all text nodes or elements containing "EUR", "USD"
        
        # Let's try to find the currency name elements
        divs = container.find_all('div')
        # Iterate and look for currency codes
        
        current_code = None
        vals = []
        
        # Parse text content of container split by whitespace might be easier if structure is flat text
        # But let's try classes first if valid. 
        # Re-reading subagent: "Uses a div-based grid... .currname, .currval"
        
        curr_names = container.find_all(class_='currname')
        for name_el in curr_names:
            code_text = name_el.get_text(strip=True).upper()
            code = None
            if 'EUR' in code_text: code = 'eur'
            elif 'USD' in code_text: code = 'usd'
            elif 'RON' in code_text: code = 'ron'
            elif 'GBP' in code_text: code = 'gbp'
            elif 'RUB' in code_text: code = 'rub'
            elif 'CHF' in code_text: code = 'chf'
            
            if code:
                # The values are likely valid next siblings with class 'currval'
                # But DOM structure might be messy.
                # Let's look at next siblings until we find numbers.
                
                siblings = name_el.find_next_siblings(class_='currval')
                if len(siblings) >= 2:
                    try:
                        buy = float(siblings[0].get_text(strip=True).replace(',', '.'))
                        sell = float(siblings[1].get_text(strip=True).replace(',', '.'))
                        rates[code] = {"buy": buy, "sell": sell}
                    except:
                        pass
        
        if rates:
             return {
                "name": "EuroCreditBank",
                "type": "commercial",
                "rates": rates
            }
        return None
    except Exception as e:
        print(f"Error fetching EuroCreditBank: {e}")
        return None

def get_procredit_rates():
    """Fetches rates from ProCredit Bank (Official)"""
    print(f"Fetching ProCredit Bank rates from {PROCREDIT_URL}...")
    try:
        response = requests.get(PROCREDIT_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        table = soup.select_one('#exchange-rates-table')
        if not table:
            return None
            
        rates = {}
        # Iterate all rows, look for data
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            # Need at least 3 cols: Code, Buy, Sell
            # The structure for data rows is usually: Valuta, Buy, Sell, NBM
            if len(tds) >= 3:
                code_text = tds[0].get_text(strip=True).upper()
                code = None
                if code_text in ['EUR', 'USD', 'RON', 'GBP', 'UAH', 'RUB', 'CHF']:
                    code = code_text.lower()
                
                if code:
                    try:
                        buy_str = tds[1].get_text(strip=True).replace(',', '.')
                        sell_str = tds[2].get_text(strip=True).replace(',', '.')
                        
                        if '---' in buy_str or '---' in sell_str:
                            continue
                            
                        buy = float(buy_str)
                        sell = float(sell_str)
                        
                        # Store (overwrite if duplicates found later - usually later rows are Card/etc)
                        # Actually we prefer later rows if earlier were empty (handled by check)
                        # If earlier had data and later has data... maybe stick with first? 
                        # ProCredit often puts "Cashless" first then "Card". Cashless is usually what we want if available.
                        # But dump showed Cashless was empty "---".
                        # So we populate.
                        rates[code] = {"buy": buy, "sell": sell}
                    except:
                        continue
                        
        if rates:
             return {
                "name": "ProCredit Bank",
                "type": "commercial",
                "rates": rates
            }
        return None
    except Exception as e:
        print(f"Error fetching ProCredit Bank: {e}")
        return None

def get_otp_rates():
    """Fetches rates from OTP Bank"""
    print(f"Fetching OTP rates from {OTP_URL}...")
    try:
        response = requests.get(OTP_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        rates = {}
        # Strategy: Find any table containing EUR and USD
        tables = soup.find_all('table')
        target_table = None
        for t in tables:
            t_text = t.get_text()
            if 'EUR' in t_text and 'USD' in t_text:
                target_table = t
                break
        
        if not target_table:
            return None

        # Iterate rows
        for tr in target_table.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) < 3:
                continue
            
            # Col 0 has currency name/code
            code_text = tds[0].get_text(strip=True).upper()
            
            # Check for currency
            code = None
            if 'EUR' in code_text: code = 'eur'
            elif 'USD' in code_text: code = 'usd'
            elif 'RON' in code_text: code = 'ron'
            elif 'GBP' in code_text: code = 'gbp'
            elif 'UAH' in code_text: code = 'uah'
            elif 'RUB' in code_text: code = 'rub'
            
            if code:
                try:
                    buy = float(tds[1].get_text(strip=True).replace(',', '.'))
                    sell = float(tds[2].get_text(strip=True).replace(',', '.'))
                    rates[code] = {"buy": buy, "sell": sell}
                except:
                    continue
                    
        if rates:
            return {
                "name": "OTP Bank",
                "type": "commercial",
                "rates": rates
            }
        return None
    except Exception as e:
        print(f"Error fetching OTP rates: {e}")
        return None

def get_exim_rates():
    """Fetches rates from Eximbank"""
    print(f"Fetching Eximbank rates from {EXIM_URL}...")
    try:
        response = requests.get(EXIM_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        container = soup.select_one('div.static__table')
        if not container:
            return None
        
        target_table = container.find('table')
        if not target_table:
            return None
            
        rates = {}
        for tr in target_table.find_all('tr'):
            tds = tr.find_all('td')
            # Expecting > 3 cols. 
            # 0: Name/Code, 1: Buy, 2: Sell
            if len(tds) >= 3:
                text0 = tds[0].get_text(strip=True).upper()
                code = None
                if '(EUR)' in text0: code = 'eur'
                elif '(USD)' in text0: code = 'usd'
                elif '(RON)' in text0: code = 'ron'
                elif '(GBP)' in text0: code = 'gbp'
                elif '(RUB)' in text0: code = 'rub'
                elif '(UAH)' in text0: code = 'uah'
                
                if code:
                    try:
                        buy = float(tds[1].get_text(strip=True).replace(',', '.'))
                        sell = float(tds[2].get_text(strip=True).replace(',', '.'))
                        rates[code] = {"buy": buy, "sell": sell}
                    except:
                        continue
        
        if rates:
             return {
                "name": "Eximbank",
                "type": "commercial",
                "rates": rates
            }
        return None
    except Exception as e:
        print(f"Error fetching Eximbank rates: {e}")
        return None

def get_fincom_rates():
    """Fetches rates from FinComBank"""
    print(f"Fetching FinComBank rates from {FINCOM_URL}...")
    try:
        response = requests.get(FINCOM_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        table = soup.select_one('table.exchange-rates__table')
        if not table:
            return None
            
        rates = {}
        rows = table.find_all('tr', class_='exchange-rates__table-row')
        for tr in rows:
            tds = tr.find_all('td')
            # 0: Valuta, 1: Buy, 2: Sell
            if len(tds) >= 3:
                code_text = tds[0].get_text(strip=True).upper()
                
                # Direct match expected usually
                code = None
                if code_text in ['EUR', 'USD', 'RON', 'GBP', 'UAH', 'RUB']:
                    code = code_text.lower()
                
                if code:
                    try:
                        buy = float(tds[1].get_text(strip=True).replace(',', '.'))
                        sell = float(tds[2].get_text(strip=True).replace(',', '.'))
                        rates[code] = {"buy": buy, "sell": sell}
                    except:
                        continue
                        
        if rates:
             return {
                "name": "FinComBank",
                "type": "commercial",
                "rates": rates
            }
        return None
    except Exception as e:
        print(f"Error fetching FinComBank rates: {e}")
        return None

def get_micb_rates():
    """Fetches commercial rates from Moldindconbank (MICB)"""
    print(f"Fetching MICB rates from {MICB_URL}...")
    try:
        response = requests.get(MICB_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Locate container
        # We rely on finding 'buy_XXX' and 'sell_XXX' classes directly
        # Example: <div class="col buy_EUR" ...>
        
        rates = {}
        
        # Find all elements that have a class starting with 'buy_'
        # We can regex the class name
        buy_elements = soup.find_all('div', class_=re.compile(r'\bbuy_[A-Z]{3}\b'))
        
        for el in buy_elements:
            # Extract currency code from class name (e.g., "buy_EUR")
            classes = el.get('class', [])
            currency_code = None
            for cls in classes:
                if cls.startswith('buy_') and len(cls) == 7:
                    currency_code = cls.split('_')[1].lower()
                    break
            
            if not currency_code:
                continue
                
            # Get Buy Value
            try:
                buy_val_text = el.get_text(strip=True).replace(',', '.')
                buy_val = float(buy_val_text)
            except:
                continue
                
            # Find corresponding Sell Value
            # Usually in the same row, sibling with class 'sell_CODE'
            # Or just search globally like we did for buy
            sell_el = soup.find('div', class_=f'sell_{currency_code.upper()}')
            if sell_el:
                try:
                    sell_val_text = sell_el.get_text(strip=True).replace(',', '.')
                    sell_val = float(sell_val_text)
                    
                    rates[currency_code] = {
                        "buy": buy_val,
                        "sell": sell_val
                    }
                except:
                    pass

        if rates:
             return {
                "name": "Moldindconbank",
                "type": "commercial",
                "rates": rates
            }
        
        return None

    except Exception as e:
        print(f"Error fetching MICB rates: {e}")
        return None

def save_to_json(data, filename="rates.json"):
    if data:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Курсы успешно обновлены в файле {filename}")
    else:
        print("Не удалось получить данные для сохранения.")

if __name__ == "__main__":
    combined_data = {
        "date": datetime.datetime.now().strftime("%d.%m.%Y"),
        "timestamp": int(datetime.datetime.now().timestamp() * 1000),
        "sources": {}
    }
    
    # 1. Get BNM
    bnm_data = get_bnm_rates()
    if bnm_data:
        combined_data["sources"]["bnm"] = bnm_data
    
    # 2. Get MICB
    micb_data = get_micb_rates()
    if micb_data:
        combined_data["sources"]["micb"] = micb_data

    # 3. Get OTP
    otp_data = get_otp_rates()
    if otp_data:
        combined_data["sources"]["otp"] = otp_data

    # 4. Get Eximbank
    exim_data = get_exim_rates()
    if exim_data:
        combined_data["sources"]["exim"] = exim_data

    # 5. Get FinComBank
    fincom_data = get_fincom_rates()
    if fincom_data:
        combined_data["sources"]["fincom"] = fincom_data
        
    # 6. Get MAIB (curs.md)
    maib_data = get_curs_md_rates("maib", "MAIB")
    if maib_data:
        combined_data["sources"]["maib"] = maib_data

    # 7. Get Victoriabank (curs.md)
    victoria_data = get_curs_md_rates("victoriabank", "Victoriabank")
    if victoria_data:
        combined_data["sources"]["victoria"] = victoria_data

    # 8. Get Comertbank (curs.md - official site protected)
    comert_data = get_curs_md_rates("comertbank", "Comerțbank")
    if comert_data:
        combined_data["sources"]["comert"] = comert_data

    # 9. Get Energbank (curs.md - official site protected)
    energ_data = get_curs_md_rates("energbank", "Energbank")
    if energ_data:
        combined_data["sources"]["energ"] = energ_data

    # 10. Get EuroCreditBank (Official)
    ecb_data = get_ecb_rates()
    if ecb_data:
        combined_data["sources"]["ecb"] = ecb_data

    # 11. Get ProCredit Bank (Official)
    procredit_data = get_procredit_rates()
    if procredit_data:
        combined_data["sources"]["procredit"] = procredit_data

    # Save
    save_to_json(combined_data)
