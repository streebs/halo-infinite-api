from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import apidata

app = FastAPI()


origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/servicerecord/{gamertag}")
async def get_service_record(gamertag : str):
    try:
        data = apidata.request_data('GET', f"https://halostats.svc.halowaypoint.com/hi/players/{gamertag}/Matchmade/servicerecord")
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "failure", "error": e}
    
