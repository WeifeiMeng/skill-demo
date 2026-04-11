from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from docker_manager import create_container, get_containers, stop_container, remove_container, start_container

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/create_env")
def create_env():
    result = create_container()
    return result

@app.get("/containers")
def list_containers():
    return get_containers()

@app.post("/containers/{container_id}/stop")
def stop_container_api(container_id: str):
    return stop_container(container_id)

@app.post("/containers/{container_id}/start")
def start_container_api(container_id: str):
    return start_container(container_id)

@app.post("/containers/{container_id}/remove")
def remove_container_api(container_id: str):
    return remove_container(container_id)