"""
Implementación del patrón Prototype para templates de VM.
Permite clonar configuraciones predefinidas y personalizarlas según necesidades específicas.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from copy import deepcopy
import json
from models_extended import (
    VMSpecification, VirtualMachineConfig, NetworkConfig, StorageConfig,
    VMType, Provider
)
from logger import safe_log


class VMPrototype(ABC):
    """
    Interfaz abstracta para prototipos de VM.
    Define el contrato para clonación y personalización.
    """
    
    @abstractmethod
    def clone(self) -> 'VMPrototype':
        """Crea una copia profunda del prototipo"""
        pass
    
    @abstractmethod
    def customize(self, customizations: Dict[str, Any]) -> 'VMPrototype':
        """Personaliza el prototipo clonado con parámetros específicos"""
        pass
    
    @abstractmethod
    def get_vm_specification(self) -> VMSpecification:
        """Obtiene la especificación de VM del prototipo"""
        pass
    
    @abstractmethod
    def get_template_info(self) -> Dict[str, Any]:
        """Obtiene información descriptiva del template"""
        pass


class ConcreteVMPrototype(VMPrototype):
    """
    Implementación concreta del prototipo de VM.
    Encapsula una configuración completa de VM que puede ser clonada y personalizada.
    """
    
    def __init__(
        self,
        template_name: str,
        description: str,
        vm_specification: VMSpecification,
        category: str = "general",
        tags: Optional[Dict[str, str]] = None
    ):
        self.template_name = template_name
        self.description = description
        self.vm_specification = vm_specification
        self.category = category
        self.tags = tags or {}
        self.creation_count = 0  # Contador de veces que se ha clonado
        
        safe_log(f"Prototype: Template '{template_name}' creado", {
            "category": category,
            "provider": vm_specification.provider,
            "vm_type": vm_specification.vm_type
        })
    
    def clone(self) -> 'ConcreteVMPrototype':
        """
        Crea una copia profunda del prototipo.
        Utiliza deepcopy para evitar referencias compartidas.
        """
        safe_log(f"Prototype: Clonando template '{self.template_name}'", {})
        
        # Realizar copia profunda de la especificación
        cloned_spec = VMSpecification(
            vm_type=self.vm_specification.vm_type,
            provider=self.vm_specification.provider,
            region=self.vm_specification.region,
            vm_config=VirtualMachineConfig(**self.vm_specification.vm_config.model_dump()),
            network_config=NetworkConfig(**self.vm_specification.network_config.model_dump()),
            storage_config=StorageConfig(**self.vm_specification.storage_config.model_dump())
        )
        
        # Crear nuevo prototipo con la especificación clonada
        cloned_prototype = ConcreteVMPrototype(
            template_name=self.template_name,
            description=self.description,
            vm_specification=cloned_spec,
            category=self.category,
            tags=deepcopy(self.tags)
        )
        
        # Incrementar contador del prototipo original
        self.creation_count += 1
        
        return cloned_prototype
    
    def customize(self, customizations: Dict[str, Any]) -> 'ConcreteVMPrototype':
        """
        Personaliza el prototipo con parámetros específicos.
        Permite modificar VM, red y almacenamiento de forma granular.
        """
        safe_log(f"Prototype: Personalizando template '{self.template_name}'", customizations)
        
        # Personalizar configuración de VM
        if "vm_config" in customizations:
            vm_updates = customizations["vm_config"]
            current_config = self.vm_specification.vm_config.model_dump()
            current_config.update(vm_updates)
            self.vm_specification.vm_config = VirtualMachineConfig(**current_config)
        
        # Personalizar configuración de red
        if "network_config" in customizations:
            network_updates = customizations["network_config"]
            current_config = self.vm_specification.network_config.model_dump()
            current_config.update(network_updates)
            self.vm_specification.network_config = NetworkConfig(**current_config)
        
        # Personalizar configuración de almacenamiento
        if "storage_config" in customizations:
            storage_updates = customizations["storage_config"]
            current_config = self.vm_specification.storage_config.model_dump()
            current_config.update(storage_updates)
            self.vm_specification.storage_config = StorageConfig(**current_config)
        
        # Personalizar metadatos del template
        if "region" in customizations:
            self.vm_specification.region = customizations["region"]
        
        # Actualizar tags si se proporcionan
        if "tags" in customizations:
            self.tags.update(customizations["tags"])
        
        return self
    
    def get_vm_specification(self) -> VMSpecification:
        """Retorna la especificación actual de la VM"""
        return self.vm_specification
    
    def get_template_info(self) -> Dict[str, Any]:
        """Retorna información descriptiva del template"""
        return {
            "template_name": self.template_name,
            "description": self.description,
            "category": self.category,
            "provider": self.vm_specification.provider,
            "vm_type": self.vm_specification.vm_type,
            "region": self.vm_specification.region,
            "tags": self.tags,
            "creation_count": self.creation_count,
            "specifications": {
                "vcpus": self.vm_specification.vm_config.vcpus,
                "memory_gb": self.vm_specification.vm_config.memory_gb,
                "storage_gb": self.vm_specification.storage_config.size_gb,
                "network_type": getattr(self.vm_specification.network_config, 'network_type', 'standard')
            }
        }


class PrototypeRegistry:
    """
    Registry que gestiona todos los prototipos disponibles.
    Implementa el patrón Registry para organizar y acceder a los prototipos.
    """
    
    def __init__(self):
        self._prototypes: Dict[str, VMPrototype] = {}
        self._categories: Dict[str, list[str]] = {}
        self._initialize_default_templates()
    
    def register(self, name: str, prototype: VMPrototype) -> bool:
        """
        Registra un nuevo prototipo en el registry.
        
        Args:
            name: Nombre único del template
            prototype: Instancia del prototipo a registrar
            
        Returns:
            bool: True si se registró correctamente, False si ya existía
        """
        if name in self._prototypes:
            safe_log(f"PrototypeRegistry: Template '{name}' ya existe", {"level": "warning"})
            return False
        
        self._prototypes[name] = prototype
        
        # Organizar por categoría
        template_info = prototype.get_template_info()
        category = template_info.get("category", "general")
        
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(name)
        
        safe_log(f"PrototypeRegistry: Template '{name}' registrado en categoría '{category}'", {})
        return True
    
    def get_prototype(self, name: str) -> Optional[VMPrototype]:
        """
        Obtiene un prototipo por nombre.
        
        Args:
            name: Nombre del template
            
        Returns:
            VMPrototype o None si no existe
        """
        return self._prototypes.get(name)
    
    def clone_and_customize(
        self, 
        name: str, 
        customizations: Dict[str, Any] = None
    ) -> Optional[VMPrototype]:
        """
        Clona un prototipo y lo personaliza en una sola operación.
        
        Args:
            name: Nombre del template a clonar
            customizations: Diccionario con personalizaciones
            
        Returns:
            VMPrototype personalizado o None si el template no existe
        """
        prototype = self.get_prototype(name)
        if not prototype:
            safe_log(f"PrototypeRegistry: Template '{name}' no encontrado", {"level": "error"})
            return None
        
        cloned = prototype.clone()
        
        if customizations:
            cloned.customize(customizations)
        
        return cloned
    
    def list_templates(self, category: str = None) -> Dict[str, Any]:
        """
        Lista todos los templates disponibles, opcionalmente filtrados por categoría.
        
        Args:
            category: Categoría opcional para filtrar
            
        Returns:
            Dict con información de templates disponibles
        """
        if category and category not in self._categories:
            return {"templates": [], "total": 0}
        
        template_names = (
            self._categories[category] if category 
            else list(self._prototypes.keys())
        )
        
        templates = []
        for name in template_names:
            prototype = self._prototypes[name]
            templates.append(prototype.get_template_info())
        
        return {
            "templates": templates,
            "total": len(templates),
            "categories": list(self._categories.keys()) if not category else [category]
        }
    
    def remove_template(self, name: str) -> bool:
        """
        Elimina un template del registry.
        
        Args:
            name: Nombre del template a eliminar
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        if name not in self._prototypes:
            return False
        
        # Obtener categoría antes de eliminar
        template_info = self._prototypes[name].get_template_info()
        category = template_info.get("category", "general")
        
        # Eliminar del registry principal
        del self._prototypes[name]
        
        # Eliminar de la categoría
        if category in self._categories and name in self._categories[category]:
            self._categories[category].remove(name)
            
            # Si la categoría queda vacía, eliminarla
            if not self._categories[category]:
                del self._categories[category]
        
        safe_log(f"PrototypeRegistry: Template '{name}' eliminado", {})
        return True
    
    def _initialize_default_templates(self):
        """Inicializa templates predeterminados para casos de uso comunes"""
        
        # Template 1: Web Server Standard
        web_server_spec = VMSpecification(
            vm_type=VMType.STANDARD,
            provider=Provider.AWS,
            region="us-east-1",
            vm_config=VirtualMachineConfig(
                provider=Provider.AWS,
                vcpus=2,
                memory_gb=4,
                instance_type="t3.medium",
                ami="ami-0c02fb55956c7d316",
                key_pair_name="web-server-key"
            ),
            network_config=NetworkConfig(
                provider=Provider.AWS,
                region="us-east-1",
                firewall_rules=["HTTP", "HTTPS", "SSH"],
                public_ip=True,
                network_type="public"
            ),
            storage_config=StorageConfig(
                provider=Provider.AWS,
                region="us-east-1",
                size_gb=20,
                storage_type="gp3",
                iops=3000
            )
        )
        
        web_server_template = ConcreteVMPrototype(
            template_name="web-server-standard",
            description="Servidor web estándar con balanceador de carga y almacenamiento optimizado",
            vm_specification=web_server_spec,
            category="web-services",
            tags={"purpose": "web-server", "tier": "frontend", "environment": "production"}
        )
        
        # Template 2: Database Server
        db_server_spec = VMSpecification(
            vm_type=VMType.MEMORY_OPTIMIZED,
            provider=Provider.AWS,
            region="us-east-1",
            vm_config=VirtualMachineConfig(
                provider=Provider.AWS,
                vcpus=4,
                memory_gb=32,
                memory_optimization=True,
                instance_type="r5.xlarge",
                ami="ami-0c02fb55956c7d316",
                key_pair_name="db-server-key"
            ),
            network_config=NetworkConfig(
                provider=Provider.AWS,
                region="us-east-1",
                firewall_rules=["MySQL", "PostgreSQL", "SSH"],
                public_ip=False,
                network_type="private"
            ),
            storage_config=StorageConfig(
                provider=Provider.AWS,
                region="us-east-1",
                size_gb=100,
                storage_type="io2",
                iops=10000,
                encrypted=True
            )
        )
        
        db_server_template = ConcreteVMPrototype(
            template_name="database-optimized",
            description="Servidor de base de datos optimizado para memoria con almacenamiento de alto rendimiento",
            vm_specification=db_server_spec,
            category="databases",
            tags={"purpose": "database", "tier": "backend", "performance": "high"}
        )
        
        # Template 3: Analytics/Compute
        analytics_spec = VMSpecification(
            vm_type=VMType.COMPUTE_OPTIMIZED,
            provider=Provider.AWS,
            region="us-east-1",
            vm_config=VirtualMachineConfig(
                provider=Provider.AWS,
                vcpus=16,
                memory_gb=16,
                disk_optimization=True,
                instance_type="c5.4xlarge",
                ami="ami-0c02fb55956c7d316",
                key_pair_name="compute-key"
            ),
            network_config=NetworkConfig(
                provider=Provider.AWS,
                region="us-east-1",
                firewall_rules=["SSH", "Custom-8080"],
                public_ip=True,
                network_type="public"
            ),
            storage_config=StorageConfig(
                provider=Provider.AWS,
                region="us-east-1",
                size_gb=200,
                storage_type="gp3",
                iops=5000
            )
        )
        
        analytics_template = ConcreteVMPrototype(
            template_name="analytics-compute",
            description="Servidor optimizado para procesamiento y análisis de datos intensivo",
            vm_specification=analytics_spec,
            category="analytics",
            tags={"purpose": "analytics", "workload": "compute-intensive", "scale": "horizontal"}
        )
        
        # Registrar templates predeterminados
        self.register("web-server-standard", web_server_template)
        self.register("database-optimized", db_server_template)
        self.register("analytics-compute", analytics_template)
        
        safe_log("PrototypeRegistry: Templates predeterminados inicializados", {
            "total_templates": len(self._prototypes),
            "categories": list(self._categories.keys())
        })