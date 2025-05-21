from pydantic import BaseModel


class AddressBase(BaseModel):
    city: str
    street: str


class AddressCreate(AddressBase):
    pass


class AddressResponse(AddressBase):
    id: int

    class Config:
        from_attributes = True


# Разрешаем forward references
AddressCreate.model_rebuild()
AddressResponse.model_rebuild()
