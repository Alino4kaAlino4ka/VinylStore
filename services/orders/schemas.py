from pydantic import BaseModel, Field
from typing import List
import datetime

# ====================================================================
# Input DTOs
# ====================================================================

class OrderItemIn(BaseModel):
    """
    Сырой элемент для создания заказа.
    """
    vinyl_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)

class OrderIn(BaseModel):
    """
    Входная DTO для создания заказа.
    """
    items: List[OrderItemIn]

# ====================================================================
# Output DTOs
# ====================================================================

class OrderItemOut(BaseModel):
    """
    Детализация товара в созданном заказе.
    """
    id: int
    vinyl_id: int
    quantity: int
    price_at_purchase: float

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    """
    Итоговый ответ с информацией о созданном заказе.
    """
    id: int
    created_at: datetime.datetime
    total_price: float
    items: List[OrderItemOut]

    class Config:
        from_attributes = True
