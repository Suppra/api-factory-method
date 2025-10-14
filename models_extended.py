"""
Modelos de datos extendidos para el patrón Builder con Director.
Incluye los nuevos atributos obligatorios y opcionales para VM, Network y Storage.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from enum import Enum

# ============= ENUMERACIONES PARA TIPOS DE VM =============

class VMType(str, Enum):
    STANDARD = "standard"
    MEMORY_OPTIMIZED = "memory_optimized" 
    COMPUTE_OPTIMIZED = "compute_optimized"

class Provider(str, Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ONPREMISE = "onpremise"

# ============= MODELOS EXTENDIDOS PARA RECURSOS =============

class VirtualMachineConfig(BaseModel):
    """Configuración extendida para máquina virtual"""
    # Parámetros obligatorios
    provider: Provider
    vcpus: int = Field(gt=0, description="Núcleos virtuales asignados")
    memory_gb: int = Field(gt=0, description="Memoria RAM asignada en GB")
    
    # Parámetros opcionales
    memory_optimization: Optional[bool] = False
    disk_optimization: Optional[bool] = False
    key_pair_name: Optional[str] = "default-key"
    
    # Parámetros específicos del proveedor (heredados del modelo anterior)
    instance_type: Optional[str] = None
    region: Optional[str] = None
    ami: Optional[str] = None
    size: Optional[str] = None
    resource_group: Optional[str] = None
    image: Optional[str] = None
    machine_type: Optional[str] = None
    zone: Optional[str] = None
    project: Optional[str] = None
    cpu: Optional[int] = None
    ram: Optional[int] = None
    hypervisor: Optional[str] = None

class NetworkConfig(BaseModel):
    """Configuración extendida para red"""
    # Parámetros obligatorios
    region: str = Field(description="Región de red")
    
    # Parámetros opcionales
    firewall_rules: Optional[List[str]] = Field(default=["SSH"], description="Reglas de seguridad")
    public_ip: Optional[bool] = True
    
    # Parámetros específicos del proveedor (heredados)
    vpc_id: Optional[str] = None
    subnet: Optional[str] = None
    security_group: Optional[str] = None
    virtual_network: Optional[str] = None
    subnet_name: Optional[str] = None
    network_security_group: Optional[str] = None
    network_name: Optional[str] = None
    subnetwork_name: Optional[str] = None
    firewall_tag: Optional[str] = None
    physical_interface: Optional[str] = None
    vlan_id: Optional[int] = None
    firewall_policy: Optional[str] = None

class StorageConfig(BaseModel):
    """Configuración extendida para almacenamiento"""
    # Parámetros obligatorios
    region: str = Field(description="Región del almacenamiento")
    size_gb: int = Field(gt=0, description="Tamaño en GB")
    
    # Parámetros opcionales
    iops: Optional[int] = Field(default=3000, description="Rendimiento del disco")
    
    # Parámetros específicos del proveedor (heredados)
    volume_type: Optional[str] = None
    encrypted: Optional[bool] = True
    disk_sku: Optional[str] = None
    managed_disk: Optional[bool] = True
    disk_type: Optional[str] = None
    auto_delete: Optional[bool] = True
    storage_pool: Optional[str] = None
    raid_level: Optional[str] = None

# ============= MODELOS PARA BUILDER PATTERN =============

class VMSpecification(BaseModel):
    """Especificación completa de una VM con sus recursos"""
    vm_type: VMType
    provider: Provider
    region: str
    vm_config: VirtualMachineConfig
    network_config: NetworkConfig
    storage_config: StorageConfig

class BuilderRequest(BaseModel):
    """Request para el patrón Builder con Director"""
    vm_type: VMType
    provider: Provider
    region: str
    
    # Configuraciones opcionales que override las del Director
    custom_vm_config: Optional[Dict[str, Any]] = None
    custom_network_config: Optional[Dict[str, Any]] = None
    custom_storage_config: Optional[Dict[str, Any]] = None

class BuilderResponse(BaseModel):
    """Response del patrón Builder"""
    success: bool
    vm_specification: Optional[VMSpecification] = None
    created_resources: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True

# ============= MODELOS ORIGINALES (MANTENIDOS PARA COMPATIBILIDAD) =============

class VMRequest(BaseModel):
    provider: str
    params: dict

class VMResponse(BaseModel):
    success: bool
    vm_id: str = None
    error: str = None

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
    resources: Optional[List[ResourceInfo]] = None
    error: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True