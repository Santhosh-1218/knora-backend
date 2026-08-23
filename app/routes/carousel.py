from typing import List
from fastapi import APIRouter, HTTPException, status
from app.repositories.carousel_repository import CarouselRepository
from app.schemas.carousel import CarouselSlideCreate, CarouselSlideUpdate, CarouselSlideResponse
from app.schemas.response import APIResponse

carousel_router = APIRouter(prefix="/api/v1/carousel", tags=["Promotional Carousel"])
admin_carousel_router = APIRouter(prefix="/api/v1/admin/carousel", tags=["Admin Carousel Controller"])
repository = CarouselRepository()


@carousel_router.get("/slides", response_model=APIResponse[List[CarouselSlideResponse]])
async def get_active_carousel_slides():
    """Public endpoint to fetch active promotional carousel slides."""
    slides = await repository.get_active_slides()
    return APIResponse(
        success=True,
        message="Active carousel slides retrieved successfully",
        data=slides
    )


@admin_carousel_router.get("/slides", response_model=APIResponse[List[CarouselSlideResponse]])
async def get_all_carousel_slides_admin():
    """Admin endpoint to fetch all carousel slides including draft/inactive ones."""
    slides = await repository.get_all_slides()
    return APIResponse(
        success=True,
        message="All carousel slides retrieved for admin",
        data=slides
    )


@admin_carousel_router.post("/slides", response_model=APIResponse[CarouselSlideResponse], status_code=status.HTTP_201_CREATED)
async def create_carousel_slide(slide_in: CarouselSlideCreate):
    """Admin endpoint to create a new promotional carousel slide."""
    slide_dict = slide_in.dict(by_alias=True)
    created_slide = await repository.create_slide(slide_dict)
    return APIResponse(
        success=True,
        message="New carousel slide created successfully",
        data=created_slide
    )


@admin_carousel_router.put("/slides/{slide_id}", response_model=APIResponse[CarouselSlideResponse])
async def update_carousel_slide(slide_id: str, slide_in: CarouselSlideUpdate):
    """Admin endpoint to update an existing promotional carousel slide."""
    update_dict = {k: v for k, v in slide_in.dict(by_alias=True).items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    updated_slide = await repository.update_slide(slide_id, update_dict)
    if not updated_slide:
        raise HTTPException(status_code=404, detail="Carousel slide not found")

    return APIResponse(
        success=True,
        message="Carousel slide updated successfully",
        data=updated_slide
    )


@admin_carousel_router.delete("/slides/{slide_id}", response_model=APIResponse[dict])
async def delete_carousel_slide(slide_id: str):
    """Admin endpoint to delete a promotional carousel slide."""
    deleted = await repository.delete_slide(slide_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Carousel slide not found")

    return APIResponse(
        success=True,
        message="Carousel slide deleted successfully",
        data={"id": slide_id}
    )
