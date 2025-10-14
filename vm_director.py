"""
Implementación del patrón Director para orquestar la construcción de diferentes tipos de VM.
Define las especificaciones de hardware para cada proveedor y tipo de VM.
"""

from typing import Dict, Any
from models_extended import (
    VMType, Provider, VMSpecification, VirtualMachineConfig, 
    NetworkConfig, StorageConfig
)

class VMDirector:
    """
    Director que define las políticas de construcción y valores de recursos
    para diferentes tipos de VM según el proveedor.
    """
    
    def __init__(self):
        self._vm_specifications = self._initialize_vm_specs()
    
    def _initialize_vm_specs(self) -> Dict[Provider, Dict[VMType, Dict[str, Any]]]:
        """Inicializa las especificaciones de VM por proveedor y tipo"""
        return {
            Provider.AWS: {
                VMType.STANDARD: {
                    "flavors": {
                        "small": {"instance_type": "t3.medium", "vcpus": 2, "memory_gb": 4},
                        "medium": {"instance_type": "m5.large", "vcpus": 2, "memory_gb": 8},
                        "large": {"instance_type": "m5.xlarge", "vcpus": 4, "memory_gb": 16}
                    },
                    "default_flavor": "medium"
                },
                VMType.MEMORY_OPTIMIZED: {
                    "flavors": {
                        "small": {"instance_type": "r5.large", "vcpus": 2, "memory_gb": 16},
                        "medium": {"instance_type": "r5.xlarge", "vcpus": 4, "memory_gb": 32},
                        "large": {"instance_type": "r5.2xlarge", "vcpus": 8, "memory_gb": 64}
                    },
                    "default_flavor": "small"
                },
                VMType.COMPUTE_OPTIMIZED: {
                    "flavors": {
                        "small": {"instance_type": "c5.large", "vcpus": 2, "memory_gb": 4},
                        "medium": {"instance_type": "c5.xlarge", "vcpus": 4, "memory_gb": 8},
                        "large": {"instance_type": "c5.2xlarge", "vcpus": 8, "memory_gb": 16}
                    },
                    "default_flavor": "medium"
                }
            },
            Provider.AZURE: {
                VMType.STANDARD: {
                    "flavors": {
                        "small": {"size": "D2s_v3", "vcpus": 2, "memory_gb": 8},
                        "medium": {"size": "D4s_v3", "vcpus": 4, "memory_gb": 16},
                        "large": {"size": "D8s_v3", "vcpus": 8, "memory_gb": 32}
                    },
                    "default_flavor": "small"
                },
                VMType.MEMORY_OPTIMIZED: {
                    "flavors": {
                        "small": {"size": "E2s_v3", "vcpus": 2, "memory_gb": 16},
                        "medium": {"size": "E4s_v3", "vcpus": 4, "memory_gb": 32},
                        "large": {"size": "E8s_v3", "vcpus": 8, "memory_gb": 64}
                    },
                    "default_flavor": "small"
                },
                VMType.COMPUTE_OPTIMIZED: {
                    "flavors": {
                        "small": {"size": "F2s_v2", "vcpus": 2, "memory_gb": 4},
                        "medium": {"size": "F4s_v2", "vcpus": 4, "memory_gb": 8},
                        "large": {"size": "F8s_v2", "vcpus": 8, "memory_gb": 16}
                    },
                    "default_flavor": "medium"
                }
            },
            Provider.GCP: {
                VMType.STANDARD: {
                    "flavors": {
                        "small": {"machine_type": "e2-standard-2", "vcpus": 2, "memory_gb": 8},
                        "medium": {"machine_type": "e2-standard-4", "vcpus": 4, "memory_gb": 16},
                        "large": {"machine_type": "e2-standard-8", "vcpus": 8, "memory_gb": 32}
                    },
                    "default_flavor": "small"
                },
                VMType.MEMORY_OPTIMIZED: {
                    "flavors": {
                        "small": {"machine_type": "n2-highmem-2", "vcpus": 2, "memory_gb": 16},
                        "medium": {"machine_type": "n2-highmem-4", "vcpus": 4, "memory_gb": 32},
                        "large": {"machine_type": "n2-highmem-8", "vcpus": 8, "memory_gb": 64}
                    },
                    "default_flavor": "small"
                },
                VMType.COMPUTE_OPTIMIZED: {
                    "flavors": {
                        "small": {"machine_type": "n2-highcpu-2", "vcpus": 2, "memory_gb": 2},
                        "medium": {"machine_type": "n2-highcpu-4", "vcpus": 4, "memory_gb": 4},
                        "large": {"machine_type": "n2-highcpu-8", "vcpus": 8, "memory_gb": 8}
                    },
                    "default_flavor": "medium"
                }
            },
            Provider.ONPREMISE: {
                VMType.STANDARD: {
                    "flavors": {
                        "small": {"flavor": "onprem-std1", "vcpus": 2, "memory_gb": 4},
                        "medium": {"flavor": "onprem-std2", "vcpus": 4, "memory_gb": 8},
                        "large": {"flavor": "onprem-std3", "vcpus": 8, "memory_gb": 16}
                    },
                    "default_flavor": "medium"
                },
                VMType.MEMORY_OPTIMIZED: {
                    "flavors": {
                        "small": {"flavor": "onprem-mem1", "vcpus": 2, "memory_gb": 16},
                        "medium": {"flavor": "onprem-mem2", "vcpus": 4, "memory_gb": 32},
                        "large": {"flavor": "onprem-mem3", "vcpus": 8, "memory_gb": 64}
                    },
                    "default_flavor": "small"
                },
                VMType.COMPUTE_OPTIMIZED: {
                    "flavors": {
                        "small": {"flavor": "onprem-cpu1", "vcpus": 2, "memory_gb": 2},
                        "medium": {"flavor": "onprem-cpu2", "vcpus": 4, "memory_gb": 4},
                        "large": {"flavor": "onprem-cpu3", "vcpus": 8, "memory_gb": 8}
                    },
                    "default_flavor": "medium"
                }
            }
        }
    
    def get_vm_specification(
        self, 
        provider: Provider, 
        vm_type: VMType, 
        region: str,
        flavor: str = None,
        custom_overrides: Dict[str, Any] = None
    ) -> VMSpecification:
        """
        Obtiene la especificación completa de una VM según el Director.
        
        Args:
            provider: Proveedor de nube
            vm_type: Tipo de VM (standard, memory_optimized, compute_optimized)
            region: Región donde desplegar
            flavor: Tamaño específico (small, medium, large)
            custom_overrides: Configuraciones personalizadas
            
        Returns:
            VMSpecification: Especificación completa de la VM
        """
        if provider not in self._vm_specifications:
            raise ValueError(f"Proveedor {provider} no soportado")
            
        if vm_type not in self._vm_specifications[provider]:
            raise ValueError(f"Tipo de VM {vm_type} no soportado para {provider}")
        
        spec_data = self._vm_specifications[provider][vm_type]
        
        # Usar flavor por defecto si no se especifica
        if not flavor:
            flavor = spec_data["default_flavor"]
        
        if flavor not in spec_data["flavors"]:
            raise ValueError(f"Flavor {flavor} no disponible para {provider} {vm_type}")
        
        flavor_config = spec_data["flavors"][flavor]
        
        # Construir configuración de VM
        vm_config = self._build_vm_config(provider, vm_type, flavor_config, custom_overrides)
        
        # Construir configuración de red
        network_config = self._build_network_config(provider, region, vm_type)
        
        # Construir configuración de almacenamiento
        storage_config = self._build_storage_config(provider, region, vm_type)
        
        return VMSpecification(
            vm_type=vm_type,
            provider=provider,
            region=region,
            vm_config=vm_config,
            network_config=network_config,
            storage_config=storage_config
        )
    
    def _build_vm_config(
        self, 
        provider: Provider, 
        vm_type: VMType, 
        flavor_config: Dict[str, Any],
        custom_overrides: Dict[str, Any] = None
    ) -> VirtualMachineConfig:
        """Construye la configuración de VM según el proveedor y tipo"""
        
        # Configuración base del Director
        config = {
            "provider": provider,
            "vcpus": flavor_config["vcpus"],
            "memory_gb": flavor_config["memory_gb"],
            "memory_optimization": vm_type == VMType.MEMORY_OPTIMIZED,
            "disk_optimization": vm_type == VMType.COMPUTE_OPTIMIZED,
            "key_pair_name": "default-key"
        }
        
        # Agregar parámetros específicos del proveedor
        if provider == Provider.AWS:
            config.update({
                "instance_type": flavor_config["instance_type"],
                "ami": "ami-0c02fb55956c7d316"  # Amazon Linux 2
            })
        elif provider == Provider.AZURE:
            config.update({
                "size": flavor_config["size"],
                "resource_group": "rg-default",
                "image": "UbuntuLTS"
            })
        elif provider == Provider.GCP:
            config.update({
                "machine_type": flavor_config["machine_type"],
                "project": "default-project"
            })
        elif provider == Provider.ONPREMISE:
            config.update({
                "cpu": flavor_config["vcpus"],
                "ram": flavor_config["memory_gb"],
                "hypervisor": "vmware"
            })
        
        # Aplicar overrides personalizados
        if custom_overrides:
            config.update(custom_overrides)
        
        return VirtualMachineConfig(**config)
    
    def _build_network_config(
        self, 
        provider: Provider, 
        region: str, 
        vm_type: VMType
    ) -> NetworkConfig:
        """Construye la configuración de red según el proveedor"""
        
        config = {
            "region": region,
            "firewall_rules": ["SSH", "HTTP", "HTTPS"],
            "public_ip": True
        }
        
        if provider == Provider.AWS:
            config.update({
                "vpc_id": f"vpc-{region.replace('-', '')}",
                "subnet": f"subnet-{region.replace('-', '')}",
                "security_group": f"sg-{vm_type.value}"
            })
        elif provider == Provider.AZURE:
            config.update({
                "virtual_network": f"vnet-{region}",
                "subnet_name": f"subnet-{vm_type.value}",
                "network_security_group": f"nsg-{vm_type.value}"
            })
        elif provider == Provider.GCP:
            config.update({
                "network_name": "default",
                "subnetwork_name": f"subnet-{region}",
                "firewall_tag": f"allow-{vm_type.value}"
            })
        elif provider == Provider.ONPREMISE:
            config.update({
                "physical_interface": "eth0",
                "vlan_id": 100,
                "firewall_policy": f"policy-{vm_type.value}"
            })
        
        return NetworkConfig(**config)
    
    def _build_storage_config(
        self, 
        provider: Provider, 
        region: str, 
        vm_type: VMType
    ) -> StorageConfig:
        """Construye la configuración de almacenamiento según el proveedor y tipo"""
        
        # Tamaño base según tipo de VM
        base_size = {
            VMType.STANDARD: 50,
            VMType.MEMORY_OPTIMIZED: 100,
            VMType.COMPUTE_OPTIMIZED: 30
        }
        
        config = {
            "region": region,
            "size_gb": base_size[vm_type],
            "iops": 3000 if vm_type == VMType.COMPUTE_OPTIMIZED else 1000
        }
        
        if provider == Provider.AWS:
            config.update({
                "volume_type": "gp3" if vm_type == VMType.COMPUTE_OPTIMIZED else "gp2",
                "encrypted": True
            })
        elif provider == Provider.AZURE:
            config.update({
                "disk_sku": "Premium_LRS" if vm_type == VMType.MEMORY_OPTIMIZED else "Standard_LRS",
                "managed_disk": True
            })
        elif provider == Provider.GCP:
            config.update({
                "disk_type": "pd-ssd" if vm_type == VMType.COMPUTE_OPTIMIZED else "pd-standard",
                "auto_delete": True
            })
        elif provider == Provider.ONPREMISE:
            config.update({
                "storage_pool": f"pool-{vm_type.value}",
                "raid_level": "raid1"
            })
        
        return StorageConfig(**config)
    
    def get_available_vm_types(self, provider: Provider) -> Dict[VMType, Dict[str, Any]]:
        """Obtiene los tipos de VM disponibles para un proveedor"""
        if provider not in self._vm_specifications:
            return {}
        
        result = {}
        for vm_type, spec in self._vm_specifications[provider].items():
            result[vm_type] = {
                "flavors": list(spec["flavors"].keys()),
                "default_flavor": spec["default_flavor"],
                "configurations": spec["flavors"]
            }
        
        return result