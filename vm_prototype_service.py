"""
Servicio de gestión de prototipos de VM que integra el patrón Prototype
con los patrones existentes (Factory Method, Abstract Factory, Builder+Director).
"""

from typing import Dict, Any, Optional, List
from models_extended import (
    VMSpecification, BuilderResponse, VMType, Provider
)
from vm_prototype import PrototypeRegistry, VMPrototype, ConcreteVMPrototype
from vm_construction_service import VMConstructionService
from vm_director import VMDirector
from vm_builder import ConcreteVMBuilder
from logger import safe_log


class VMPrototypeService:
    """
    Servicio principal para gestionar templates de VM usando el patrón Prototype.
    Integra la funcionalidad de clonación con el sistema de construcción existente.
    """
    
    def __init__(self):
        self.prototype_registry = PrototypeRegistry()
        self.construction_service = VMConstructionService()
        self.director = VMDirector()
        safe_log("VMPrototypeService: Servicio inicializado", {})
    
    def create_from_template(
        self,
        template_name: str,
        provider: Optional[Provider] = None,
        region: Optional[str] = None,
        customizations: Optional[Dict[str, Any]] = None
    ) -> BuilderResponse:
        """
        Crea una VM a partir de un template, opcionalmente personalizándola.
        
        Args:
            template_name: Nombre del template a usar
            provider: Proveedor objetivo (si es diferente al del template)
            region: Región objetivo (si es diferente al del template)
            customizations: Personalizaciones adicionales
            
        Returns:
            BuilderResponse con el resultado de la creación
        """
        safe_log(f"PrototypeService: Creando VM desde template '{template_name}'", {
            "provider": provider,
            "region": region,
            "has_customizations": bool(customizations)
        })
        
        try:
            # 1. Obtener y clonar el prototipo
            cloned_prototype = self.prototype_registry.clone_and_customize(
                template_name, 
                customizations or {}
            )
            
            if not cloned_prototype:
                return BuilderResponse(
                    success=False,
                    error=f"Template '{template_name}' no encontrado"
                )
            
            # 2. Obtener la especificación del prototipo clonado
            vm_spec = cloned_prototype.get_vm_specification()
            
            # 3. Aplicar overrides de proveedor y región si se especifican
            if provider and provider != vm_spec.provider:
                vm_spec = self._adapt_to_provider(vm_spec, provider)
            
            if region and region != vm_spec.region:
                vm_spec.region = region
                vm_spec.network_config.region = region
                vm_spec.storage_config.region = region
            
            # 4. Usar el builder para crear los recursos reales
            builder = ConcreteVMBuilder()
            result = (builder
                     .set_vm_config(vm_spec.vm_config)
                     .set_network_config(vm_spec.network_config)
                     .set_storage_config(vm_spec.storage_config)
                     .build())
            
            if result["success"]:
                return BuilderResponse(
                    success=True,
                    vm_specification=vm_spec,
                    created_resources=result["resources"]
                )
            else:
                return BuilderResponse(
                    success=False,
                    error=result["error"]
                )
                
        except Exception as e:
            safe_log(f"PrototypeService: Error creando desde template", {"error": str(e), "level": "error"})
            return BuilderResponse(
                success=False,
                error=f"Error interno: {str(e)}"
            )
    
    def register_template(
        self,
        template_name: str,
        vm_specification: VMSpecification,
        description: str,
        category: str = "custom",
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Registra un nuevo template en el registry.
        
        Args:
            template_name: Nombre único del template
            vm_specification: Especificación base del template
            description: Descripción del template
            category: Categoría del template
            tags: Tags adicionales
            
        Returns:
            Dict con resultado de la operación
        """
        safe_log(f"PrototypeService: Registrando template '{template_name}'", {
            "category": category,
            "provider": vm_specification.provider
        })
        
        try:
            prototype = ConcreteVMPrototype(
                template_name=template_name,
                description=description,
                vm_specification=vm_specification,
                category=category,
                tags=tags or {}
            )
            
            success = self.prototype_registry.register(template_name, prototype)
            
            if success:
                return {
                    "success": True,
                    "message": f"Template '{template_name}' registrado exitosamente",
                    "template_info": prototype.get_template_info()
                }
            else:
                return {
                    "success": False,
                    "error": f"Template '{template_name}' ya existe"
                }
                
        except Exception as e:
            safe_log(f"PrototypeService: Error registrando template", {"error": str(e), "level": "error"})
            return {
                "success": False,
                "error": f"Error registrando template: {str(e)}"
            }
    
    def list_available_templates(self, category: str = None) -> Dict[str, Any]:
        """
        Lista todos los templates disponibles.
        
        Args:
            category: Filtrar por categoría específica
            
        Returns:
            Dict con lista de templates y metadata
        """
        safe_log("PrototypeService: Listando templates disponibles", {"category": category})
        
        try:
            templates_info = self.prototype_registry.list_templates(category)
            
            # Enriquecer con estadísticas adicionales
            templates_info["statistics"] = self._generate_template_statistics()
            
            return {
                "success": True,
                **templates_info
            }
            
        except Exception as e:
            safe_log("PrototypeService: Error listando templates", {"error": str(e), "level": "error"})
            return {
                "success": False,
                "error": f"Error listando templates: {str(e)}"
            }
    
    def get_template_details(self, template_name: str) -> Dict[str, Any]:
        """
        Obtiene detalles completos de un template específico.
        
        Args:
            template_name: Nombre del template
            
        Returns:
            Dict con detalles del template o error
        """
        safe_log(f"PrototypeService: Obteniendo detalles de '{template_name}'", {})
        
        try:
            prototype = self.prototype_registry.get_prototype(template_name)
            
            if not prototype:
                return {
                    "success": False,
                    "error": f"Template '{template_name}' no encontrado"
                }
            
            template_info = prototype.get_template_info()
            vm_spec = prototype.get_vm_specification()
            
            # Calcular costo estimado usando el servicio existente
            cost_estimate = self.construction_service._estimate_cost(vm_spec)
            
            return {
                "success": True,
                "template_info": template_info,
                "vm_specification": vm_spec.model_dump(),
                "cost_estimate": cost_estimate,
                "compatible_providers": self._get_compatible_providers(vm_spec)
            }
            
        except Exception as e:
            safe_log(f"PrototypeService: Error obteniendo detalles", {"error": str(e), "level": "error"})
            return {
                "success": False,
                "error": f"Error obteniendo detalles: {str(e)}"
            }
    
    def delete_template(self, template_name: str) -> Dict[str, Any]:
        """
        Elimina un template del registry.
        
        Args:
            template_name: Nombre del template a eliminar
            
        Returns:
            Dict con resultado de la operación
        """
        safe_log(f"PrototypeService: Eliminando template '{template_name}'", {})
        
        try:
            success = self.prototype_registry.remove_template(template_name)
            
            if success:
                return {
                    "success": True,
                    "message": f"Template '{template_name}' eliminado exitosamente"
                }
            else:
                return {
                    "success": False,
                    "error": f"Template '{template_name}' no encontrado"
                }
                
        except Exception as e:
            safe_log(f"PrototypeService: Error eliminando template", {"error": str(e), "level": "error"})
            return {
                "success": False,
                "error": f"Error eliminando template: {str(e)}"
            }
    
    def create_template_from_existing_vm(
        self,
        template_name: str,
        base_vm_spec: VMSpecification,
        description: str,
        category: str = "derived",
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Crea un nuevo template basado en una VM existente.
        Útil para capturar configuraciones exitosas como templates reutilizables.
        
        Args:
            template_name: Nombre del nuevo template
            base_vm_spec: Especificación de la VM base
            description: Descripción del template
            category: Categoría del template
            tags: Tags adicionales
            
        Returns:
            Dict con resultado de la operación
        """
        safe_log(f"PrototypeService: Creando template desde VM existente '{template_name}'", {})
        
        # Agregar tags automáticos
        auto_tags = {
            "source": "existing_vm",
            "provider": str(base_vm_spec.provider),
            "vm_type": str(base_vm_spec.vm_type),
            "created_from": "production_vm"
        }
        
        if tags:
            auto_tags.update(tags)
        
        return self.register_template(
            template_name=template_name,
            vm_specification=base_vm_spec,
            description=description,
            category=category,
            tags=auto_tags
        )
    
    def _adapt_to_provider(self, vm_spec: VMSpecification, target_provider: Provider) -> VMSpecification:
        """
        Adapta una especificación de VM a un proveedor diferente.
        Utiliza el Director para obtener configuraciones equivalentes.
        """
        safe_log(f"PrototypeService: Adaptando de {vm_spec.provider} a {target_provider}", {})
        
        try:
            # Usar el Director para obtener configuración equivalente
            adapted_spec = self.director.get_vm_specification(
                provider=target_provider,
                vm_type=vm_spec.vm_type,
                region=vm_spec.region,
                custom_overrides={
                    "vcpus": vm_spec.vm_config.vcpus,
                    "memory_gb": vm_spec.vm_config.memory_gb
                }
            )
            
            return adapted_spec
            
        except Exception as e:
            safe_log(f"PrototypeService: Error adaptando proveedor", {"error": str(e), "level": "error"})
            # Si falla la adaptación, retornar la especificación original
            return vm_spec
    
    def _generate_template_statistics(self) -> Dict[str, Any]:
        """Genera estadísticas sobre los templates disponibles"""
        all_templates = self.prototype_registry.list_templates()
        
        stats = {
            "total_templates": all_templates["total"],
            "categories": len(all_templates["categories"]),
            "provider_distribution": {},
            "vm_type_distribution": {},
            "most_used_templates": []
        }
        
        for template in all_templates["templates"]:
            provider = template["provider"]
            vm_type = template["vm_type"]
            
            # Distribución por proveedor
            stats["provider_distribution"][provider] = (
                stats["provider_distribution"].get(provider, 0) + 1
            )
            
            # Distribución por tipo de VM
            stats["vm_type_distribution"][vm_type] = (
                stats["vm_type_distribution"].get(vm_type, 0) + 1
            )
            
            # Templates más utilizados
            stats["most_used_templates"].append({
                "name": template["template_name"],
                "usage_count": template["creation_count"],
                "category": template["category"]
            })
        
        # Ordenar por uso
        stats["most_used_templates"].sort(
            key=lambda x: x["usage_count"], 
            reverse=True
        )
        stats["most_used_templates"] = stats["most_used_templates"][:5]  # Top 5
        
        return stats
    
    def _get_compatible_providers(self, vm_spec: VMSpecification) -> List[str]:
        """
        Determina qué proveedores son compatibles con una especificación de VM.
        """
        compatible = []
        
        for provider in Provider:
            try:
                # Intentar adaptar la especificación al proveedor
                adapted_spec = self._adapt_to_provider(vm_spec, provider)
                if adapted_spec:
                    compatible.append(str(provider))
            except:
                # Si falla la adaptación, el proveedor no es compatible
                continue
        
        return compatible