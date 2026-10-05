from pydantic import BaseModel



class RedisRequest(BaseModel):
    username:str