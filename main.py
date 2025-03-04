from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import apidata
from auth_manager import _xuid

app = FastAPI()


origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/servicerecord/careerrank')
async def get_career_rank_data():
    try:
        url = "https://gamecms-hacs.svc.halowaypoint.com/hi/Progression/file/RewardTracks/CareerRanks/careerRank1.json"
        data = apidata.request_data('GET', url)
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "failure", "error": e}
    
@app.get("/servicerecord/{gamertag}")
async def get_service_record(gamertag : str):
    try:
        data = apidata.request_data('GET', f"https://halostats.svc.halowaypoint.com/hi/players/{gamertag}/Matchmade/servicerecord")
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "failure", "error": e}
    
@app.get('/servicerecord/careerrank/{gamertag}')
async def get_career_rank(gamertag: str):
    try:
        xuid = _xuid(gamertag)['people'][0]['xuid']
        data = apidata.request_data('GET', f'https://economy.svc.halowaypoint.com/hi/players/xuid({xuid})/rewardtracks/careerranks/careerrank1')
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "failure", "error": e}
    
@app.get('/servicerecord/careerrank/images')
async def get_career_rank_info():
    try:
        data = apidata.request_data('GET', 'https://gamecms-hacs.svc.halowaypoint.com/hi/Progression/file/RewardTracks/CareerRanks/careerRank1.json')
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "failure", "error": e}
    
@app.get('/xbox/player/{gamertag}/xuid')
async def get_xuid(gamertag: str):
    try:
        data = _xuid(gamertag)
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "failure", "error": e}
    

@app.get('/halo/clearence/')
async def get_clearence():
    try:
        data = apidata.request_data('GET', "https://settings.svc.halowaypoint.com/oban/flight-configurations/titles/hi/audiences/RETAIL/players/xuid(2535437387044548)/active?sandbox=UNUSED&build=210921.22.01.10.1706-0")
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "failure", "error": e}
    

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    

# IMAGE_FOLDER = 'media'
# LANGUAGE = 'en-us'
# USER_AGENT = 'OpenSpartan.Career/1.0'
# CAREER_ENDPOINT = 'https://gamecms-hacs.svc.halowaypoint.com/hi/Progression/file/RewardTracks/CareerRanks/careerRank1.json'
# IMAGE_ENDPOINT = 'https://gamecms-hacs.svc.halowaypoint.com/hi/images/file/'
# IMAGE_PREFIX = 'https://assets.den.dev/images/postmedia/halo-infinite-career-ranks/'

