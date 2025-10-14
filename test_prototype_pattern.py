"""
Test suite para el patrón Prototype.
Valida la funcionalidad de clonación, personalización y gestión de templates.
"""

import pytest
from vm_prototype import ConcreteVMPrototype, PrototypeRegistry
from vm_prototype_service import VMPrototypeService
from models_extended import (
    VMSpecification, VirtualMachineConfig, NetworkConfig, StorageConfig,
    VMType, Provider
)


class TestVMPrototype:
    """Tests para la implementación del prototipo de VM"""
    
    def test_prototype_creation(self):
        """Test: Crear un prototipo básico"""
        vm_spec = VMSpecification(
            vm_type=VMType.STANDARD,
            provider=Provider.AWS,
            region="us-east-1",
            vm_config=VirtualMachineConfig(
                provider=Provider.AWS,
                vcpus=2,
                memory_gb=4,
                instance_type="t3.medium"
            ),
            network_config=NetworkConfig(
                provider=Provider.AWS,
                region="us-east-1",
                firewall_rules=["SSH"]
            ),
            storage_config=StorageConfig(
                provider=Provider.AWS,
                region="us-east-1",
                size_gb=20
            )
        )
        
        prototype = ConcreteVMPrototype(
            template_name="test-template",
            description="Template de prueba",
            vm_specification=vm_spec
        )
        
        assert prototype.template_name == "test-template"
        assert prototype.description == "Template de prueba"
        assert prototype.vm_specification.provider == Provider.AWS
        assert prototype.creation_count == 0
    
    def test_prototype_clone(self):
        """Test: Clonar un prototipo"""
        vm_spec = VMSpecification(
            vm_type=VMType.STANDARD,
            provider=Provider.AWS,
            region="us-east-1",
            vm_config=VirtualMachineConfig(
                provider=Provider.AWS,
                vcpus=2,
                memory_gb=4,
                instance_type="t3.medium"
            ),
            network_config=NetworkConfig(
                provider=Provider.AWS,
                region="us-east-1",
                firewall_rules=["SSH"]
            ),
            storage_config=StorageConfig(
                provider=Provider.AWS,
                region="us-east-1",
                size_gb=20
            )
        )
        
        original = ConcreteVMPrototype(
            template_name="original",
            description="Prototipo original",
            vm_specification=vm_spec
        )
        
        cloned = original.clone()
        
        # Verificar que son instancias diferentes
        assert id(original) != id(cloned)
        assert id(original.vm_specification) != id(cloned.vm_specification)
        
        # Verificar que el contenido es igual
        assert original.template_name == cloned.template_name
        assert original.vm_specification.provider == cloned.vm_specification.provider
        
        # Verificar que el contador se incrementó
        assert original.creation_count == 1
        assert cloned.creation_count == 0
    
    def test_prototype_customize(self):
        """Test: Personalizar un prototipo clonado"""
        vm_spec = VMSpecification(
            vm_type=VMType.STANDARD,
            provider=Provider.AWS,
            region="us-east-1",
            vm_config=VirtualMachineConfig(
                provider=Provider.AWS,
                vcpus=2,
                memory_gb=4,
                instance_type="t3.medium"
            ),
            network_config=NetworkConfig(
                provider=Provider.AWS,
                region="us-east-1",
                firewall_rules=["SSH"]
            ),
            storage_config=StorageConfig(
                provider=Provider.AWS,
                region="us-east-1",
                size_gb=20
            )
        )
        
        prototype = ConcreteVMPrototype(
            template_name="customizable",
            description="Prototipo personalizable",
            vm_specification=vm_spec
        )
        
        cloned = prototype.clone()
        
        # Personalizar diferentes aspectos
        customizations = {
            "vm_config": {
                "vcpus": 4,
                "memory_gb": 8,
                "instance_type": "t3.large"
            },
            "network_config": {
                "firewall_rules": ["SSH", "HTTP", "HTTPS"]
            },
            "storage_config": {
                "size_gb": 50
            },
            "region": "us-west-2",
            "tags": {"environment": "testing"}
        }
        
        cloned.customize(customizations)
        
        # Verificar personalizaciones aplicadas
        assert cloned.vm_specification.vm_config.vcpus == 4
        assert cloned.vm_specification.vm_config.memory_gb == 8
        assert cloned.vm_specification.vm_config.instance_type == "t3.large"
        assert "HTTP" in cloned.vm_specification.network_config.firewall_rules
        assert cloned.vm_specification.storage_config.size_gb == 50
        assert cloned.vm_specification.region == "us-west-2"
        assert cloned.tags["environment"] == "testing"
        
        # Verificar que el original no cambió
        assert prototype.vm_specification.vm_config.vcpus == 2
        assert prototype.vm_specification.region == "us-east-1"
    
    def test_template_info(self):
        """Test: Obtener información del template"""
        vm_spec = VMSpecification(
            vm_type=VMType.MEMORY_OPTIMIZED,
            provider=Provider.AZURE,
            region="eastus",
            vm_config=VirtualMachineConfig(
                provider=Provider.AZURE,
                vcpus=8,
                memory_gb=32,
                memory_optimization=True
            ),
            network_config=NetworkConfig(
                provider=Provider.AZURE,
                region="eastus",
                firewall_rules=["SSH"]
            ),
            storage_config=StorageConfig(
                provider=Provider.AZURE,
                region="eastus",
                size_gb=100
            )
        )
        
        prototype = ConcreteVMPrototype(
            template_name="memory-optimized",
            description="Template optimizado para memoria",
            vm_specification=vm_spec,
            category="databases",
            tags={"purpose": "database", "tier": "production"}
        )
        
        info = prototype.get_template_info()
        
        assert info["template_name"] == "memory-optimized"
        assert info["category"] == "databases"
        assert info["provider"] == Provider.AZURE
        assert info["vm_type"] == VMType.MEMORY_OPTIMIZED
        assert info["specifications"]["vcpus"] == 8
        assert info["specifications"]["memory_gb"] == 32
        assert info["tags"]["purpose"] == "database"


