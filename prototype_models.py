"""
Modelos específicos para el patrón Prototype.
Define las estructuras de datos para requests y responses de templates.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from models_extended import VMSpecification, Provider, VMType


class TemplateCreationRequest(BaseModel):
    """Request para crear VM desde template"""
    template_name: str = Field(..., description="Nombre del template a usar")
    provider: Optional[Provider] = Field(None, description="Proveedor objetivo (override)")
    region: Optional[str] = Field(None, description="Región objetivo (override)")
    
    # Personalizaciones por recurso
    vm_customizations: Optional[Dict[str, Any]] = Field(None, description="Personalizaciones de VM")
    network_customizations: Optional[Dict[str, Any]] = Field(None, description="Personalizaciones de red")
    storage_customizations: Optional[Dict[str, Any]] = Field(None, description="Personalizaciones de almacenamiento")
    
    # Tags adicionales
    additional_tags: Optional[Dict[str, str]] = Field(None, description="Tags adicionales para el template")


class TemplateCreationResponse(BaseModel):
    """Response de creación de VM desde template"""
    success: bool
    template_name: Optional[str] = None
    vm_specification: Optional[VMSpecification] = None
    created_resources: Optional[List[Dict[str, Any]]] = None
    cost_estimate: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


class TemplateRegistrationRequest(BaseModel):
    """Request para registrar nuevo template"""
    template_name: str = Field(..., description="Nombre único del template")
    description: str = Field(..., description="Descripción del template")
    category: str = Field(default="custom", description="Categoría del template")
    
    # Especificación base del template
    vm_specification: VMSpecification = Field(..., description="Especificación de VM del template")
    
    # Metadatos adicionales
    tags: Optional[Dict[str, str]] = Field(None, description="Tags del template")


class TemplateRegistrationResponse(BaseModel):
    """Response de registro de template"""
    success: bool
    template_name: Optional[str] = None
    template_info: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None


class TemplateListResponse(BaseModel):
    """Response de listado de templates"""
    success: bool
    templates: Optional[List[Dict[str, Any]]] = None
    total: Optional[int] = None
    categories: Optional[List[str]] = None
    statistics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TemplateDetailsResponse(BaseModel):
    """Response de detalles de template específico"""
    success: bool
    template_info: Optional[Dict[str, Any]] = None
    vm_specification: Optional[Dict[str, Any]] = None
    cost_estimate: Optional[Dict[str, Any]] = None
    compatible_providers: Optional[List[str]] = None
    error: Optional[str] = None


class TemplateFromVMRequest(BaseModel):
    """Request para crear template desde VM existente"""
    template_name: str = Field(..., description="Nombre del nuevo template")
    description: str = Field(..., description="Descripción del template")
    category: str = Field(default="derived", description="Categoría del template")
    
    # Especificación de la VM base
    base_vm_specification: VMSpecification = Field(..., description="Especificación de la VM base")
    
    # Tags adicionales
    tags: Optional[Dict[str, str]] = Field(None, description="Tags adicionales")


class TemplateDeletionResponse(BaseModel):
    """Response de eliminación de template"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


class TemplateValidationRequest(BaseModel):
    """Request para validar un template antes de usarlo"""
    template_name: str = Field(..., description="Nombre del template a validar")
    target_provider: Optional[Provider] = Field(None, description="Proveedor objetivo")
    target_region: Optional[str] = Field(None, description="Región objetivo")


class TemplateValidationResponse(BaseModel):
    """Response de validación de template"""
    success: bool
    is_valid: Optional[bool] = None
    validation_results: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    cost_estimate: Optional[Dict[str, Any]] = None
    error: Optional[str] = None