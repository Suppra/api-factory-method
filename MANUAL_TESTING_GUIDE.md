# Guía de Pruebas Manuales - API Multi-Cloud Completa

## Instrucciones Previas

1. **Instalar dependencias:**
   ```bash
   py -m pip install fastapi uvicorn httpx pydantic
   ```

2. **Ejecutar el servidor:**
   ```bash
   py -m uvicorn api:app --reload
   ```

3. **Acceder a la documentación interactiva:**
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

## Resumen de Patrones y Endpoints

La API implementa **3 patrones creacionales** con diferentes niveles de abstracción:

1. **Factory Method** → `/provision_vm` (Individual)
2. **Abstract Factory** → `/provision_resource_family` (Familias)
3. **Builder + Director** → `/build_vm` (Construcción guiada)

## Endpoint 1: Aprovisionamiento Individual (Factory Method)

### URL: `POST /provision_vm`

#### Ejemplo AWS:
```json
{
  "provider": "aws",
  "params": {
    "instance_type": "t2.micro",
    "region": "us-east-1",
    "vpc": "vpc-123",
    "ami": "ami-456"
  }
}
```

#### Ejemplo Azure:
```json
{
  "provider": "azure", 
  "params": {
    "size": "Standard_B1s",
    "resource_group": "rg-test",
    "image": "ubuntu-20.04",
    "vnet": "vnet-test"
  }
}
```

## Endpoint 2: Aprovisionamiento de Familias (Abstract Factory)

### URL: `POST /provision_resource_family`

#### Ejemplo Completo AWS:
```json
{
  "provider": "aws",
  "vm_params": {
    "instance_type": "t2.micro",
    "region": "us-east-1",
    "ami": "ami-12345"
  },
  "network_params": {
    "vpcId": "vpc-123",
    "subnet": "subnet-456", 
    "securityGroup": "sg-789"
  },
  "storage_params": {
    "volumeType": "gp2",
    "sizeGB": 20,
    "encrypted": true
  }
}
```

#### Ejemplo Completo Azure:
```json
{
  "provider": "azure",
  "vm_params": {
    "size": "Standard_B1s",
    "resource_group": "rg-production",
    "image": "ubuntu-20.04"
  },
  "network_params": {
    "virtualNetwork": "vnet-production",
    "subnetName": "subnet-web",
    "networkSecurityGroup": "nsg-web"
  },
  "storage_params": {
    "diskSku": "Premium_LRS",
    "sizeGB": 100,
    "managedDisk": true
  }
}
```

#### Ejemplo Completo Google Cloud:
```json
{
  "provider": "gcp",
  "vm_params": {
    "machine_type": "n1-standard-2",
    "zone": "us-central1-b",
    "project": "my-project-123"
  },
  "network_params": {
    "networkName": "default",
    "subnetworkName": "default-subnet",
    "firewallTag": "allow-http-https"
  },
  "storage_params": {
    "diskType": "pd-ssd",
    "sizeGB": 50,
    "autoDelete": false
  }
}
```

#### Ejemplo Completo On-Premise:
```json
{
  "provider": "onpremise",
  "vm_params": {
    "cpu": 8,
    "ram": 16,
    "hypervisor": "vmware"
  },
  "network_params": {
    "physicalInterface": "eth0",
    "vlanId": 200,
    "firewallPolicy": "allow-web"
  },
  "storage_params": {
    "storagePool": "pool-nvme",
    "sizeGB": 500,
    "raidLevel": "raid5"
  }
}
```

## Endpoint 3: Proveedores Soportados

### URL: `GET /supported_providers`

No requiere parámetros. Devuelve la lista de proveedores disponibles.

## Respuestas Esperadas

### Respuesta Exitosa (Individual):
```json
{
  "success": true,
  "vm_id": "aws-vm-123",
  "error": null
}
```

### Respuesta Exitosa (Familia):
```json
{
  "success": true,
  "provider": "AWS",
  "resources": [
    {
      "resource_id": "aws-network-n123",
      "resource_type": "network",
      "status": "provisioned",
      "details": {
        "vpcId": "vpc-123",
        "subnet": "subnet-456",
        "securityGroup": "sg-789"
      }
    },
    {
      "resource_id": "aws-storage-s456",
      "resource_type": "storage", 
      "status": "provisioned",
      "details": {
        "volumeType": "gp2",
        "sizeGB": 20,
        "encrypted": true
      }
    },
    {
      "resource_id": "aws-vm-vm789",
      "resource_type": "vm",
      "status": "provisioned",
      "details": {
        "instance_type": "t2.micro",
        "region": "us-east-1",
        "ami": "ami-12345",
        "network_id": "aws-network-n123",
        "storage_id": "aws-storage-s456"
      }
    }
  ],
  "error": null
}
```

### Respuesta de Error:
```json
{
  "success": false,
  "vm_id": null,
  "error": "Falta parámetro AWS: ami"
}
```

