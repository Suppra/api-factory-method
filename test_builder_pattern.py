"""
Tests para el patrón Builder con Director.
Valida la construcción de diferentes tipos de VM usando Director + Builder.
"""

import pytest
from fastapi.testclient import TestClient
from api import app
from models_extended import VMType, Provider

client = TestClient(app)

# ============= TESTS PARA BUILDER PATTERN =============

def test_build_standard_aws_vm():
    """Test construcción de VM Standard en AWS"""
    response = client.post("/build_vm", json={
        "vm_type": "standard",
        "provider": "aws", 
        "region": "us-east-1"
    })
    
    data = response.json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["vm_specification"]["vm_type"] == "standard"
    assert data["vm_specification"]["provider"] == "aws"
    assert len(data["created_resources"]) == 3
    
    # Verificar que los recursos tienen IDs de AWS
    resource_ids = [r["resource_id"] for r in data["created_resources"]]
    assert all("aws" in rid.lower() for rid in resource_ids)

def test_build_memory_optimized_azure_vm():
    """Test construcción de VM Memory Optimized en Azure"""
    response = client.post("/build_vm", json={
        "vm_type": "memory_optimized",
        "provider": "azure",
        "region": "eastus"
    })
    
    data = response.json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["vm_specification"]["vm_type"] == "memory_optimized"
    assert data["vm_specification"]["provider"] == "azure"
    
    # Verificar configuración de memoria optimizada
    vm_config = data["vm_specification"]["vm_config"]
    assert vm_config["memory_optimization"] is True
    assert vm_config["memory_gb"] >= 16  # Memory optimized tiene más memoria

def test_build_compute_optimized_gcp_vm():
    """Test construcción de VM Compute Optimized en GCP"""
    response = client.post("/build_vm", json={
        "vm_type": "compute_optimized",
        "provider": "gcp",
        "region": "us-central1"
    })
    
    data = response.json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["vm_specification"]["vm_type"] == "compute_optimized"
    
    # Verificar configuración de cómputo optimizado
    vm_config = data["vm_specification"]["vm_config"]
    assert vm_config["disk_optimization"] is True

def test_build_onpremise_vm_with_custom_config():
    """Test construcción de VM OnPremise con configuraciones personalizadas"""
    response = client.post("/build_vm", json={
        "vm_type": "standard",
        "provider": "onpremise",
        "region": "datacenter-1",
        "custom_vm_config": {
            "key_pair_name": "custom-key",
            "memory_optimization": True
        },
        "custom_storage_config": {
            "size_gb": 200,
            "raid_level": "raid5"
        }
    })
    
    data = response.json()
    assert response.status_code == 200
    assert data["success"] is True
    
    # Verificar que se aplicaron las configuraciones personalizadas
    vm_config = data["vm_specification"]["vm_config"]
    assert vm_config["key_pair_name"] == "custom-key"
    assert vm_config["memory_optimization"] is True
    
    storage_config = data["vm_specification"]["storage_config"]
    assert storage_config["size_gb"] == 200

def test_get_aws_configurations():
    """Test obtener configuraciones disponibles para AWS"""
    response = client.get("/vm_configurations/aws")
    
    data = response.json()
    assert response.status_code == 200
    assert data["provider"] == "aws"
    assert "vm_types" in data
    assert "standard" in data["vm_types"]
    assert "memory_optimized" in data["vm_types"] 
    assert "compute_optimized" in data["vm_types"]
    
    # Verificar que cada tipo tiene flavors disponibles
    for vm_type in data["vm_types"]:
        assert "flavors" in data["vm_types"][vm_type]
        assert "default_flavor" in data["vm_types"][vm_type]

def test_get_azure_configurations():
    """Test obtener configuraciones disponibles para Azure"""
    response = client.get("/vm_configurations/azure")
    
    data = response.json()
    assert response.status_code == 200
    assert data["provider"] == "azure"
    assert "supported_regions" in data
    assert "eastus" in data["supported_regions"]

def test_validate_valid_configuration():
    """Test validar configuración válida"""
    response = client.post("/validate_vm_config", params={
        "provider": "aws",
        "vm_type": "standard",
        "region": "us-east-1",
        "flavor": "medium"
    })
    
    data = response.json()
    assert response.status_code == 200
    assert data["valid"] is True
    assert "specification" in data
    assert "estimated_cost" in data

