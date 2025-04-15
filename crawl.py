import csv
import os
import time
import json
from datetime import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def ensure_celsius(temp_str):
    try:
        temp = float(temp_str)
        if temp > 60:  # Very likely Fahrenheit
            temp = (temp - 32) * 5 / 9
        return round(temp, 0)
    except:
        return "N/A"
    
tram = ["hanoi/hai-batrung/ha-noi:-dai-hoc-bách-khoa-cong-parabol-duong-giai-phong-kk",
        "hanoi/thanh-xuan/ha-noi:-cong-vien-ho-dieu-hoa-nhan-chinh-khuat-duy-tien-kk",
        "hanoi/hanoi/minh-khai-bac-tu-liem",
        "tinh-ba-ria-vung-tau/vung-tau/vung-tau:-nga-tu-gieng-nuoc-tp-vung-tau-kk",
        "tinh-hai-duong/hai-duong/hai-duong:-ubnd-tp-hai-duong-106-duong-tran-hung-dao-kk",
        "tinh-thua-thien-hue/hue/thua-thien-hue:-83-duong-hung-vuong-kk",
        "phu-tho/phu-tho/phu-tho:-duong-hung-vuong-tp-viet-tri-kk"
]

#Set up headless browser
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    for i in tram: 

        url = f"https://www.iqair.com/vi/vietnam/{i}"
        driver.get(url)
        time.sleep(10)

        current_time = datetime.now().replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")

        station_name = "Unknown"
        scripts = driver.find_elements(By.XPATH, "//script[@type='application/ld+json']")
        for script in scripts:
            try:
                json_text = script.get_attribute("innerHTML")
                data = json.loads(json_text)
                if isinstance(data, dict) and data.get("@type") == "BreadcrumbList":
                    station_name = data["itemListElement"][-1]["name"]
                    break
            except Exception:
                continue

        # --- Default values ---
        aqi = temp = humidity = wind_speed = "N/A"
        pollutant_data = {
            "PM2.5": "N/A",
            "PM10": "N/A",
            "O3": "N/A",
            "NO2": "N/A",
            "SO2": "N/A",
            "CO": "N/A"
        }

        #Weather components
        items = driver.find_elements(By.CSS_SELECTOR, 'hourly-forecast-item')
        for item in items:
            try:
                timestamp_text = item.find_element(By.CLASS_NAME, 'timestamp').text.strip()
                if timestamp_text == "Bây giờ":
                    aqi = item.find_element(By.CLASS_NAME, 'aqi-chip').text.strip()
                    temp = item.find_element(By.CLASS_NAME, 'temperature').text.strip().replace("°", "")
                    temp = ensure_celsius(temp)
                    humidity = item.find_element(By.CLASS_NAME, 'humidity-value').text.strip().replace("%", "")
                    wind_speed = item.find_element(By.CLASS_NAME, 'wind-speed').text.strip()
                    
                    break
            except Exception as e:
                print("Error parsing forecast:", e)

        #Pollutant components
        pollutant_cards = driver.find_elements(By.CSS_SELECTOR, "air-pollutant-card")
        for card in pollutant_cards:
            try:
                name = card.find_element(By.CLASS_NAME, "card-wrapper-info__title").text.upper()
                value = card.find_element(By.CLASS_NAME, "measurement-wrapper__value").text.strip()
                if "PM2.5" in name:
                    pollutant_data["PM2.5"] = value
                elif "PM10" in name:
                    pollutant_data["PM10"] = value
                elif "O₃" in name:
                    pollutant_data["O3"] = value
                elif "NO₂" in name:
                    pollutant_data["NO2"] = value
                elif "SO₂" in name:
                    pollutant_data["SO2"] = value
                elif "CO" in name:
                    pollutant_data["CO"] = value
            except Exception as e:
                print("⚠️ Error parsing pollutant card:", e)

        #Save file csv
        filename = "air_quality.csv"
        header = ["timestamp", "Địa chỉ", "AQI", "PM2.5", "PM10", "O3", "NO2", "SO2", "CO", "temperature", "humidity", "wind speed"]
        row = [
            current_time, station_name, aqi,
            pollutant_data["PM2.5"],
            pollutant_data["PM10"],
            pollutant_data["O3"],
            pollutant_data["NO2"],
            pollutant_data["SO2"],
            pollutant_data["CO"],
            temp, humidity, wind_speed
        ]

        file_exists = os.path.isfile(filename)
        with open(filename, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(header)
            writer.writerow(row)
finally:
    driver.quit()
