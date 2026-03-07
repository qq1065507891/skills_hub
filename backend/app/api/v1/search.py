"""搜索相关 API"""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.models import Skill
from app.schemas.skill import (
    CategoriesResponse,
    SearchResponse,
    SkillResponse,
    TagsResponse,
)
from app.services.search_service import SearchService

router = APIRouter()


@router.get("/", response_model=SearchResponse)
def search_skills(
    q: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    min_rating: Optional[float] = None,
    sort_by: str = "relevance",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """搜索技能"""
    if tags and len(tags) == 1 and "," in tags[0]:
        tags = [tag.strip() for tag in tags[0].split(",") if tag.strip()]

    skip = (page - 1) * page_size

    skills, total = SearchService.search_skills(
        db=db,
        query=q,
        category=category,
        tags=tags,
        min_rating=min_rating,
        sort_by=sort_by,
        skip=skip,
        limit=page_size,
    )

    total_pages = 0
    if total > 0:
        total_pages = (total + page_size - 1) // page_size

    return SearchResponse(
        items=skills,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/categories", response_model=CategoriesResponse)
def get_categories(db: Session = Depends(get_db)):
    """获取所有分类列表"""
    categories = SearchService.get_categories(db)
    return CategoriesResponse(categories=categories)


@router.get("/tags", response_model=TagsResponse)
def get_tags(db: Session = Depends(get_db)):
    """获取所有标签列表"""
    tags = SearchService.get_all_tags(db)
    return TagsResponse(tags=tags)


@router.get("/simple", response_model=List[SkillResponse])
def simple_search_skills(
    q: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """简单搜索"""
    query = db.query(Skill)

    if q:
        query = query.filter(Skill.name.contains(q) | Skill.description.contains(q))

    if category:
        query = query.filter(Skill.category == category)

    return query.all()
