import requests
from datetime import datetime

# API request
def fetch_state_data(state):
    url = "https://waterservices.usgs.gov/nwis/iv/"
    params = {
        "format": "json",
        "stateCd": state,
        "period": "P3D",
        "siteStatus": "all",
        "parameterCd": "00065" 
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.status_code}")
    data = response.json()
    return data

# Loop through the data
def parse_time_series(data):
    site_data = {}
    time_series_list = data['value']['timeSeries']

    for time_stamp in time_series_list:
        site_name = time_stamp['sourceInfo']['siteName']
        site_id = time_stamp['sourceInfo']['siteCode'][0]['value']
        readings = time_stamp['values'][0]['value']
        
        if site_id not in site_data:
            site_data[site_id] = {
                "site_name": site_name,
                "readings": []
            }
        
        sorted_readings = sorted(readings, key=lambda x: x['dateTime']) # sort by timestamp
        for reading in sorted_readings:
            timestamp = reading['dateTime']
            value = float(reading['value'])
            
            site_data[site_id]['readings'].append({
                "timestamp": timestamp,
                "value": value
            })
    return site_data

# Combine data from multiple states for simplicity of parsing
def fetch_and_combine(states):
    combined = {}
    for state in states:
        print(f"Fetching data for {state}")
        data = fetch_state_data(state)
        print("Data fetched successfully :D")
        state_site_data = parse_time_series(data)
        
        for site_id, site_info in state_site_data.items():
            if site_id not in combined:
                combined[site_id] = site_info
            else: # should never happen??? but just in case
                combined[site_id]['readings'].extend(site_info['readings'])
                combined[site_id]['readings'].sort(key=lambda r: r['timestamp'])
    return combined

def find_anomalies(data):
    anomalies = []
    for site_id, site_info in data.items():
        readings = site_info['readings']
        for i in range(1, len(readings)):
            prev = readings[i - 1]['value']
            curr = readings[i]['value']
            if abs(curr - prev) > 5: 
                anomalies.append({
                    "site_id": site_id,
                    "site_name": site_info['site_name'],
                    "timestamp": readings[i]['timestamp'],
                    "prev_value": prev,
                    "curr_value": curr
                })
    return anomalies

if __name__ == "__main__":
    states = ["tx", "ok"]
    combined_data = fetch_and_combine(states)
    anomalies = find_anomalies(combined_data)
    print(f"ANOMALIES FOUND: {len(anomalies)}")
    print("------------------")
    for anomaly in anomalies:
        direction = "JUMP" if anomaly['curr_value'] > anomaly['prev_value'] else "DROP"
        timestamp_str = anomaly['timestamp']
        dt_object = datetime.fromisoformat(timestamp_str)
        timestamp = dt_object.strftime("%B %d, %Y at %-I:%M %p")
        print(f"{direction} in levels found at site {anomaly['site_name']} (site id {anomaly['site_id']}) on {timestamp}: "
              f"{anomaly['prev_value']} -> {anomaly['curr_value']}\n")