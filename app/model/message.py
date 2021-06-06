from pydantic import BaseModel

class Message(BaseModel):
    type: str
    content: str
    sender_name : str
    reciever_name : str
    sender_image : str
