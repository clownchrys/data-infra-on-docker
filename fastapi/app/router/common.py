import os, signal, psutil
from fastapi import APIRouter

router = APIRouter(
    prefix="/common",
    tags=["common"]
)

@router.get("/")
async def status():
    return "OK"

@router.get("/server_info")
async def server_info():
    info = {
        "server": "dev"
    }
    print(f"server_info: {info}")
    return info

@router.get(
    path="/restart",
    description="FastAPI 서버의 워커 프로세스 재시작",
)
async def restart():
    try:
        parent = psutil.Process(os.getppid())
    except psutil.NoSuchProcess:
        print("Cannot find parent process...")
        return False

    children  = parent.children(recursive=True)
    for p in children:
        p.send_signal(signal.SIGINT)
    return True