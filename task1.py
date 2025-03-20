from fastapi import FastAPI, HTTPException
import requests
from typing import List, Dict, Union
import random

app = FastAPI()


data_sources = {
    "prime": "http://20.244.56.144/test/primes",
    "fibonacci": "http://20.244.56.144/test/fibo",
    "even": "http://20.244.56.144/test/even",
    "random": "http://20.244.56.144/test/rand"
}


max_window_size = 10

data_buffer: List[Union[int, float]] = []

def generate_random_number():
    return random.randint(1, 100)


@app.get("/analyze")  #
def analyze_data(source: str):  
    
    if source not in data_sources:
        raise HTTPException(status_code=400, detail="Invalid data source specified")

    try:
        
        response = requests.get(data_sources[source], timeout=0.6)  
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Failed to retrieve data: {e}")

    try:
        raw_data = response.json()
        if isinstance(raw_data, list):
            extracted_numbers = list(set(raw_data))
        elif isinstance(raw_data, dict) and "numbers" in raw_data:
            extracted_numbers = list(set(raw_data["numbers"]))
        else:
            raise ValueError("Unexpected data format received")

    except (ValueError, AttributeError, TypeError) as e:
        raise HTTPException(status_code=400, detail=f"Error processing received data: {e}")

    
    valid_numbers: List[Union[int, float]] = []
    for item in extracted_numbers:
        if isinstance(item, (int, float)) and item >= 0:
            valid_numbers.append(item)

    if not valid_numbers:
        raise HTTPException(status_code=400, detail="No valid numerical data found")

    
    global data_buffer
    data_buffer.extend(valid_numbers)
    data_buffer = list(set(data_buffer))  

    
    if len(data_buffer) > max_window_size:
        data_buffer = data_buffer[-max_window_size:]

    
    average = sum(data_buffer) / len(data_buffer)

    
    return {
        "previousBufferState": data_buffer[:-len(valid_numbers)] if len(data_buffer) > len(valid_numbers) else [],
        "currentBufferState": data_buffer,
        "receivedNumbers": valid_numbers,
        "calculatedAverage": round(average,2)
        
    }