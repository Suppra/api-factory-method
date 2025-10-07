# DOCUMENTACIÓN ACADÉMICA - PATRÓN ABSTRACT FACTORY

## Introducción

Esta implementación extiende el proyecto original para aplicar el **patrón Abstract Factory**, permitiendo el aprovisionamiento coherente de **familias de recursos** (VM + Red + Disco) en diferentes proveedores de nube.

## Patrón Abstract Factory vs Factory Method

### Factory Method (Implementación Original)
- **Propósito**: Crear objetos individuales (solo VMs)
- **Estructura**: Una factory que crea un tipo de producto
- **Extensibilidad**: Agregar nuevos proveedores para VMs

### Abstract Factory (Nueva Implementación) 
- **Propósito**: Crear familias de objetos relacionados (VM + Red + Disco)
- **Estructura**: Multiple factories que crean familias de productos
- **Consistencia**: Garantiza que todos los recursos pertenezcan al mismo proveedor
- **Extensibilidad**: Agregar nuevos proveedores con familias completas de recursos

## Estructura del Código

### 1. resources.py
**Responsabilidad**: Define las interfaces abstractas y las implementaciones concretas para cada tipo de recurso.

**Clases Abstractas**:
- `NetworkResource`: Interface para recursos de red
- `StorageResource`: Interface para recursos de almacenamiento  
- `VMResource`: Interface para recursos de máquinas virtuales

**Implementaciones por Proveedor**:
- **AWS**: `AWSNetwork`, `AWSStorage`, `AWSVM`
- **Azure**: `AzureNetwork`, `AzureStorage`, `AzureVM`
- **GCP**: `GCPNetwork`, `GCPStorage`, `GCPVM`
- **OnPremise**: `OnPremiseNetwork`, `OnPremiseStorage`, `OnPremiseVM`

### 2. abstract_factory.py
**Responsabilidad**: Implementa el patrón Abstract Factory para crear familias de recursos.

**Clase Abstracta**:
- `CloudResourceFactory`: Factory abstracta que define métodos para crear red, almacenamiento y VM

**Factories Concretas**:
- `AWSResourceFactory`: Crea recursos específicos de AWS
- `AzureResourceFactory`: Crea recursos específicos de Azure
- `GCPResourceFactory`: Crea recursos específicos de GCP
- `OnPremiseResourceFactory`: Crea recursos específicos de On-Premise

**Registry**:
- `AbstractFactoryRegistry`: Registro centralizado de factories para extensibilidad

### 3. resource_provisioner.py
**Responsabilidad**: Servicio de aprovisionamiento que coordina la creación de familias de recursos.

**Funcionalidades**:
- Aprovisionamiento atómico (si falla un recurso, no se crean los demás)
- Consistencia de proveedor (todos los recursos del mismo proveedor)
- Orden de creación: Red → Almacenamiento → VM
- Logging seguro de operaciones

### 4. models.py (Actualizado)
**Responsabilidad**: Modelos de datos para solicitudes y respuestas.

**Nuevos Modelos**:
- `ResourceFamilyRequest`: Solicitud para familia de recursos
- `ResourceInfo`: Información de recursos creados
- `ResourceFamilyResponse`: Respuesta con familia de recursos

### 5. api.py (Actualizado)
**Responsabilidad**: Endpoints REST para ambos patrones.

**Endpoints**:
- `/provision_vm`: Factory Method original (compatibilidad)
- `/provision_resource_family`: Abstract Factory (nueva funcionalidad)
- `/supported_providers`: Lista de proveedores disponibles

## Principios SOLID Aplicados

### 1. Single Responsibility Principle (SRP)
- Cada clase tiene una responsabilidad específica
- `NetworkResource` solo maneja redes
- `StorageResource` solo maneja almacenamiento
- `VMResource` solo maneja VMs

### 2. Open/Closed Principle (OCP)
- Extensible para nuevos proveedores sin modificar código existente
- `AbstractFactoryRegistry.register_factory()` permite agregar proveedores

### 3. Liskov Substitution Principle (LSP)
- Todas las implementaciones concretas pueden sustituir a sus abstracciones
- `AWSNetwork` puede sustituir a `NetworkResource`

