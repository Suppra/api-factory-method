from fastapi import FastAPI, HTTPException
from models import VMRequest, VMResponse, ResourceFamilyRequest, ResourceFamilyResponse
from factory import VMFactory
from resource_provisioner import ResourceProvisioningService
from logger import safe_log

app = FastAPI(
    title="API de Aprovisionamiento Multi-Cloud",
    description="API para aprovisionar recursos en múltiples proveedores de nube usando Factory Method y Abstract Factory",
    version="2.0.0"
)

# Instanciar servicio de aprovisionamiento
provisioning_service = ResourceProvisioningService()

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

@app.get("/supported_providers", tags=["Información"])
def get_supported_providers():
    """Obtiene la lista de proveedores soportados"""
    return {
        "providers": provisioning_service.get_supported_providers(),
        "message": "Proveedores disponibles para aprovisionamiento de recursos"
    }
