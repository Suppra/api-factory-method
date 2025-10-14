"""
Servicio de construcción de VMs que integra Director + Builder + Abstract Factory.
Orquesta todo el proceso de construcción de VMs con el patrón combinado.
"""

from typing import Dict, Any, Optional
from models_extended import (
    BuilderRequest, BuilderResponse, VMSpecification, VMType, Provider
)
from vm_director import VMDirector
from vm_builder import ConcreteVMBuilder
from logger import safe_log

class VMConstructionService:
    """
    Servicio principal que coordina Director, Builder y Abstract Factory
    para construir VMs de manera extensible y mantenible.
    """
    
    def __init__(self):
        self.director = VMDirector()
    
    def build_vm(
        self, 
        vm_type: VMType, 
        provider: Provider, 
        region: str,
        flavor: str = None,
        custom_vm_config: Optional[Dict[str, Any]] = None,
        custom_network_config: Optional[Dict[str, Any]] = None,
        custom_storage_config: Optional[Dict[str, Any]] = None
    ) -> BuilderResponse:
        """
        Construye una VM completa usando Director + Builder pattern.
        
        Args:
            vm_type: Tipo de VM (standard, memory_optimized, compute_optimized)
            provider: Proveedor de nube
            region: Región de despliegue
            flavor: Tamaño de VM (small, medium, large)
            custom_vm_config: Configuraciones personalizadas de VM
            custom_network_config: Configuraciones personalizadas de red
            custom_storage_config: Configuraciones personalizadas de almacenamiento
            
        Returns:
            BuilderResponse: Resultado de la construcción
        """
        
        safe_log(f"VMConstruction: Iniciando construcción {vm_type} en {provider}", {
            "region": region,
            "flavor": flavor
        })
        
        try:
            # 1. Director crea la especificación base
            vm_specification = self.director.get_vm_specification(
                provider=provider,
                vm_type=vm_type,
                region=region,
                flavor=flavor,
                custom_overrides=custom_vm_config
            )
            
            # 2. Aplicar overrides personalizados si existen
            if custom_network_config:
                self._apply_network_overrides(vm_specification, custom_network_config)
            
            if custom_storage_config:
                self._apply_storage_overrides(vm_specification, custom_storage_config)
            
            # 3. Builder construye la VM paso a paso
            builder = ConcreteVMBuilder()
            result = (builder
                     .set_vm_config(vm_specification.vm_config)
                     .set_network_config(vm_specification.network_config)  
                     .set_storage_config(vm_specification.storage_config)
                     .build())
            
            # 4. Preparar respuesta
            if result["success"]:
                return BuilderResponse(
                    success=True,
                    vm_specification=vm_specification,
                    created_resources=result["resources"]
                )
            else:
                return BuilderResponse(
                    success=False,
                    error=result["error"]
                )
                
        except Exception as e:
            safe_log("VMConstruction: Error durante construcción", {"error": str(e)})
            return BuilderResponse(
                success=False,
                error=f"Error en construcción: {str(e)}"
            )
    
    def build_vm_from_request(self, request: BuilderRequest) -> BuilderResponse:
        """
        Construye una VM a partir de un BuilderRequest.
        Método de conveniencia para el API REST.
        """
        return self.build_vm(
            vm_type=request.vm_type,
            provider=request.provider,
            region=request.region,
            custom_vm_config=request.custom_vm_config,
            custom_network_config=request.custom_network_config,
            custom_storage_config=request.custom_storage_config
        )
    
    def get_available_configurations(self, provider: Provider) -> Dict[str, Any]:
        """
        Obtiene las configuraciones disponibles para un proveedor.
        Útil para documentación y validación.
        """
        try:
            vm_types = self.director.get_available_vm_types(provider)
            
            return {
                "provider": provider.value,
                "vm_types": vm_types,
                "supported_regions": self._get_supported_regions(provider),
                "default_configs": self._get_default_configs(provider)
            }
            
        except Exception as e:
            return {
                "error": f"Error obteniendo configuraciones: {str(e)}"
            }
    
    def validate_configuration(
        self,
        provider: Provider,
        vm_type: VMType, 
        region: str,
        flavor: str = None
    ) -> Dict[str, Any]:
        """
        Valida una configuración antes de construcción.
        Permite verificar compatibilidad sin crear recursos.
        """
        try:
            # Intentar obtener especificación del Director
            specification = self.director.get_vm_specification(
                provider=provider,
                vm_type=vm_type,
                region=region,
                flavor=flavor
            )
            
            return {
                "valid": True,
                "specification": specification.dict(),
                "estimated_cost": self._estimate_cost(specification),
                "warnings": self._get_configuration_warnings(specification)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "suggestions": self._get_configuration_suggestions(provider, vm_type)
            }
    
    def _apply_network_overrides(self, specification: VMSpecification, overrides: Dict[str, Any]):
        """Aplica configuraciones personalizadas de red"""
        for key, value in overrides.items():
            if hasattr(specification.network_config, key):
                setattr(specification.network_config, key, value)
    
    def _apply_storage_overrides(self, specification: VMSpecification, overrides: Dict[str, Any]):
        """Aplica configuraciones personalizadas de almacenamiento"""
        for key, value in overrides.items():
            if hasattr(specification.storage_config, key):
                setattr(specification.storage_config, key, value)
    
    def _get_supported_regions(self, provider: Provider) -> list[str]:
        """Obtiene las regiones soportadas por proveedor"""
        regions_map = {
            Provider.AWS: ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
            Provider.AZURE: ["eastus", "westus2", "westeurope", "southeastasia"],
            Provider.GCP: ["us-central1", "us-west1", "europe-west1", "asia-southeast1"],
            Provider.ONPREMISE: ["datacenter-1", "datacenter-2", "edge-location-1"]
        }
        return regions_map.get(provider, [])
    
    def _get_default_configs(self, provider: Provider) -> Dict[str, Any]:
        """Obtiene configuraciones por defecto del proveedor"""
        return {
            "default_vm_type": VMType.STANDARD,
            "default_flavor": "medium",
            "default_region": self._get_supported_regions(provider)[0] if self._get_supported_regions(provider) else None,
            "network_defaults": {
                "firewall_rules": ["SSH", "HTTP", "HTTPS"],
                "public_ip": True
            },
            "storage_defaults": {
                "iops": 3000,
                "encrypted": True
            }
        }
    
    def _estimate_cost(self, specification: VMSpecification) -> Dict[str, Any]:
        """Estima el costo de una configuración (simulado)"""
        # Simulación de estimación de costos
        base_cost_per_hour = {
            VMType.STANDARD: 0.10,
            VMType.MEMORY_OPTIMIZED: 0.20,
            VMType.COMPUTE_OPTIMIZED: 0.15
        }
        
        vm_cost = base_cost_per_hour[specification.vm_type] * specification.vm_config.vcpus
        storage_cost = specification.storage_config.size_gb * 0.001
        network_cost = 0.05 if specification.network_config.public_ip else 0.02
        
        total_hourly = vm_cost + storage_cost + network_cost
        
        return {
            "currency": "USD",
            "vm_cost_hourly": round(vm_cost, 4),
            "storage_cost_hourly": round(storage_cost, 4),
            "network_cost_hourly": round(network_cost, 4),
            "total_hourly": round(total_hourly, 4),
            "estimated_monthly": round(total_hourly * 24 * 30, 2)
        }
    
    def _get_configuration_warnings(self, specification: VMSpecification) -> list[str]:
        """Genera advertencias sobre la configuración"""
        warnings = []
        
        # Advertencia por alta memoria
        if specification.vm_config.memory_gb > 32:
            warnings.append("Configuración de alta memoria puede incrementar costos significativamente")
        
        # Advertencia por almacenamiento grande
        if specification.storage_config.size_gb > 1000:
            warnings.append("Almacenamiento grande puede afectar tiempos de backup")
        
        # Advertencia por IP pública
        if specification.network_config.public_ip:
            warnings.append("IP pública expone la VM a internet, asegurar reglas de firewall")
        
        return warnings
    
    def _get_configuration_suggestions(self, provider: Provider, vm_type: VMType) -> list[str]:
        """Genera sugerencias para configuraciones inválidas"""
        suggestions = []
        
        try:
            available_types = self.director.get_available_vm_types(provider)
            if available_types:
                suggestions.append(f"Tipos disponibles para {provider.value}: {list(available_types.keys())}")
                
                if vm_type in available_types:
                    flavors = available_types[vm_type]["flavors"]
                    suggestions.append(f"Flavors disponibles para {vm_type.value}: {flavors}")
            
            regions = self._get_supported_regions(provider)
            if regions:
                suggestions.append(f"Regiones soportadas: {regions}")
                
        except Exception:
            suggestions.append("Verificar parámetros de proveedor y tipo de VM")
        
        return suggestions