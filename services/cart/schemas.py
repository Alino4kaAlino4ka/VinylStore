from pydantic import BaseModel, Field
from typing import List

# ====================================================================
# Input DTOs
# ====================================================================

class CartItemIn(BaseModel):
    """
    Элемент корзины, получаемый в запросе.
    """
    vinyl_id: int = Field(..., gt=0, description="Уникальный идентификатор виниловой пластинки")
    quantity: int = Field(..., gt=0, description="Количество экземпляров")

class CartIn(BaseModel):
    """
    Входная DTO для расчета корзины.
    """
    items: List[CartItemIn]

# ====================================================================
# Output DTOs
# ====================================================================

class VinylRecordDetails(BaseModel):
    """
    Информация о товаре, возвращаемая в ответе.
    """
    id: int
    title: str
    price: float

class CartItemOut(BaseModel):
    """
    Полная информация о товаре в корзине.
    """
    vinyl_record: VinylRecordDetails
    quantity: int

class CartOut(BaseModel):
    """
    Итоговый ответ с рассчитанной корзиной.
    """
    items: List[CartItemOut]
    total_price: float = Field(..., description="Итоговая стоимость всей корзины")