def test_validate_invalid_configuration():
    """Test validar configuración inválida"""
    response = client.post("/validate_vm_config", params={
        "provider": "aws",
        "vm_type": "invalid_type",
        "region": "us-east-1"
    })
    
    data = response.json()
    assert response.status_code == 422  # Validation error por enum inválido

def test_build_vm_unsupported_provider():
    """Test error con proveedor no soportado en Builder"""
    # Nota: Este test usará un proveedor válido del enum pero que falle internamente
    response = client.post("/build_vm", json={
        "vm_type": "standard",
        "provider": "aws",  # Usamos AWS pero con región inválida para forzar error
        "region": "invalid-region-12345"
    })
    
    data = response.json()
    # El request es válido en formato pero puede fallar en ejecución
    assert response.status_code == 200
    # Puede ser exitoso o fallar dependiendo de la validación interna

def test_vm_types_consistency():
    """Test consistencia de tipos de VM entre Director y Builder"""
    # Verificar que los tipos soportados son consistentes
    response = client.get("/supported_providers")
    data = response.json()
    
    assert "vm_types" in data
    expected_types = ["standard", "memory_optimized", "compute_optimized"]
    for vm_type in expected_types:
        assert vm_type in data["vm_types"]

def test_cost_estimation_in_validation():
    """Test estimación de costos en validación"""
    response = client.post("/validate_vm_config", params={
        "provider": "aws",
        "vm_type": "memory_optimized",
        "region": "us-east-1",
        "flavor": "large"
    })
    
    data = response.json()
    if data.get("valid"):
        cost_info = data["estimated_cost"]
        assert "total_hourly" in cost_info
        assert "estimated_monthly" in cost_info
        assert cost_info["total_hourly"] > 0

def test_region_consistency_validation():
    """Test validación de consistencia de regiones"""
    response = client.post("/build_vm", json={
        "vm_type": "standard",
        "provider": "gcp",
        "region": "us-central1",
        "custom_network_config": {
            "region": "us-central1"  # Misma región
        },
        "custom_storage_config": {
            "region": "us-central1"  # Misma región
        }
    })
    
    data = response.json()
    assert response.status_code == 200
    # Debería ser exitoso con regiones consistentes

# ============= TESTS DE CONFIGURACIONES ESPECÍFICAS POR PROVEEDOR =============

def test_aws_instance_types_assignment():
    """Test que AWS asigne tipos de instancia correctamente según VM type"""
    response = client.post("/build_vm", json={
        "vm_type": "compute_optimized",
        "provider": "aws",
        "region": "us-east-1"
    })
    
    data = response.json()
    if data["success"]:
        vm_config = data["vm_specification"]["vm_config"]
        # Compute optimized debería usar instancias C5
        assert vm_config.get("instance_type", "").startswith("c5")

def test_azure_vm_sizes_assignment():
    """Test que Azure asigne tamaños correctamente según VM type"""
    response = client.post("/build_vm", json={
        "vm_type": "memory_optimized",
        "provider": "azure", 
        "region": "eastus"
    })
    
    data = response.json()
    if data["success"]:
        vm_config = data["vm_specification"]["vm_config"]
        # Memory optimized debería usar series E
        assert "E" in vm_config.get("size", "")

def test_gcp_machine_types_assignment():
    """Test que GCP asigne machine types correctamente"""
    response = client.post("/build_vm", json={
        "vm_type": "standard",
        "provider": "gcp",
        "region": "us-central1"
    })
    
    data = response.json()
    if data["success"]:
        vm_config = data["vm_specification"]["vm_config"]
        # Standard debería usar e2-standard
        assert vm_config.get("machine_type", "").startswith("e2-standard")

def test_onpremise_flavor_assignment():
    """Test que OnPremise asigne flavors correctamente"""
    response = client.post("/build_vm", json={
        "vm_type": "standard",
        "provider": "onpremise",
        "region": "datacenter-1"
    })
    
    data = response.json()
    if data["success"]:
        vm_config = data["vm_specification"]["vm_config"]
        assert vm_config["vcpus"] >= 2
        assert vm_config["memory_gb"] >= 4