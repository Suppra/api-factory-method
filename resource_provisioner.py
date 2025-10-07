# resource_provisioner.py - Servicio de aprovisionamiento de familias de recursos

from abstract_factory import AbstractFactoryRegistry, CloudResourceFactory
from resources import NetworkResource, StorageResource, VMResource
from models import ResourceInfo, ResourceFamilyResponse
from logger import safe_log
from typing import Tuple, List, Optional

class ResourceProvisioningService:
    """Servicio para aprovisionar familias de recursos usando Abstract Factory"""
    
    def __init__(self):
        self.factory_registry = AbstractFactoryRegistry()
    
    def provision_resource_family(
        self, 
        provider: str, 
        vm_params: dict, 
        network_params: dict, 
        storage_params: dict
    ) -> ResourceFamilyResponse:
        """
        Aprovisiona una familia completa de recursos (VM + Red + Disco) para un proveedor específico.
        
        Garantiza consistencia: todos los recursos pertenecen al mismo proveedor.
        Aplica el principio de atomicidad: si falla algún recurso, no se crean los demás.
        """
        
        provider_name = provider.lower()
        safe_log(f"Iniciando aprovisionamiento de familia de recursos para {provider_name}", {
            "vm_params": vm_params,
            "network_params": network_params, 
            "storage_params": storage_params
        })
        
        try:
            # Obtener factory del proveedor específico
            factory = self.factory_registry.get_factory(provider_name)
            
            # Crear instancias de recursos usando la factory
            network_resource = factory.create_network()
            storage_resource = factory.create_storage()
            vm_resource = factory.create_vm()
            
            # Aprovisionar recursos en orden: Red -> Almacenamiento -> VM
            resources_created = []
            
            # 1. Crear recurso de red
            success, network_id, error = network_resource.create_network(network_params)
            if not success:
                return ResourceFamilyResponse(
                    success=False, 
                    error=f"Error al crear recurso de red: {error}"
                )
            
            resources_created.append(ResourceInfo(
                resource_id=network_id,
                resource_type="network",
                status="disponible",
                details=network_resource.get_network_info()
            ))
            
            safe_log(f"Recurso de red creado exitosamente", {"network_id": network_id})
            
            # 2. Crear recurso de almacenamiento
            success, storage_id, error = storage_resource.create_storage(storage_params)
            if not success:
                return ResourceFamilyResponse(
                    success=False, 
                    error=f"Error al crear recurso de almacenamiento: {error}"
                )
            
            resources_created.append(ResourceInfo(
                resource_id=storage_id,
                resource_type="storage", 
                status="disponible",
                details=storage_resource.get_storage_info()
            ))
            
            safe_log(f"Recurso de almacenamiento creado exitosamente", {"storage_id": storage_id})
            
            # 3. Crear VM asociada a la red y almacenamiento
            success, vm_id, error = vm_resource.create_vm(vm_params, network_id, storage_id)
            if not success:
                return ResourceFamilyResponse(
                    success=False, 
                    error=f"Error al crear VM: {error}"
                )
            
            resources_created.append(ResourceInfo(
                resource_id=vm_id,
                resource_type="vm",
                status="aprovisionada",
                details=vm_resource.get_vm_info()
            ))
            
            safe_log(f"VM creada exitosamente", {"vm_id": vm_id})
            
            # Retornar respuesta exitosa con todos los recursos creados
            return ResourceFamilyResponse(
                success=True,
                provider=factory.get_provider_name(),
                resources=resources_created
            )
            
        except ValueError as e:
            # Proveedor no soportado
            return ResourceFamilyResponse(
                success=False,
                error=str(e)
            )
        except Exception as e:
            # Error inesperado
            safe_log(f"Error inesperado en aprovisionamiento", {"error": str(e)})
            return ResourceFamilyResponse(
                success=False,
                error=f"Error interno del sistema: {str(e)}"
            )
    
    def get_supported_providers(self) -> List[str]:
        """Obtener lista de proveedores soportados"""
        return self.factory_registry.get_supported_providers()
    
    def register_new_provider(self, provider_name: str, factory_class: type):
        """Registrar un nuevo proveedor para extensibilidad futura"""
        self.factory_registry.register_factory(provider_name, factory_class)
        safe_log(f"Nuevo proveedor registrado", {"provider": provider_name})