class TestPrototypeRegistry:
    """Tests para el registro de prototipos"""
    
    def test_registry_initialization(self):
        """Test: Inicialización del registry con templates predeterminados"""
        registry = PrototypeRegistry()
        
        # Verificar que se crearon templates predeterminados
        templates = registry.list_templates()
        assert templates["total"] > 0
        
        # Verificar que existen templates específicos
        assert registry.get_prototype("web-server-standard") is not None
        assert registry.get_prototype("database-optimized") is not None
        assert registry.get_prototype("analytics-compute") is not None
    
    def test_register_new_template(self):
        """Test: Registrar un nuevo template"""
        registry = PrototypeRegistry()
        
        vm_spec = VMSpecification(
            vm_type=VMType.COMPUTE_OPTIMIZED,
            provider=Provider.GCP,
            region="us-central1",
            vm_config=VirtualMachineConfig(
                provider=Provider.GCP,
                vcpus=16,
                memory_gb=16,
                disk_optimization=True
            ),
            network_config=NetworkConfig(
                provider=Provider.GCP,
                region="us-central1",
                firewall_rules=["SSH"]
            ),
            storage_config=StorageConfig(
                provider=Provider.GCP,
                region="us-central1",
                size_gb=200
            )
        )
        
        prototype = ConcreteVMPrototype(
            template_name="custom-compute",
            description="Template computacional personalizado",
            vm_specification=vm_spec,
            category="compute"
        )
        
        success = registry.register("custom-compute", prototype)
        
        assert success is True
        assert registry.get_prototype("custom-compute") is not None
        
        # Intentar registrar el mismo nombre debería fallar
        duplicate_success = registry.register("custom-compute", prototype)
        assert duplicate_success is False
    
    def test_clone_and_customize(self):
        """Test: Clonar y personalizar en una operación"""
        registry = PrototypeRegistry()
        
        customizations = {
            "vm_config": {"vcpus": 8, "memory_gb": 16},
            "region": "us-west-1",
            "tags": {"environment": "development"}
        }
        
        cloned = registry.clone_and_customize("web-server-standard", customizations)
        
        assert cloned is not None
        assert cloned.vm_specification.vm_config.vcpus == 8
        assert cloned.vm_specification.region == "us-west-1"
        assert cloned.tags["environment"] == "development"
        
        # Intentar clonar template inexistente
        non_existent = registry.clone_and_customize("non-existent", {})
        assert non_existent is None
    
    def test_list_templates_by_category(self):
        """Test: Listar templates por categoría"""
        registry = PrototypeRegistry()
        
        all_templates = registry.list_templates()
        web_templates = registry.list_templates("web-services")
        db_templates = registry.list_templates("databases")
        
        assert all_templates["total"] >= web_templates["total"]
        assert len(web_templates["templates"]) > 0
        assert len(db_templates["templates"]) > 0
        
        # Verificar categoría específica
        for template in web_templates["templates"]:
            assert template["category"] == "web-services"
    
    def test_remove_template(self):
        """Test: Eliminar template del registry"""
        registry = PrototypeRegistry()
        
        # Agregar template temporal
        vm_spec = VMSpecification(
            vm_type=VMType.STANDARD,
            provider=Provider.AWS,
            region="us-east-1",
            vm_config=VirtualMachineConfig(
                provider=Provider.AWS,
                vcpus=1,
                memory_gb=1
            ),
            network_config=NetworkConfig(
                provider=Provider.AWS,
                region="us-east-1",
                firewall_rules=[]
            ),
            storage_config=StorageConfig(
                provider=Provider.AWS,
                region="us-east-1",
                size_gb=10
            )
        )
        
        temp_prototype = ConcreteVMPrototype(
            template_name="temp-template",
            description="Template temporal",
            vm_specification=vm_spec
        )
        
        registry.register("temp-template", temp_prototype)
        
        # Verificar que existe
        assert registry.get_prototype("temp-template") is not None
        
        # Eliminar
        removed = registry.remove_template("temp-template")
        assert removed is True
        
        # Verificar que ya no existe
        assert registry.get_prototype("temp-template") is None
        
        # Intentar eliminar template inexistente
        not_removed = registry.remove_template("non-existent")
        assert not_removed is False


