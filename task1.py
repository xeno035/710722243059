from fastapi import FastAPI, HTTPException
import requests
from typing import List, Dict, Union

app = FastAPI()


JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzQyNDQ5Mzk3LCJpYXQiOjE3NDI0NDkwOTcsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6IjI1NjljMDJiLTU2NzMtNGM3MS05ODk3LTIyZTFkZmJjNTlhNyIsInN1YiI6IjIyYWQwNTlAZHJuZ3BpdC5hYy5pbiJ9LCJjb21wYW55TmFtZSI6IkRyLk5HUElUIiwiY2xpZW50SUQiOiIyNTY5YzAyYi01NjczLTRjNzEtOTg5Ny0yMmUxZGZiYzU5YTciLCJjbGllbnRTZWNyZXQiOiJUWklzQnBYRVFTcXJvZmJsIiwib3duZXJOYW1lIjoiVmlzaG51IEsiLCJvd25lckVtYWlsIjoiMjJhZDA1OUBkcm5ncGl0LmFjLmluIiwicm9sbE5vIjoiNzEwNzIyMjQzMDU5In0.xHtxZIjFTCmUkUZB34ITp_zWT25g1StbjA6kx8O-T-A"
server_url = {
    "p": "http://20.244.56.144/test/primes",
    "f": "http://20.244.56.144/test/fibo",
    "e": "http://20.244.56.144/test/even",
    "r": "http://20.244.56.144/test/rand"
}

window_size = 10
window: List[Union[int, float]] = []


@app.get("/calculate")
def calculate_avg(source: str):
    if source not in server_url:
        raise HTTPException(status_code=400, detail="Invalid source")

    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}"  # Add the JWT to the headers
    }

    try:
        response = requests.get(server_url[source], headers=headers, timeout=0.5)  # Include headers in the request
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Error fetching data: {e}")

    try:
        data = response.json()
        if isinstance(data, list):
            num = list(set(data))
        elif isinstance(data, dict) and "numbers" in data:
            num = list(set(data["numbers"]))
        else:
            raise ValueError("Invalid data format")

    except (ValueError, AttributeError, TypeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid data received: {e}")

    fnum: List[Union[int, float]] = []
    for n in num:
        if isinstance(n, (int, float)) and n >= 0:
            fnum.append(n)

    num = fnum

    if not num:
        raise HTTPException(status_code=400, detail="No valid numbers")

    global window
    window.extend(num)
    window = list(set(window))
    if len(window) > window_size:
        window = window[-window_size:]

    avg = sum(window) / len(window)

    return {
        "windowPrevState": window[:-len(num)] if len(window) > len(num) else [],
        "windowCurrState": window,
        "numbers": num,
        "avg": round(avg,2)
    }
