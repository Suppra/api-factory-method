# abstract_factory.py - Implementación del patrón Abstract Factory

from abc import ABC, abstractmethod
from resources import (
    NetworkResource, StorageResource, VMResource,
    AWSNetwork, AWSStorage, AWSVM,
    AzureNetwork, AzureStorage, AzureVM,
    GCPNetwork, GCPStorage, GCPVM,
    OnPremiseNetwork, OnPremiseStorage, OnPremiseVM
)

# ============= ABSTRACT FACTORY BASE =============

class CloudResourceFactory(ABC):
    """Factory abstracta para crear familias de recursos de nube"""
    
    @abstractmethod
    def create_network(self) -> NetworkResource:
        """Crear recurso de red específico del proveedor"""
        pass
    
    @abstractmethod
    def create_storage(self) -> StorageResource:
        """Crear recurso de almacenamiento específico del proveedor"""
        pass
    
    @abstractmethod
    def create_vm(self) -> VMResource:
        """Crear recurso de VM específico del proveedor"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Obtener el nombre del proveedor"""
        pass

# ============= CONCRETE FACTORIES =============

class AWSResourceFactory(CloudResourceFactory):
    """Factory concreta para recursos de AWS"""
    
    def create_network(self) -> NetworkResource:
        return AWSNetwork()
    
    def create_storage(self) -> StorageResource:
        return AWSStorage()
    
    def create_vm(self) -> VMResource:
        return AWSVM()
    
    def get_provider_name(self) -> str:
        return "AWS"

class AzureResourceFactory(CloudResourceFactory):
    """Factory concreta para recursos de Azure"""
    
    def create_network(self) -> NetworkResource:
        return AzureNetwork()
    
    def create_storage(self) -> StorageResource:
        return AzureStorage()
    
    def create_vm(self) -> VMResource:
        return AzureVM()
    
    def get_provider_name(self) -> str:
        return "Azure"

class GCPResourceFactory(CloudResourceFactory):
    """Factory concreta para recursos de Google Cloud"""
    
    def create_network(self) -> NetworkResource:
        return GCPNetwork()
    
    def create_storage(self) -> StorageResource:
        return GCPStorage()
    
    def create_vm(self) -> VMResource:
        return GCPVM()
    
    def get_provider_name(self) -> str:
        return "Google Cloud"

class OnPremiseResourceFactory(CloudResourceFactory):
    """Factory concreta para recursos On-Premise"""
    
    def create_network(self) -> NetworkResource:
        return OnPremiseNetwork()
    
    def create_storage(self) -> StorageResource:
        return OnPremiseStorage()
    
    def create_vm(self) -> VMResource:
        return OnPremiseVM()
    
    def get_provider_name(self) -> str:
        return "On-Premise"

# ============= FACTORY REGISTRY =============

class AbstractFactoryRegistry:
    """Registro de factories para diferentes proveedores"""
    
    _factories = {
        'aws': AWSResourceFactory,
        'azure': AzureResourceFactory,
        'gcp': GCPResourceFactory,
        'onpremise': OnPremiseResourceFactory
    }
    
    @classmethod
    def get_factory(cls, provider_name: str) -> CloudResourceFactory:
        """Obtener factory del proveedor especificado"""
        factory_class = cls._factories.get(provider_name.lower())
        if not factory_class:
            raise ValueError(f"Proveedor '{provider_name}' no soportado")
        return factory_class()
    
    @classmethod
    def register_factory(cls, provider_name: str, factory_class: type):
        """Registrar una nueva factory para extensibilidad"""
        cls._factories[provider_name.lower()] = factory_class
    
    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """Obtener lista de proveedores soportados"""
        return list(cls._factories.keys())