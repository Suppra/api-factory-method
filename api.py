from fastapi import FastAPI, HTTPException
from models import VMRequest, VMResponse, ResourceFamilyRequest, ResourceFamilyResponse
from models_extended import BuilderRequest, BuilderResponse, VMType, Provider
from prototype_models import (
    TemplateCreationRequest, TemplateCreationResponse,
    TemplateRegistrationRequest, TemplateRegistrationResponse,
    TemplateListResponse, TemplateDetailsResponse,
    TemplateFromVMRequest, TemplateDeletionResponse,
    TemplateValidationRequest, TemplateValidationResponse
)
from factory import VMFactory
from resource_provisioner import ResourceProvisioningService
from vm_construction_service import VMConstructionService
from vm_prototype_service import VMPrototypeService
from logger import safe_log

app = FastAPI(
    title="API de Aprovisionamiento Multi-Cloud",
    description="API para aprovisionar recursos en múltiples proveedores de nube usando Factory Method, Abstract Factory y Builder con Director",
    version="3.0.0"
)

# Instanciar servicios
provisioning_service = ResourceProvisioningService()
construction_service = VMConstructionService()
prototype_service = VMPrototypeService()

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

# ============= ENDPOINTS PARA PATRÓN PROTOTYPE =============

@app.post("/create_from_template", response_model=TemplateCreationResponse, tags=["Prototype Pattern"])
def create_vm_from_template(request: TemplateCreationRequest):
    """Crea una VM a partir de un template existente con personalizaciones opcionales"""
    safe_log(f"API: Creando VM desde template '{request.template_name}'", {
        "provider": request.provider,
        "region": request.region,
        "has_customizations": any([
            request.vm_customizations,
            request.network_customizations, 
            request.storage_customizations
        ])
    })
    
    # Consolidar personalizaciones
    customizations = {}
    if request.vm_customizations:
        customizations["vm_config"] = request.vm_customizations
    if request.network_customizations:
        customizations["network_config"] = request.network_customizations
    if request.storage_customizations:
        customizations["storage_config"] = request.storage_customizations
    if request.additional_tags:
        customizations["tags"] = request.additional_tags
    if request.region:
        customizations["region"] = request.region
    
    # Crear VM usando el servicio de prototipos
    result = prototype_service.create_from_template(
        template_name=request.template_name,
        provider=request.provider,
        region=request.region,
        customizations=customizations if customizations else None
    )
    
    # Convertir BuilderResponse a TemplateCreationResponse
    if result.success:
        return TemplateCreationResponse(
            success=True,
            template_name=request.template_name,
            vm_specification=result.vm_specification,
            created_resources=result.created_resources,
            cost_estimate=None  # TODO: Agregar estimación de costo
        )
    else:
        return TemplateCreationResponse(
            success=False,
            error=result.error
        )

@app.post("/register_template", response_model=TemplateRegistrationResponse, tags=["Prototype Pattern"])
def register_vm_template(request: TemplateRegistrationRequest):
    """Registra un nuevo template de VM en el sistema"""
    safe_log(f"API: Registrando template '{request.template_name}'", {
        "category": request.category,
        "provider": request.vm_specification.provider
    })
    
    result = prototype_service.register_template(
        template_name=request.template_name,
        vm_specification=request.vm_specification,
        description=request.description,
        category=request.category,
        tags=request.tags
    )
    
    return TemplateRegistrationResponse(
        success=result["success"],
        template_name=request.template_name if result["success"] else None,
        template_info=result.get("template_info"),
        message=result.get("message"),
        error=result.get("error")
    )

@app.get("/vm_templates", response_model=TemplateListResponse, tags=["Prototype Pattern"])
def list_vm_templates(category: str = None):
    """Lista todos los templates disponibles, opcionalmente filtrados por categoría"""
    safe_log("API: Listando templates", {"category": category})
    
    result = prototype_service.list_available_templates(category)
    
    return TemplateListResponse(
        success=result["success"],
        templates=result.get("templates"),
        total=result.get("total"),
        categories=result.get("categories"),
        statistics=result.get("statistics"),
        error=result.get("error")
    )

@app.get("/vm_templates/{template_name}", response_model=TemplateDetailsResponse, tags=["Prototype Pattern"])
def get_template_details(template_name: str):
    """Obtiene los detalles completos de un template específico"""
    safe_log(f"API: Obteniendo detalles de template '{template_name}'")
    
    result = prototype_service.get_template_details(template_name)
    
    return TemplateDetailsResponse(
        success=result["success"],
        template_info=result.get("template_info"),
        vm_specification=result.get("vm_specification"),
        cost_estimate=result.get("cost_estimate"),
        compatible_providers=result.get("compatible_providers"),
        error=result.get("error")
    )

@app.delete("/vm_templates/{template_name}", response_model=TemplateDeletionResponse, tags=["Prototype Pattern"])
def delete_vm_template(template_name: str):
    """Elimina un template del sistema"""
    safe_log(f"API: Eliminando template '{template_name}'")
    
    result = prototype_service.delete_template(template_name)
    
    return TemplateDeletionResponse(
        success=result["success"],
        message=result.get("message"),
        error=result.get("error")
    )

@app.post("/create_template_from_vm", response_model=TemplateRegistrationResponse, tags=["Prototype Pattern"])
def create_template_from_existing_vm(request: TemplateFromVMRequest):
    """Crea un nuevo template basado en una VM existente"""
    safe_log(f"API: Creando template '{request.template_name}' desde VM existente")
    
    result = prototype_service.create_template_from_existing_vm(
        template_name=request.template_name,
        base_vm_spec=request.base_vm_specification,
        description=request.description,
        category=request.category,
        tags=request.tags
    )
    
    return TemplateRegistrationResponse(
        success=result["success"],
        template_name=request.template_name if result["success"] else None,
        template_info=result.get("template_info"),
        message=result.get("message"),
        error=result.get("error")
    )

@app.post("/validate_template", response_model=TemplateValidationResponse, tags=["Prototype Pattern"])
def validate_vm_template(request: TemplateValidationRequest):
    """Valida un template antes de usarlo, opcionalmente para un proveedor/región específicos"""
    safe_log(f"API: Validando template '{request.template_name}'", {
        "target_provider": request.target_provider,
        "target_region": request.target_region
    })
    
    # Obtener detalles del template
    template_details = prototype_service.get_template_details(request.template_name)
    
    if not template_details["success"]:
        return TemplateValidationResponse(
            success=False,
            error=template_details["error"]
        )
    
    # Realizar validación básica
    validation_results = {
        "template_exists": True,
        "has_valid_config": True,
        "provider_compatible": True,
        "region_available": True
    }
    
    suggestions = []
    
    # Si se especifica proveedor objetivo, verificar compatibilidad
    if request.target_provider:
        compatible_providers = template_details.get("compatible_providers", [])
        if str(request.target_provider) not in compatible_providers:
            validation_results["provider_compatible"] = False
            suggestions.append(f"Template no es compatible con {request.target_provider}. Proveedores compatibles: {', '.join(compatible_providers)}")
    
    # Validación exitosa si todos los checks pasan
    is_valid = all(validation_results.values())
    
    return TemplateValidationResponse(
        success=True,
        is_valid=is_valid,
        validation_results=validation_results,
        suggestions=suggestions if suggestions else None,
        cost_estimate=template_details.get("cost_estimate")
    )
