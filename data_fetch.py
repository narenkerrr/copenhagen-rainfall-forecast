"""
data_fetch.py
-------------
Pulls 10 years of daily weather data for Copenhagen from Open-Meteo,
including hourly precipitation to extract extreme-event proxies.
"""

import requests
import pandas as pd

LATITUDE, LONGITUDE = 55.6761, 12.5683
START_DATE = "2015-01-01"
END_DATE = "2024-12-31"

def fetch_daily():
    """Fetch daily aggregates from Open-Meteo."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "precipitation_sum",
            "windspeed_10m_max",
            "windgusts_10m_max",
            "winddirection_10m_dominant",
            "surface_pressure_mean",
            "relative_humidity_2m_mean",
            "cloudcover_mean",
        ]),
        "timezone": "Europe/Copenhagen",
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame({
        "date": pd.to_datetime(data["daily"]["time"]),
        "temperature_2m_max": data["daily"]["temperature_2m_max"],
        "temperature_2m_min": data["daily"]["temperature_2m_min"],
        "temperature_2m_mean": data["daily"]["temperature_2m_mean"],
        "precipitation_sum": data["daily"]["precipitation_sum"],
        "windspeed_10m_max": data["daily"]["windspeed_10m_max"],
        "windgusts_10m_max": data["daily"]["windgusts_10m_max"],
        "winddirection_10m_dominant": data["daily"]["winddirection_10m_dominant"],
        "surface_pressure_mean": data["daily"]["surface_pressure_mean"],
        "relative_humidity_2m_mean": data["daily"]["relative_humidity_2m_mean"],
        "cloudcover_mean": data["daily"]["cloudcover_mean"],
    })
    return df

def fetch_hourly():
    """Fetch hourly precipitation to extract max-1-hour."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": "precipitation",
        "timezone": "Europe/Copenhagen",
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    df_h = pd.DataFrame({
        "datetime": pd.to_datetime(data["hourly"]["time"]),
        "precipitation": data["hourly"]["precipitation"],
    })
    df_h["date"] = df_h["datetime"].dt.date
    hourly_max = df_h.groupby("date")["precipitation"].max().reset_index()
    hourly_max.columns = ["date", "precip_max_1h"]
    hourly_max["date"] = pd.to_datetime(hourly_max["date"])
    return hourly_max

if __name__ == "__main__":
    print("Fetching daily data...")
    df_daily = fetch_daily()
    print(f"  {len(df_daily)} days")
    
    print("Fetching hourly data for max-1-hour precipitation...")
    df_hourly = fetch_hourly()
    print(f"  {len(df_hourly)} days with hourly data")
    
    df_daily = df_daily.merge(df_hourly, on="date", how="left")
    df_daily.to_csv("copenhagen_daily_weather.csv", index=False)
    print(f"Saved to copenhagen_daily_weather.csv")
