from fastapi import FastAPI, HTTPException
from models import VMRequest, VMResponse, ResourceFamilyRequest, ResourceFamilyResponse
from models_extended import BuilderRequest, BuilderResponse, VMType, Provider
from factory import VMFactory
from resource_provisioner import ResourceProvisioningService
from vm_construction_service import VMConstructionService
from logger import safe_log

app = FastAPI(
    title="API de Aprovisionamiento Multi-Cloud",
    description="API para aprovisionar recursos en múltiples proveedores de nube usando Factory Method, Abstract Factory y Builder con Director",
    version="3.0.0"
)

# Instanciar servicios
provisioning_service = ResourceProvisioningService()
construction_service = VMConstructionService()

# ============= ENDPOINT ORIGINAL (MANTENIDO PARA COMPATIBILIDAD) =============

@app.post("/provision_vm", response_model=VMResponse, tags=["VM Individual"])
def provision_vm(request: VMRequest):
    """Aprovisiona una VM individual (endpoint original)"""
    provider_name = request.provider.lower()
    params = request.params
    safe_log(f"Solicitud aprovisionamiento VM individual {provider_name}", params)
    try:
        provider = VMFactory.get_provider(provider_name)
        success, vm_id, error = provider.create_vm(params)
        if success:
            return VMResponse(success=True, vm_id=vm_id)
        else:
            return VMResponse(success=False, error=error)
    except Exception as e:
        return VMResponse(success=False, error=str(e))

# ============= NUEVO ENDPOINT PARA FAMILIAS DE RECURSOS =============

@app.post("/provision_resource_family", response_model=ResourceFamilyResponse, tags=["Familia de Recursos"])
def provision_resource_family(request: ResourceFamilyRequest):
    """Aprovisiona una familia completa de recursos (VM + Red + Disco) de forma consistente"""
    return provisioning_service.provision_resource_family(
        provider=request.provider,
        vm_params=request.vm_params,
        network_params=request.network_params,
        storage_params=request.storage_params
    )

# ============= NUEVO ENDPOINT PARA BUILDER PATTERN =============

@app.post("/build_vm", response_model=BuilderResponse, tags=["Builder Pattern"])
def build_vm(request: BuilderRequest):
    """Construye una VM usando Director + Builder pattern con configuraciones predefinidas"""
    return construction_service.build_vm_from_request(request)

@app.get("/vm_configurations/{provider}", tags=["Builder Pattern"])
def get_vm_configurations(provider: Provider):
    """Obtiene las configuraciones disponibles para un proveedor específico"""
    return construction_service.get_available_configurations(provider)

@app.post("/validate_vm_config", tags=["Builder Pattern"])
def validate_vm_configuration(
    provider: Provider,
    vm_type: VMType,
    region: str,
    flavor: str = "medium"
):
    """Valida una configuración de VM antes de construirla"""
    return construction_service.validate_configuration(provider, vm_type, region, flavor)

@app.get("/supported_providers", tags=["Información"])
def get_supported_providers():
    """Obtiene la lista de proveedores soportados"""
    return {
        "providers": provisioning_service.get_supported_providers(),
        "vm_types": [vm_type.value for vm_type in VMType],
        "message": "Proveedores disponibles para aprovisionamiento de recursos"
    }
