# Documentación Académica - Patrón Builder con Director

## Introducción al Patrón Builder

El patrón Builder permite construir objetos complejos paso a paso. En nuestro caso, construye VMs con diferentes configuraciones según el tipo (Standard, Memory-Optimized, Compute-Optimized) mientras el Director define las políticas de construcción específicas para cada proveedor.

## Problema Resuelto

### Desafío Original
- **Configuraciones Complejas**: Las VMs requieren múltiples parámetros específicos por proveedor
- **Tipos Diferentes**: Standard, Memory-Optimized, Compute-Optimized con especificaciones distintas
- **Consistencia**: Mantener coherencia entre tipos de instancia, CPU, memoria según proveedor
- **Extensibilidad**: Agregar nuevos tipos sin modificar código existente

### Solución con Builder + Director
- **Builder**: Construye VMs paso a paso con validación
- **Director**: Define las especificaciones estándar por tipo y proveedor
- **Flexibilidad**: Permite overrides personalizados manteniendo bases sólidas

## Arquitectura de Patrones Combinados

### Integración de Patrones
```
Director (Políticas) → Builder (Construcción) → Abstract Factory (Recursos) → Factory Method (Objetos)
```

1. **Director**: Define qué configuraciones usar según tipo de VM y proveedor
2. **Builder**: Construye la VM paso a paso aplicando las políticas del Director
3. **Abstract Factory**: Crea familias consistentes de recursos (VM + Red + Disco)
4. **Factory Method**: Crea objetos específicos por proveedor

## Especificaciones por Proveedor y Tipo

### AWS
| Tipo | Flavor | Instance Type | vCPUs | RAM (GB) | Optimización |
|------|--------|---------------|--------|----------|--------------|
| **Standard** | small | t3.medium | 2 | 4 | General |
| | medium | m5.large | 2 | 8 | General |
| | large | m5.xlarge | 4 | 16 | General |
| **Memory Optimized** | small | r5.large | 2 | 16 | Memoria |
| | medium | r5.xlarge | 4 | 32 | Memoria |
| | large | r5.2xlarge | 8 | 64 | Memoria |
| **Compute Optimized** | small | c5.large | 2 | 4 | CPU |
| | medium | c5.xlarge | 4 | 8 | CPU |
| | large | c5.2xlarge | 8 | 16 | CPU |

### Azure
| Tipo | Flavor | VM Size | vCPUs | RAM (GB) | Optimización |
|------|--------|---------|--------|----------|--------------|
| **Standard** | small | D2s_v3 | 2 | 8 | General |
| | medium | D4s_v3 | 4 | 16 | General |
| | large | D8s_v3 | 8 | 32 | General |
| **Memory Optimized** | small | E2s_v3 | 2 | 16 | Memoria |
| | medium | E4s_v3 | 4 | 32 | Memoria |
| | large | E8s_v3 | 8 | 64 | Memoria |
| **Compute Optimized** | small | F2s_v2 | 2 | 4 | CPU |
| | medium | F4s_v2 | 4 | 8 | CPU |
| | large | F8s_v2 | 8 | 16 | CPU |

### Google Cloud Platform
| Tipo | Flavor | Machine Type | vCPUs | RAM (GB) | Optimización |
|------|--------|--------------|--------|----------|--------------|
| **Standard** | small | e2-standard-2 | 2 | 8 | General |
| | medium | e2-standard-4 | 4 | 16 | General |
| | large | e2-standard-8 | 8 | 32 | General |
| **Memory Optimized** | small | n2-highmem-2 | 2 | 16 | Memoria |
| | medium | n2-highmem-4 | 4 | 32 | Memoria |
| | large | n2-highmem-8 | 8 | 64 | Memoria |
| **Compute Optimized** | small | n2-highcpu-2 | 2 | 2 | CPU |
| | medium | n2-highcpu-4 | 4 | 4 | CPU |
| | large | n2-highcpu-8 | 8 | 8 | CPU |

### On-Premise
| Tipo | Flavor | Flavor Name | vCPUs | RAM (GB) | Optimización |
|------|--------|-------------|--------|----------|--------------|
| **Standard** | small | onprem-std1 | 2 | 4 | General |
| | medium | onprem-std2 | 4 | 8 | General |
| | large | onprem-std3 | 8 | 16 | General |
| **Memory Optimized** | small | onprem-mem1 | 2 | 16 | Memoria |
| | medium | onprem-mem2 | 4 | 32 | Memoria |
| | large | onprem-mem3 | 8 | 64 | Memoria |
| **Compute Optimized** | small | onprem-cpu1 | 2 | 2 | CPU |
| | medium | onprem-cpu2 | 4 | 4 | CPU |
| | large | onprem-cpu3 | 8 | 8 | CPU |