class TestVMPrototypeService:
    """Tests para el servicio de gestión de prototipos"""
    
    def test_service_initialization(self):
        """Test: Inicialización del servicio"""
        service = VMPrototypeService()
        
        assert service.prototype_registry is not None
        assert service.construction_service is not None
        assert service.director is not None
    
    def test_list_available_templates(self):
        """Test: Listar templates disponibles"""
        service = VMPrototypeService()
        
        result = service.list_available_templates()
        
        assert result["success"] is True
        assert result["total"] > 0
        assert "templates" in result
        assert "statistics" in result
        
        # Verificar estadísticas
        stats = result["statistics"]
        assert "total_templates" in stats
        assert "categories" in stats
        assert "provider_distribution" in stats
    
    def test_get_template_details(self):
        """Test: Obtener detalles de template específico"""
        service = VMPrototypeService()
        
        result = service.get_template_details("web-server-standard")
        
        assert result["success"] is True
        assert "template_info" in result
        assert "vm_specification" in result
        assert "cost_estimate" in result
        assert "compatible_providers" in result
        
        # Verificar template inexistente
        not_found = service.get_template_details("non-existent")
        assert not_found["success"] is False
        assert "error" in not_found
    
    def test_register_new_template(self):
        """Test: Registrar nuevo template"""
        service = VMPrototypeService()
        
        vm_spec = VMSpecification(
            vm_type=VMType.STANDARD,
            provider=Provider.ONPREMISE,
            region="datacenter-1",
            vm_config=VirtualMachineConfig(
                provider=Provider.ONPREMISE,
                vcpus=4,
                memory_gb=8,
                cpu=4,
                ram=8,
                hypervisor="vmware"
            ),
            network_config=NetworkConfig(
                provider=Provider.ONPREMISE,
                region="datacenter-1",
                firewall_rules=["SSH"],
                network_type="internal"
            ),
            storage_config=StorageConfig(
                provider=Provider.ONPREMISE,
                region="datacenter-1",
                size_gb=50,
                storage_type="ssd"
            )
        )
        
        result = service.register_template(
            template_name="onpremise-test",
            vm_specification=vm_spec,
            description="Template de prueba on-premise",
            category="testing",
            tags={"environment": "test", "provider": "onpremise"}
        )
        
        assert result["success"] is True
        assert "template_info" in result
        
        # Verificar que se puede obtener después
        details = service.get_template_details("onpremise-test")
        assert details["success"] is True
    
    def test_delete_template(self):
        """Test: Eliminar template"""
        service = VMPrototypeService()
        
        # Crear template temporal primero
        vm_spec = VMSpecification(
            vm_type=VMType.STANDARD,
            provider=Provider.AWS,
            region="us-east-1",
            vm_config=VirtualMachineConfig(
                provider=Provider.AWS,
                vcpus=1,
                memory_gb=1
            ),
            network_config=NetworkConfig(
                provider=Provider.AWS,
                region="us-east-1",
                firewall_rules=[]
            ),
            storage_config=StorageConfig(
                provider=Provider.AWS,
                region="us-east-1",
                size_gb=10
            )
        )
        
        service.register_template(
            template_name="temp-for-deletion",
            vm_specification=vm_spec,
            description="Template temporal para eliminar"
        )
        
        # Eliminar
        result = service.delete_template("temp-for-deletion")
        assert result["success"] is True
        
        # Verificar que ya no existe
        details = service.get_template_details("temp-for-deletion")
        assert details["success"] is False
        
        # Intentar eliminar template inexistente
        not_found = service.delete_template("non-existent")
        assert not_found["success"] is False
    
    def test_create_template_from_existing_vm(self):
        """Test: Crear template desde VM existente"""
        service = VMPrototypeService()
        
        vm_spec = VMSpecification(
            vm_type=VMType.MEMORY_OPTIMIZED,
            provider=Provider.AZURE,
            region="westus2",
            vm_config=VirtualMachineConfig(
                provider=Provider.AZURE,
                vcpus=8,
                memory_gb=64,
                memory_optimization=True,
                size="Standard_E8s_v3",
                resource_group="production-rg"
            ),
            network_config=NetworkConfig(
                provider=Provider.AZURE,
                region="westus2",
                firewall_rules=["SSH", "HTTPS"],
                public_ip=False
            ),
            storage_config=StorageConfig(
                provider=Provider.AZURE,
                region="westus2",
                size_gb=200,
                storage_type="Premium_SSD",
                encrypted=True
            )
        )
        
        result = service.create_template_from_existing_vm(
            template_name="production-memory-template",
            base_vm_spec=vm_spec,
            description="Template basado en VM de producción",
            category="production",
            tags={"source_environment": "production", "optimization": "memory"}
        )
        
        assert result["success"] is True
        assert "template_info" in result
        
        # Verificar que el template tiene los tags automáticos
        details = service.get_template_details("production-memory-template")
        template_info = details["template_info"]
        assert template_info["tags"]["source"] == "existing_vm"
        assert template_info["tags"]["created_from"] == "production_vm"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])