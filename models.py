from pydantic import BaseModel

class VMRequest(BaseModel):
    provider: str
    params: dict

class VMResponse(BaseModel):
    success: bool
    vm_id: str = None
    error: str = None