## Parámetros de Configuración Extendidos

### VirtualMachine (Obligatorios ✅ / Opcionales ❌)
- **provider**: Proveedor de nube ✅
- **vcpus**: Núcleos virtuales ✅  
- **memory_gb**: Memoria RAM en GB ✅
- **memory_optimization**: Optimización de memoria ❌
- **disk_optimization**: Optimización de disco ❌
- **key_pair_name**: Clave SSH ❌

### Network (Obligatorios ✅ / Opcionales ❌)
- **region**: Región de red ✅
- **firewall_rules**: Reglas de seguridad ❌ (default: ["SSH"])
- **public_ip**: IP pública asignada ❌ (default: true)

### Storage (Obligatorios ✅ / Opcionales ❌)
- **region**: Región del almacenamiento ✅
- **size_gb**: Tamaño en GB ✅
- **iops**: Rendimiento del disco ❌ (default: 3000)

## Flujo de Construcción Builder

### Diagrama de Secuencia
```
Cliente → API → VMConstructionService → VMDirector → ConcreteVMBuilder → AbstractFactory
    │       │            │                   │              │                │
    │ POST  │            │                   │              │                │
    │──────▶│            │                   │              │                │
    │       │ build_vm() │                   │              │                │
    │       │───────────▶│                   │              │                │
    │       │            │ get_specification│              │                │
    │       │            │──────────────────▶│              │                │
    │       │            │   VMSpec         │              │                │
    │       │            │◀──────────────────│              │                │
    │       │            │                   │ set_configs()│                │
    │       │            │                   │─────────────▶│                │
    │       │            │                   │              │ build()        │
    │       │            │                   │              │───────────────▶│
    │       │            │                   │              │  Resources     │
    │       │            │                   │              │◀───────────────│
    │       │            │   BuilderResponse │              │                │
    │       │            │◀──────────────────┴──────────────│                │
    │       │  Response  │                                  │                │
    │       │◀───────────│                                  │                │
    │ JSON  │            │                                  │                │
    │◀──────│            │                                  │                │
```

### Pasos Detallados
1. **Request Processing**: API recibe BuilderRequest con tipo, proveedor, región
2. **Director Specification**: Director genera VMSpecification según políticas
3. **Builder Configuration**: Builder recibe configuraciones del Director
4. **Custom Overrides**: Se aplican personalizaciones del usuario
5. **Resource Creation**: Abstract Factory crea recursos consistentes
6. **Validation**: Se valida coherencia de regiones y configuraciones
7. **Response Generation**: Se retorna resultado con recursos creados

## Principios SOLID en Builder Pattern

### Single Responsibility Principle (SRP)
- **VMDirector**: Solo define políticas de configuración
- **ConcreteVMBuilder**: Solo construye VMs paso a paso
- **VMConstructionService**: Solo orquesta el proceso
- **Cada clase tiene una responsabilidad específica y bien definida**

### Open/Closed Principle (OCP)
- **Extensible**: Nuevos tipos de VM se agregan sin modificar código existente
- **Cerrado**: Las clases base no requieren cambios para nuevas funcionalidades

```python
# Agregar nuevo tipo de VM sin modificar código existente
class AIOptimizedVMType:
    # Nueva implementación sin tocar Director existente
    pass
```

### Liskov Substitution Principle (LSP)
- **Builders intercambiables**: Cualquier implementación de VMBuilder funciona
- **Abstracciones respetadas**: Las implementaciones concretas respetan contratos

### Interface Segregation Principle (ISP)
- **Interfaces específicas**: VMBuilder, NetworkResource, StorageResource separadas
- **Clientes no dependen de métodos que no usan**

### Dependency Inversion Principle (DIP)
- **VMConstructionService depende de abstracciones (VMBuilder, VMDirector)**
- **No depende de implementaciones concretas**

## Ejemplo de Uso Completo

