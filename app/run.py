import uvicorn
from config import settings

if __name__ == "__main__":
    uvicorn.run("app:app", reload_dirs=["/web_drive/app"], ost=settings.app_host, port=int(settings.app_host), reload=settings.app_debug)
