# Guía de Pruebas Manuales - API Multi-Cloud

## Instrucciones Previas

1. **Instalar dependencias:**
   ```bash
   py -m pip install fastapi uvicorn httpx
   ```

2. **Ejecutar el servidor:**
   ```bash
   py -m uvicorn api:app --reload
   ```

3. **Acceder a la documentación interactiva:**
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

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

## Comandos cURL Alternativos

Si prefieres usar línea de comandos:

```bash
# Familia AWS
curl -X POST "http://127.0.0.1:8000/provision_resource_family" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "aws",
    "vm_params": {"instance_type": "t2.micro", "region": "us-east-1", "ami": "ami-123"},
    "network_params": {"vpcId": "vpc-123", "subnet": "subnet-456", "securityGroup": "sg-789"},
    "storage_params": {"volumeType": "gp2", "sizeGB": 20, "encrypted": true}
  }'

# VM Individual Azure  
curl -X POST "http://127.0.0.1:8000/provision_vm" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "azure",
    "params": {"size": "Standard_B1s", "resource_group": "rg-1", "image": "ubuntu", "vnet": "vnet-1"}
  }'

# Proveedores soportados
curl -X GET "http://127.0.0.1:8000/supported_providers"
```