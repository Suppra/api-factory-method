from pydantic import BaseModel
from typing import Optional, Dict, Any

# ============= MODELOS ORIGINALES (MANTENIDOS PARA COMPATIBILIDAD) =============

class VMRequest(BaseModel):
    provider: str
    params: dict

class VMResponse(BaseModel):
    success: bool
    vm_id: str = None
    error: str = None

# ============= NUEVOS MODELOS PARA FAMILIAS DE RECURSOS =============

class ResourceFamilyRequest(BaseModel):
    """Modelo para solicitud de aprovisionamiento de familia de recursos"""
    provider: str
    vm_params: dict
    network_params: dict
    storage_params: dict

class ResourceInfo(BaseModel):
    """Información de un recurso creado"""
    resource_id: str
    resource_type: str  # 'network', 'storage', 'vm'
    status: str
    details: Dict[str, Any]

class ResourceFamilyResponse(BaseModel):
    """Respuesta del aprovisionamiento de familia de recursos"""
    success: bool
    provider: Optional[str] = None
    resources: Optional[list[ResourceInfo]] = None
    error: Optional[str] = None
    
    class Config:
        # Permite usar list[ResourceInfo] en lugar de List[ResourceInfo]
        arbitrary_types_allowed = True
