# Diagrama UML - Patrones Factory Method y Abstract Factory

## Diagrama de Clases Completo

```mermaid
classDiagram
    %% Factory Method Pattern (Original)
    class VMFactory {
        <<Static>>
        +get_provider(name: str) Provider
        +register_provider(name: str, provider_cls)
    }
    
    class Provider {
        <<interface>>
        +create_vm(params: dict) tuple
    }
    
    VMFactory --> Provider : creates
    Provider <|-- AWSProvider
    Provider <|-- AzureProvider  
    Provider <|-- GCPProvider
    Provider <|-- OnPremiseProvider
    
    %% Abstract Factory Pattern (New)
    class CloudResourceFactory {
        <<abstract>>
        +create_network() NetworkResource
        +create_storage() StorageResource
        +create_vm() VMResource
        +get_provider_name() str
    }
    
    class NetworkResource {
        <<abstract>>
        +create_network(params: dict) tuple
        +get_network_info() dict
    }
    
    class StorageResource {
        <<abstract>>  
        +create_storage(params: dict) tuple
        +get_storage_info() dict
    }
    
    class VMResource {
        <<abstract>>
        +create_vm(params: dict, network_id: str, storage_id: str) tuple
        +get_vm_info() dict
    }
    
    %% Concrete Factories
    CloudResourceFactory <|-- AWSResourceFactory
    CloudResourceFactory <|-- AzureResourceFactory
    CloudResourceFactory <|-- GCPResourceFactory
    CloudResourceFactory <|-- OnPremiseResourceFactory
    
    %% AWS Family
    AWSResourceFactory --> AWSNetwork : creates
    AWSResourceFactory --> AWSStorage : creates
    AWSResourceFactory --> AWSVM : creates
    
    NetworkResource <|-- AWSNetwork
    StorageResource <|-- AWSStorage  
    VMResource <|-- AWSVM
    
    %% Azure Family
    AzureResourceFactory --> AzureNetwork : creates
    AzureResourceFactory --> AzureStorage : creates
    AzureResourceFactory --> AzureVM : creates
    
    NetworkResource <|-- AzureNetwork
    StorageResource <|-- AzureStorage
    VMResource <|-- AzureVM
    
    %% GCP Family
    GCPResourceFactory --> GCPNetwork : creates
    GCPResourceFactory --> GCPStorage : creates
    GCPResourceFactory --> GCPVM : creates
    
    NetworkResource <|-- GCPNetwork
    StorageResource <|-- GCPStorage
    VMResource <|-- GCPVM
    
    %% OnPremise Family
    OnPremiseResourceFactory --> OnPremiseNetwork : creates
    OnPremiseResourceFactory --> OnPremiseStorage : creates
    OnPremiseResourceFactory --> OnPremiseVM : creates
    
    NetworkResource <|-- OnPremiseNetwork
    StorageResource <|-- OnPremiseStorage
    VMResource <|-- OnPremiseVM
    
    %% Services
    class ResourceProvisioningService {
        +provision_resource_family(provider: str, vm_params: dict, network_params: dict, storage_params: dict) ResourceFamilyResponse
        +get_supported_providers() list
    }
    
    class AbstractFactoryRegistry {
        +register_factory(name: str, factory_cls)
        +get_factory(name: str) CloudResourceFactory
        +get_supported_providers() list
    }
    
    ResourceProvisioningService --> AbstractFactoryRegistry : uses
    AbstractFactoryRegistry --> CloudResourceFactory : manages
    
    %% API Layer
    class FastAPI {
        +provision_vm(request: VMRequest) VMResponse
        +provision_resource_family(request: ResourceFamilyRequest) ResourceFamilyResponse
        +get_supported_providers() dict
    }
    
    FastAPI --> VMFactory : uses
    FastAPI --> ResourceProvisioningService : uses
```

## Diagrama de Secuencia - Aprovisionamiento de Familia de Recursos

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant ResourceProvisioningService
    participant AbstractFactoryRegistry
    participant AWSResourceFactory
    participant AWSNetwork
    participant AWSStorage
    participant AWSVM
    
    Client->>API: POST /provision_resource_family
    API->>ResourceProvisioningService: provision_resource_family()
    ResourceProvisioningService->>AbstractFactoryRegistry: get_factory("aws")
    AbstractFactoryRegistry->>ResourceProvisioningService: AWSResourceFactory
    
    ResourceProvisioningService->>AWSResourceFactory: create_network()
    AWSResourceFactory->>AWSNetwork: new()
    ResourceProvisioningService->>AWSNetwork: create_network(params)
    AWSNetwork-->>ResourceProvisioningService: (true, "aws-network-123", null)
    
    ResourceProvisioningService->>AWSResourceFactory: create_storage()
    AWSResourceFactory->>AWSStorage: new()
    ResourceProvisioningService->>AWSStorage: create_storage(params)
    AWSStorage-->>ResourceProvisioningService: (true, "aws-storage-456", null)
    
    ResourceProvisioningService->>AWSResourceFactory: create_vm()
    AWSResourceFactory->>AWSVM: new()
    ResourceProvisioningService->>AWSVM: create_vm(params, network_id, storage_id)
    AWSVM-->>ResourceProvisioningService: (true, "aws-vm-789", null)
    
    ResourceProvisioningService-->>API: ResourceFamilyResponse
    API-->>Client: JSON Response
```

## Patrón Strategy - Selección de Factory

```mermaid
classDiagram
    class AbstractFactoryRegistry {
        -factories: dict
        +register_factory(name, factory)
        +get_factory(name) CloudResourceFactory
    }
    
    AbstractFactoryRegistry --> CloudResourceFactory : selects strategy
    
    note for AbstractFactoryRegistry : "Implementa Strategy Pattern para seleccionar la factory apropiada según el proveedor"
```