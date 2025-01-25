from pydantic import Field, BaseModel


class SendMessageRequest(BaseModel):
    user_id: str
    message: str = Field(max_length=1000)
