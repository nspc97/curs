import requests
import xml.etree.ElementTree as ET
import json
import datetime
import os

# URL НБМ (BNM)
# Data parameters will be added dynamically
BNM_URL = "https://www.bnm.md/en/official_exchange_rates?get_xml=1"

def get_bnm_rates():
    # Получаем сегодняшнюю дату в формате dd.mm.yyyy
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    url = f"{BNM_URL}&date={today}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Парсим XML
        root = ET.fromstring(response.content)
        
        # Структура для сохранения
        data = {
            "date": root.attrib.get('Date', today),
            "source": "Banca Națională a Moldovei",
            "rates": {
                "mdl": 1.0 # Базовая валюта
            }
        }
        
        for valute in root.findall('Valute'):
            char_code = valute.find('CharCode').text.lower()
            nominal = float(valute.find('Nominal').text)
            value = float(valute.find('Value').text)
            
            # Нормализуем курс к 1 единице валюты
            # Если номинал 100 (как у JPY), то value это цена за 100. Нам нужна цена за 1.
            rate_per_unit = value / nominal
            
            # Сохраняем курс (сколько MDL стоит 1 единица этой валюты)
            data["rates"][char_code] = rate_per_unit

        return data

    except Exception as e:
        print(f"Ошибка при обновлении курсов: {e}")
        return None

def save_to_json(data, filename="rates.json"):
    if data:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Курсы успешно обновлены в файле {filename}")
    else:
        print("Не удалось получить данные для сохранения.")

if __name__ == "__main__":
    rates_data = get_bnm_rates()
    save_to_json(rates_data)
