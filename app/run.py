import uvicorn
from load_env import HOST, PORT, DEBUG




if __name__ == "__main__":
    uvicorn.run("app:app", host=HOST, port=int(PORT), reload=DEBUG)
