# Guía de Pruebas Manuales - Patrón Prototype

## Resumen de la Implementación

Hemos implementado exitosamente el **patrón Prototype** integrado con los patrones existentes (Factory Method, Abstract Factory, Builder+Director) en el sistema multi-cloud de aprovisionamiento de VMs.

### Resultados de Testing

✅ **Tests Unitarios**: 56/56 tests pasando
- 6 tests Factory Method
- 9 tests Abstract Factory  
- 16 tests Builder Pattern
- **15 tests Prototype Pattern (NUEVO)**
- 10 tests adicionales de integración

### Nuevos Endpoints Implementados

#### 1. Listar Templates Disponibles
```http
GET /vm_templates
```
Respuesta esperada:
```json
{
  "success": true,
  "templates": [
    {
      "template_name": "web-server-standard",
      "category": "web-services",
      "provider": "aws",
      "vm_type": "standard"
    },
    {
      "template_name": "database-optimized", 
      "category": "databases",
      "provider": "aws",
      "vm_type": "memory_optimized"
    }
  ],
  "total": 3,
  "categories": ["web-services", "databases", "analytics"]
}
```

#### 2. Crear VM desde Template
```http
POST /create_from_template
Content-Type: application/json

{
  "template_name": "web-server-standard",
  "provider": "azure",
  "region": "eastus",
  "vm_customizations": {
    "vcpus": 4,
    "memory_gb": 8
  },
  "network_customizations": {
    "firewall_rules": ["HTTP", "HTTPS", "SSH"]
  }
}
```

#### 3. Obtener Detalles de Template
```http
GET /vm_templates/{template_name}
```
Ejemplo: `GET /vm_templates/web-server-standard`

#### 4. Registrar Nuevo Template
```http
POST /register_template
Content-Type: application/json

{
  "template_name": "custom-web-template",
  "description": "Template personalizado para aplicaciones web",
  "category": "custom",
  "vm_specification": {
    "vm_type": "standard",
    "provider": "aws",
    "region": "us-east-1",
    "vm_config": {
      "provider": "aws",
      "vcpus": 2,
      "memory_gb": 4,
      "instance_type": "t3.medium"
    },
    "network_config": {
      "provider": "aws", 
      "region": "us-east-1",
      "firewall_rules": ["SSH", "HTTP"]
    },
    "storage_config": {
      "provider": "aws",
      "region": "us-east-1", 
      "size_gb": 20
    }
  }
}
```

#### 5. Validar Template
```http
POST /validate_template
Content-Type: application/json

{
  "template_name": "web-server-standard",
  "target_provider": "azure",
  "target_region": "eastus"
}
```

#### 6. Eliminar Template
```http
DELETE /vm_templates/{template_name}
```

### Casos de Uso Implementados

#### Caso 1: Clonar Configuración entre Ambientes
```bash
# 1. Usar template base para desarrollo
POST /create_from_template
{
  "template_name": "web-server-standard",
  "vm_customizations": {"vcpus": 1, "memory_gb": 2}
}

# 2. Escalar para producción  
POST /create_from_template
{
  "template_name": "web-server-standard",
  "vm_customizations": {"vcpus": 8, "memory_gb": 32}
}
```

#### Caso 2: Migración entre Proveedores
```bash
# Clonar template de AWS a Azure
POST /create_from_template  
{
  "template_name": "database-optimized",
  "provider": "azure",
  "region": "westus2"
}
```

#### Caso 3: Templates Especializados por Industria
Los templates predeterminados incluyen:
- **web-server-standard**: Para servidores web con balanceador
- **database-optimized**: Para bases de datos con alta IOPS
- **analytics-compute**: Para procesamiento intensivo

### Comandos de Prueba

#### Iniciar el Servidor
```powershell
cd "C:\Users\Crist\ApiPatrones\api-factory-method"
& "C:/Users/Crist/AppData/Local/Programs/Python/Python313/python.exe" -m uvicorn api:app --host 0.0.0.0 --port 8000
```

#### Ejecutar Tests
```powershell  
# Tests específicos del Prototype
& "C:/Users/Crist/AppData/Local/Programs/Python/Python313/python.exe" -m pytest test_prototype_pattern.py -v

# Todos los tests
& "C:/Users/Crist/AppData/Local/Programs/Python/Python313/python.exe" -m pytest -v
```

#### Probar Endpoints con PowerShell
```powershell
# Listar templates
$response = Invoke-WebRequest -Uri "http://localhost:8000/vm_templates" -Method GET
$response.Content | ConvertFrom-Json

# Crear VM desde template
$body = @{
  template_name = "web-server-standard"
  provider = "azure"  
  region = "eastus"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/create_from_template" -Method POST -Body $body -ContentType "application/json"
```

### Documentación Swagger

Una vez iniciado el servidor, la documentación interactiva está disponible en:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Archivos Nuevos Creados

1. **`vm_prototype.py`**: Implementación del patrón Prototype
   - `VMPrototype` (interfaz abstracta)
   - `ConcreteVMPrototype` (implementación concreta)  
   - `PrototypeRegistry` (gestión de templates)

2. **`vm_prototype_service.py`**: Servicio de orquestación
   - Integración con patrones existentes
   - Gestión de templates avanzada
   - Adaptación entre proveedores

3. **`prototype_models.py`**: Modelos Pydantic
   - Requests y responses específicos
   - Validación de datos

4. **`test_prototype_pattern.py`**: Suite completa de tests
   - 15 tests específicos del patrón
   - Cobertura completa de funcionalidad

5. **`PROTOTYPE_PATTERN_DOCS.md`**: Documentación académica completa
   - Análisis teórico del patrón
   - Casos de uso en contexto multi-cloud
   - Diagramas UML

### Estado Final

- ✅ **4 Patrones Implementados**: Factory Method, Abstract Factory, Builder+Director, Prototype
- ✅ **56 Tests Pasando**: Cobertura completa de funcionalidad
- ✅ **12 Endpoints API**: Funcionalidad completa multi-cloud
- ✅ **Documentación Académica**: Análisis teórico y práctico
- ✅ **Integración Completa**: Todos los patrones trabajan cohesivamente

El proyecto está **COMPLETAMENTE FUNCIONAL** y listo para presentación académica en el curso de Patrones de Diseño de Software de la Universidad Popular del César.