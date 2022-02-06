from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import data_scrapping
from managers.log_manager import LogManager

app = FastAPI()
LogManager.setup()
app.include_router(data_scrapping.router)

# List of domains from which we have to enable cors requests
origins = ["*"]
# List of methods like post, get etc. in which we have to enable cors requests
methods = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"data": "Welcome to Stock Picker API. You can find more info about this api by contacting "
                    "me at github.com/platoputhur"}


