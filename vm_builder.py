"""
Implementación del patrón Builder para construir VMs paso a paso.
Permite personalizar la construcción de recursos de manera flexible.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from models_extended import (
    VMSpecification, VirtualMachineConfig, NetworkConfig, StorageConfig,
    VMType, Provider
)
from vm_director import VMDirector
from abstract_factory import AbstractFactoryRegistry
from logger import safe_log

class VMBuilder(ABC):
    """Builder abstracto para construir VMs paso a paso"""
    
    def __init__(self):
        self.reset()
    
    @abstractmethod
    def reset(self):
        """Reinicia el builder para una nueva construcción"""
        pass
    
    @abstractmethod
    def set_vm_config(self, config: VirtualMachineConfig) -> 'VMBuilder':
        """Configura los parámetros de la VM"""
        pass
    
    @abstractmethod
    def set_network_config(self, config: NetworkConfig) -> 'VMBuilder':
        """Configura los parámetros de red"""
        pass
    
    @abstractmethod
    def set_storage_config(self, config: StorageConfig) -> 'VMBuilder':
        """Configura los parámetros de almacenamiento"""
        pass
    
    @abstractmethod
    def build(self) -> Dict[str, Any]:
        """Construye y retorna la VM con sus recursos"""
        pass

class ConcreteVMBuilder(VMBuilder):
    """Implementación concreta del Builder para VMs"""
    
    def __init__(self):
        self._factory_registry = AbstractFactoryRegistry()
        super().__init__()
    
    def reset(self):
        """Reinicia el estado del builder"""
        self._vm_config: Optional[VirtualMachineConfig] = None
        self._network_config: Optional[NetworkConfig] = None  
        self._storage_config: Optional[StorageConfig] = None
        self._provider: Optional[Provider] = None
        self._created_resources: List[Dict[str, Any]] = []
    
    def set_vm_config(self, config: VirtualMachineConfig) -> 'ConcreteVMBuilder':
        """Establece la configuración de VM"""
        self._vm_config = config
        self._provider = config.provider
        safe_log(f"Builder: Configurando VM {config.provider}", {
            "vcpus": config.vcpus,
            "memory_gb": config.memory_gb,
            "instance_type": getattr(config, 'instance_type', None)
        })
        return self
    
    def set_network_config(self, config: NetworkConfig) -> 'ConcreteVMBuilder':
        """Establece la configuración de red"""
        self._network_config = config
        safe_log(f"Builder: Configurando Red", {
            "region": config.region,
            "firewall_rules": config.firewall_rules,
            "public_ip": config.public_ip
        })
        return self
    
    def set_storage_config(self, config: StorageConfig) -> 'ConcreteVMBuilder':
        """Establece la configuración de almacenamiento"""
        self._storage_config = config
        safe_log(f"Builder: Configurando Storage", {
            "region": config.region,
            "size_gb": config.size_gb,
            "iops": config.iops
        })
        return self
    
    def build(self) -> Dict[str, Any]:
        """
        Construye la VM con todos sus recursos.
        Valida coherencia y crea recursos usando Abstract Factory.
        """
        # Validaciones previas
        self._validate_configuration()
        
        try:
            # Obtener factory del proveedor
            factory = self._factory_registry.get_factory(self._provider.value)
            
            # Crear recursos en orden: Network -> Storage -> VM
            network_result = self._create_network_resource(factory)
            if not network_result["success"]:
                return network_result
            
            storage_result = self._create_storage_resource(factory)
            if not storage_result["success"]:
                return storage_result
            
            vm_result = self._create_vm_resource(
                factory, 
                network_result["resource_id"], 
                storage_result["resource_id"]
            )
            if not vm_result["success"]:
                return vm_result
            
            # Compilar respuesta exitosa
            return {
                "success": True,
                "provider": self._provider.value.upper(),
                "resources": self._created_resources,
                "vm_specification": {
                    "vm_config": self._vm_config.dict(),
                    "network_config": self._network_config.dict(),
                    "storage_config": self._storage_config.dict()
                }
            }
            
        except Exception as e:
            safe_log("Builder: Error durante construcción", {"error": str(e)})
            return {
                "success": False,
                "error": f"Error durante construcción: {str(e)}"
            }
    
    def _validate_configuration(self):
        """Valida que todas las configuraciones estén establecidas y sean coherentes"""
        if not all([self._vm_config, self._network_config, self._storage_config]):
            raise ValueError("Faltan configuraciones requeridas (VM, Network o Storage)")
        
        # Validar coherencia de región
        if self._network_config.region != self._storage_config.region:
            raise ValueError("Las regiones de Network y Storage deben coincidir")
        
        # Validar coherencia de proveedor (implícita por el Director, pero verificamos)
        if not self._provider:
            raise ValueError("Proveedor no establecido")
    
    def _create_network_resource(self, factory) -> Dict[str, Any]:
        """Crea el recurso de red"""
        try:
            network = factory.create_network()
            
            # Preparar parámetros para la creación
            network_params = self._prepare_network_params()
            
            success, resource_id, error = network.create_network(network_params)
            
            if success:
                resource_info = {
                    "resource_id": resource_id,
                    "resource_type": "network",
                    "status": "provisioned",
                    "details": network_params
                }
                self._created_resources.append(resource_info)
                return {"success": True, "resource_id": resource_id}
            else:
                return {"success": False, "error": error}
                
        except Exception as e:
            return {"success": False, "error": f"Error creando red: {str(e)}"}
    
    def _create_storage_resource(self, factory) -> Dict[str, Any]:
        """Crea el recurso de almacenamiento"""
        try:
            storage = factory.create_storage()
            
            # Preparar parámetros para la creación
            storage_params = self._prepare_storage_params()
            
            success, resource_id, error = storage.create_storage(storage_params)
            
            if success:
                resource_info = {
                    "resource_id": resource_id,
                    "resource_type": "storage",
                    "status": "provisioned", 
                    "details": storage_params
                }
                self._created_resources.append(resource_info)
                return {"success": True, "resource_id": resource_id}
            else:
                return {"success": False, "error": error}
                
        except Exception as e:
            return {"success": False, "error": f"Error creando almacenamiento: {str(e)}"}
    
    def _create_vm_resource(self, factory, network_id: str, storage_id: str) -> Dict[str, Any]:
        """Crea el recurso de VM asociado a red y almacenamiento"""
        try:
            vm = factory.create_vm()
            
            # Preparar parámetros para la creación
            vm_params = self._prepare_vm_params()
            
            success, resource_id, error = vm.create_vm(vm_params, network_id, storage_id)
            
            if success:
                resource_info = {
                    "resource_id": resource_id,
                    "resource_type": "vm",
                    "status": "provisioned",
                    "details": {
                        **vm_params,
                        "network_id": network_id,
                        "storage_id": storage_id
                    }
                }
                self._created_resources.append(resource_info)
                return {"success": True, "resource_id": resource_id}
            else:
                return {"success": False, "error": error}
                
        except Exception as e:
            return {"success": False, "error": f"Error creando VM: {str(e)}"}
    
    def _prepare_network_params(self) -> Dict[str, Any]:
        """Prepara los parámetros de red según el proveedor"""
        config = self._network_config
        
        if self._provider == Provider.AWS:
            return {
                "vpcId": config.vpc_id or f"vpc-{config.region.replace('-', '')}",
                "subnet": config.subnet or f"subnet-{config.region.replace('-', '')}",
                "securityGroup": config.security_group or "sg-default",
                "region": config.region,
                "firewallRules": config.firewall_rules,
                "publicIP": config.public_ip
            }
        elif self._provider == Provider.AZURE:
            return {
                "virtualNetwork": config.virtual_network or f"vnet-{config.region}",
                "subnetName": config.subnet_name or "subnet-default",
                "networkSecurityGroup": config.network_security_group or "nsg-default",
                "region": config.region,
                "firewallRules": config.firewall_rules,
                "publicIP": config.public_ip
            }
        elif self._provider == Provider.GCP:
            return {
                "networkName": config.network_name or "default",
                "subnetworkName": config.subnetwork_name or f"subnet-{config.region}",
                "firewallTag": config.firewall_tag or "allow-default",
                "region": config.region,
                "firewallRules": config.firewall_rules,
                "publicIP": config.public_ip
            }
        elif self._provider == Provider.ONPREMISE:
            return {
                "physicalInterface": config.physical_interface or "eth0",
                "vlanId": config.vlan_id or 100,
                "firewallPolicy": config.firewall_policy or "allow-default",
                "region": config.region,
                "firewallRules": config.firewall_rules,
                "publicIP": config.public_ip
            }
    
    def _prepare_storage_params(self) -> Dict[str, Any]:
        """Prepara los parámetros de almacenamiento según el proveedor"""
        config = self._storage_config
        
        if self._provider == Provider.AWS:
            return {
                "volumeType": config.volume_type or "gp2",
                "sizeGB": config.size_gb,
                "encrypted": config.encrypted or True,
                "region": config.region,
                "iops": config.iops
            }
        elif self._provider == Provider.AZURE:
            return {
                "diskSku": config.disk_sku or "Standard_LRS", 
                "sizeGB": config.size_gb,
                "managedDisk": config.managed_disk or True,
                "region": config.region,
                "iops": config.iops
            }
        elif self._provider == Provider.GCP:
            return {
                "diskType": config.disk_type or "pd-standard",
                "sizeGB": config.size_gb,
                "autoDelete": config.auto_delete or True,
                "region": config.region,
                "iops": config.iops
            }
        elif self._provider == Provider.ONPREMISE:
            return {
                "storagePool": config.storage_pool or "pool-default",
                "sizeGB": config.size_gb,
                "raidLevel": config.raid_level or "raid1",
                "region": config.region,
                "iops": config.iops
            }
    
    def _prepare_vm_params(self) -> Dict[str, Any]:
        """Prepara los parámetros de VM según el proveedor"""
        config = self._vm_config
        
        base_params = {
            "vcpus": config.vcpus,
            "memoryGB": config.memory_gb,
            "memoryOptimization": config.memory_optimization,
            "diskOptimization": config.disk_optimization,
            "keyPairName": config.key_pair_name
        }
        
        if self._provider == Provider.AWS:
            return {
                **base_params,
                "instance_type": config.instance_type,
                "region": self._network_config.region,
                "ami": config.ami
            }
        elif self._provider == Provider.AZURE:
            return {
                **base_params,
                "size": config.size,
                "resource_group": config.resource_group,
                "image": config.image,
                "region": self._network_config.region
            }
        elif self._provider == Provider.GCP:
            return {
                **base_params,
                "machine_type": config.machine_type,
                "zone": self._network_config.region,
                "project": config.project
            }
        elif self._provider == Provider.ONPREMISE:
            return {
                **base_params,
                "cpu": config.cpu or config.vcpus,
                "ram": config.ram or config.memory_gb,
                "hypervisor": config.hypervisor or "vmware"
            }