import uvicorn
from config import settings

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload_dirs=["/web_drive/app"],
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
    )