## Casos de Prueba Sugeridos

### ✅ Casos Exitosos:
1. Aprovisionar VM individual en cada proveedor
2. Aprovisionar familia completa en cada proveedor
3. Verificar consistencia de IDs en familias de recursos

### ❌ Casos de Error:
1. Proveedor no soportado: `"provider": "oracle"`
2. Parámetros faltantes para VM individual
3. Parámetros faltantes para network, storage o vm en familias
4. Parámetros inválidos (valores vacíos, tipos incorrectos)

## Validación de Consistencia

Verifica que en las respuestas de familias:
- Todos los `resource_id` contengan el prefijo del proveedor
- Se creen exactamente 3 recursos (network, storage, vm)
- La VM referencie los IDs de network y storage creados
- El `provider` en la respuesta coincida con el solicitado

## Endpoint 3: Construcción Guiada (Builder + Director)

### URL: `POST /build_vm`

El patrón Builder + Director simplifica la construcción de VMs definiendo tipos estándar con configuraciones automáticas por proveedor.

#### Ejemplo AWS Memory Optimized:
```json
{
  "vm_type": "memory_optimized",
  "provider": "aws",
  "region": "us-east-1"
}
```

#### Ejemplo Azure Compute Optimized con personalización:
```json
{
  "vm_type": "compute_optimized",
  "provider": "azure", 
  "region": "eastus",
  "custom_vm_config": {
    "key_pair_name": "production-key",
    "disk_optimization": true
  },
  "custom_storage_config": {
    "size_gb": 200,
    "iops": 5000
  }
}
```

#### Ejemplo GCP Standard:
```json
{
  "vm_type": "standard",
  "provider": "gcp",
  "region": "us-central1"
}
```

### Tipos de VM Disponibles:
- **standard**: Propósito general, configuración balanceada
- **memory_optimized**: Optimizada para memoria, ideal para bases de datos
- **compute_optimized**: Optimizada para CPU, ideal para procesamiento

## Endpoint 4: Configuraciones Disponibles

### URL: `GET /vm_configurations/{provider}`

Obtiene todas las configuraciones disponibles para un proveedor específico.

#### Ejemplo:
```
GET /vm_configurations/aws
```

## Endpoint 5: Validación de Configuración

### URL: `POST /validate_vm_config`

Valida una configuración antes de crear la VM, incluyendo estimación de costos.

#### Ejemplo:
```json
POST /validate_vm_config?provider=aws&vm_type=memory_optimized&region=us-east-1&flavor=large
```

## Comandos cURL Completos

```bash
# 1. VM Individual (Factory Method)
curl -X POST "http://127.0.0.1:8000/provision_vm" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "aws",
    "params": {"instance_type": "t2.micro", "region": "us-east-1", "vpc": "vpc-123", "ami": "ami-123"}
  }'

# 2. Familia de Recursos (Abstract Factory)
curl -X POST "http://127.0.0.1:8000/provision_resource_family" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "azure",
    "vm_params": {"size": "Standard_B1s", "resource_group": "rg-1", "image": "ubuntu"},
    "network_params": {"virtualNetwork": "vnet-1", "subnetName": "subnet-1", "networkSecurityGroup": "nsg-1"},
    "storage_params": {"diskSku": "Standard_LRS", "sizeGB": 50, "managedDisk": true}
  }'

# 3. Construcción Guiada (Builder + Director)
curl -X POST "http://127.0.0.1:8000/build_vm" \
  -H "Content-Type: application/json" \
  -d '{
    "vm_type": "memory_optimized",
    "provider": "gcp",
    "region": "us-central1",
    "custom_storage_config": {"size_gb": 100}
  }'

# 4. Configuraciones de Proveedor
curl -X GET "http://127.0.0.1:8000/vm_configurations/onpremise"

# 5. Validar Configuración
curl -X POST "http://127.0.0.1:8000/validate_vm_config?provider=aws&vm_type=compute_optimized&region=us-east-1"

# 6. Proveedores Soportados
curl -X GET "http://127.0.0.1:8000/supported_providers"
```

## Comparación de Patrones

| Patrón | Endpoint | Nivel de Control | Complejidad | Uso Recomendado |
|--------|----------|------------------|-------------|------------------|
| **Factory Method** | `/provision_vm` | Total | Alto | Configuraciones específicas y detalladas |
| **Abstract Factory** | `/provision_resource_family` | Medio | Medio | Familias consistentes de recursos |
| **Builder + Director** | `/build_vm` | Automático + Personalizable | Bajo | Tipos estándar con personalización opcional |

### Cuándo usar cada patrón:
- **Factory Method**: Cuando necesitas control total sobre cada parámetro
- **Abstract Factory**: Cuando necesitas garantizar consistencia entre recursos relacionados  
- **Builder + Director**: Cuando quieres configuraciones automáticas con posibilidad de personalización