"""API 路由注册"""
from fastapi import APIRouter

from app.api.v1 import (
    contributions,
    install,
    monitor,
    publish,
    reviews,
    scan,
    search,
    skills,
    users,
)

api_router = APIRouter()

v1_router = APIRouter(prefix="/v1", tags=["v1"])
v1_router.include_router(skills.router, prefix="/skills", tags=["skills"])
v1_router.include_router(users.router, prefix="/users", tags=["users"])
v1_router.include_router(search.router, prefix="/search", tags=["search"])
v1_router.include_router(install.router, prefix="/install", tags=["install"])
v1_router.include_router(scan.router, prefix="/scan", tags=["scan"])
v1_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
v1_router.include_router(monitor.router, prefix="/monitor", tags=["monitor"])
v1_router.include_router(
    contributions.router, prefix="/contributions", tags=["contributions"]
)
v1_router.include_router(publish.router, prefix="/publish", tags=["publish"])

api_router.include_router(v1_router)
