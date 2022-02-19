from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import data_scraping, short_list
from managers.log_manager import LogManager

app = FastAPI()
LogManager.setup()
app.include_router(data_scraping.router)
app.include_router(short_list.router)

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
    return {"data": "This is a private API. You can find more info about this api by contacting "
                    "me at github.com/platoputhur"}


