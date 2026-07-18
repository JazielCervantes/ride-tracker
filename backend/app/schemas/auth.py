from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    # Límites holgados para credenciales reales; frenan payloads gigantes
    # antes de llegar a bcrypt (que además trunca a 72 bytes).
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}