### Solicitud Builder AWS Memory Optimized
```json
POST /build_vm
{
  "vm_type": "memory_optimized",
  "provider": "aws",
  "region": "us-east-1",
  "custom_vm_config": {
    "key_pair_name": "production-key",
    "memory_optimization": true
  },
  "custom_storage_config": {
    "size_gb": 500,
    "iops": 10000
  }
}
```

### Respuesta Exitosa
```json
{
  "success": true,
  "vm_specification": {
    "vm_type": "memory_optimized",
    "provider": "aws",
    "region": "us-east-1",
    "vm_config": {
      "provider": "aws",
      "vcpus": 2,
      "memory_gb": 16,
      "memory_optimization": true,
      "instance_type": "r5.large",
      "ami": "ami-0c02fb55956c7d316",
      "key_pair_name": "production-key"
    },
    "network_config": {
      "region": "us-east-1",
      "firewall_rules": ["SSH", "HTTP", "HTTPS"],
      "public_ip": true,
      "vpc_id": "vpc-useast1",
      "subnet": "subnet-useast1",
      "security_group": "sg-memory_optimized"
    },
    "storage_config": {
      "region": "us-east-1",
      "size_gb": 500,
      "iops": 10000,
      "volume_type": "gp2",
      "encrypted": true
    }
  },
  "created_resources": [
    {
      "resource_id": "aws-network-n456",
      "resource_type": "network",
      "status": "provisioned",
      "details": {...}
    },
    {
      "resource_id": "aws-storage-s789",
      "resource_type": "storage", 
      "status": "provisioned",
      "details": {...}
    },
    {
      "resource_id": "aws-vm-vm123",
      "resource_type": "vm",
      "status": "provisioned",
      "details": {...}
    }
  ]
}
```

## Endpoints del API Builder

### POST /build_vm
Construye una VM usando Director + Builder pattern
- **Input**: BuilderRequest (vm_type, provider, region, configs opcionales)
- **Output**: BuilderResponse con especificación y recursos creados

### GET /vm_configurations/{provider}
Obtiene configuraciones disponibles por proveedor
- **Input**: Provider (aws, azure, gcp, onpremise)
- **Output**: Tipos de VM, flavors, regiones soportadas

### POST /validate_vm_config
Valida configuración antes de construcción
- **Input**: Provider, VM type, región, flavor
- **Output**: Validación, especificación, estimación de costos

## Validaciones Implementadas

### Validación de Coherencia
- **Regiones**: Network y Storage deben estar en la misma región
- **Proveedor**: Todos los recursos del mismo proveedor (garantizado por Abstract Factory)
- **Tipos**: VM types válidos según especificaciones del Director

### Validación de Parámetros
- **Obligatorios**: vcpus > 0, memory_gb > 0, region no vacía
- **Opcionales**: Valores por defecto seguros si no se especifican
- **Tipos de datos**: Validación automática con Pydantic

### Estimación de Costos
- **Cálculo simulado** basado en tipo de VM, recursos y proveedor
- **Advertencias** para configuraciones de alto costo
- **Sugerencias** para optimización

## Beneficios del Patrón Builder + Director

### Para el Usuario
1. **Simplicidad**: Solo especifica tipo, proveedor y región
2. **Flexibilidad**: Puede personalizar cualquier aspecto
3. **Consistencia**: Director garantiza configuraciones válidas
4. **Validación**: Verificación antes de creación de recursos

### Para el Desarrollador
1. **Mantenibilidad**: Lógica de configuración centralizada en Director
2. **Extensibilidad**: Agregar tipos/proveedores sin modificar código
3. **Testabilidad**: Cada componente se puede probar independientemente
4. **Legibilidad**: Código autodocumentado con patrones claros

### Para el Sistema
1. **Escalabilidad**: Construcción eficiente y controlada
2. **Atomicidad**: Falla todo o se crea todo
3. **Trazabilidad**: Logs detallados del proceso de construcción
4. **Performance**: Validaciones tempranas evitan recursos desperdiciados

## Conclusiones

La implementación del patrón Builder con Director proporciona:

- **Control total** sobre la construcción de VMs complejas
- **Flexibilidad** para diferentes tipos y configuraciones
- **Extensibilidad** para nuevos proveedores y tipos de VM
- **Mantenibilidad** con separación clara de responsabilidades
- **Validación robusta** de configuraciones y coherencia

El patrón se integra perfectamente con Factory Method y Abstract Factory, creando una arquitectura sólida, extensible y académicamente rica para el estudio de patrones de diseño combinados.