### 4. Interface Segregation Principle (ISP)
- Interfaces específicas por tipo de recurso
- Clientes solo dependen de métodos que necesitan

### 5. Dependency Inversion Principle (DIP)
- `ResourceProvisioningService` depende de abstracciones, no de implementaciones concretas
- Usa `CloudResourceFactory` abstracta, no factories específicas

## Requerimientos Funcionales Cumplidos

### RF1: Aprovisionamiento de Familias de Recursos ✅
- El endpoint `/provision_resource_family` permite aprovisionar VM + Red + Disco en una sola solicitud

### RF2: Endpoint REST Unificado ✅
- Un solo endpoint maneja todos los proveedores
- Parámetros específicos por proveedor aceptados en formato JSON

### RF3: Consistencia de Proveedor ✅
- Una VM de AWS solo se asocia con Red y Disco de AWS
- Garantizado por el uso de la misma factory concreta

### RF4: Respuesta Detallada ✅
- Incluye IDs generados, detalles de recursos y estado de aprovisionamiento
- Información completa de cada recurso creado

### RF5: Extensibilidad ✅
- `AbstractFactoryRegistry.register_factory()` permite agregar nuevos proveedores
- No requiere modificar el controlador central

## Requerimientos No Funcionales Cumplidos

### RNF1: Consistencia ✅
- Aprovisionamiento atómico: si falla un recurso, no se crean los demás
- Orden secuencial: Red → Almacenamiento → VM

## Casos de Uso

### Ejemplo AWS
```json
{
  "provider": "aws",
  "vm_params": {
    "instance_type": "t2.micro",
    "region": "us-east-1", 
    "ami": "ami-123456"
  },
  "network_params": {
    "vpcId": "vpc-abc123",
    "subnet": "subnet-def456", 
    "securityGroup": "sg-ghi789"
  },
  "storage_params": {
    "volumeType": "gp2",
    "sizeGB": 20,
    "encrypted": true
  }
}
```

### Respuesta Exitosa
```json
{
  "success": true,
  "provider": "AWS",
  "resources": [
    {
      "resource_id": "aws-net-123",
      "resource_type": "network",
      "status": "disponible",
      "details": {...}
    },
    {
      "resource_id": "aws-vol-456", 
      "resource_type": "storage",
      "status": "disponible",
      "details": {...}
    },
    {
      "resource_id": "aws-vm-789",
      "resource_type": "vm", 
      "status": "aprovisionada",
      "details": {...}
    }
  ]
}
```

## Extensión Futura

Para agregar un nuevo proveedor (ej: Oracle Cloud):

1. **Crear recursos en `resources.py`**:
   ```python
   class OracleNetwork(NetworkResource): ...
   class OracleStorage(StorageResource): ...
   class OracleVM(VMResource): ...
   ```

2. **Crear factory en `abstract_factory.py`**:
   ```python
   class OracleResourceFactory(CloudResourceFactory): ...
   ```

3. **Registrar el proveedor**:
   ```python
   AbstractFactoryRegistry.register_factory("oracle", OracleResourceFactory)
   ```

## Ventajas del Abstract Factory

1. **Consistencia**: Garantiza que los recursos pertenezcan al mismo proveedor
2. **Extensibilidad**: Fácil agregar nuevos proveedores con familias completas
3. **Mantenibilidad**: Código organizado por familias de productos
4. **Reutilización**: Interfaces comunes para diferentes proveedores
5. **Testabilidad**: Cada componente se puede probar independientemente

## Comparación con Factory Method

| Aspecto | Factory Method | Abstract Factory |
|---------|----------------|------------------|
| Productos | Individuales (VM) | Familias (VM+Red+Disco) |
| Consistencia | No garantizada | Garantizada |
| Complejidad | Menor | Mayor |
| Flexibilidad | Limitada | Alta |
| Casos de Uso | Recursos simples | Recursos relacionados |

Esta implementación demuestra cómo el patrón Abstract Factory proporciona una solución robusta para gestionar familias de recursos relacionados de manera consistente y extensible.