"""
Tests para el patrón Abstract Factory - Familias de Recursos
Valida el aprovisionamiento consistente de VM + Red + Disco por proveedor
"""

import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

# ============= TESTS PARA FAMILIAS DE RECURSOS (ABSTRACT FACTORY) =============

def test_provision_aws_family_success():
    """Test aprovisionamiento exitoso de familia AWS completa"""
    response = client.post("/provision_resource_family", json={
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
            "encrypted": True
        }
    })
    
    data = response.json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["provider"] == "AWS"
    assert len(data["resources"]) == 3
    
    # Verificar que se crearon los 3 tipos de recursos
    resource_types = [r["resource_type"] for r in data["resources"]]
    assert "network" in resource_types
    assert "storage" in resource_types
    assert "vm" in resource_types

def test_provision_azure_family_success():
    """Test aprovisionamiento exitoso de familia Azure completa"""
    response = client.post("/provision_resource_family", json={
        "provider": "azure",
        "vm_params": {
            "size": "Standard_B1s",
            "resource_group": "rg-test",
            "image": "ubuntu-20.04"
        },
        "network_params": {
            "virtualNetwork": "vnet-test",
            "subnetName": "subnet-test",
            "networkSecurityGroup": "nsg-test"
        },
        "storage_params": {
            "diskSku": "Standard_LRS",
            "sizeGB": 30,
            "managedDisk": True
        }
    })
    
    data = response.json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["provider"] == "Azure"
    assert len(data["resources"]) == 3

def test_provision_gcp_family_success():
    """Test aprovisionamiento exitoso de familia GCP completa"""
    response = client.post("/provision_resource_family", json={
        "provider": "gcp",
        "vm_params": {
            "machine_type": "n1-standard-1",
            "zone": "us-central1-a",
            "project": "my-project-123"
        },
        "network_params": {
            "networkName": "default",
            "subnetworkName": "default-subnet",
            "firewallTag": "allow-http"
        },
        "storage_params": {
            "diskType": "pd-standard",
            "sizeGB": 50,
            "autoDelete": True
        }
    })
    
    data = response.json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["provider"] == "Google Cloud"
    assert len(data["resources"]) == 3

def test_provision_onpremise_family_success():
    """Test aprovisionamiento exitoso de familia OnPremise completa"""
    response = client.post("/provision_resource_family", json={
        "provider": "onpremise",
        "vm_params": {
            "cpu": 4,
            "ram": 8,
            "hypervisor": "vmware"
        },
        "network_params": {
            "physicalInterface": "eth0",
            "vlanId": 100,
            "firewallPolicy": "allow-all"
        },
        "storage_params": {
            "storagePool": "pool-ssd",
            "sizeGB": 100,
            "raidLevel": "raid1"
        }
    })
    
    data = response.json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["provider"] == "On-Premise"
    assert len(data["resources"]) == 3

def test_provision_family_missing_network_params():
    """Test error cuando faltan parámetros de red"""
    response = client.post("/provision_resource_family", json={
        "provider": "aws",
        "vm_params": {
            "instance_type": "t2.micro",
            "region": "us-east-1",
            "ami": "ami-12345"
        },
        "network_params": {
            "vpcId": "vpc-123"
            # Faltan subnet y securityGroup
        },
        "storage_params": {
            "volumeType": "gp2",
            "sizeGB": 20,
            "encrypted": True
        }
    })
    
    data = response.json()
    assert data["success"] is False
    assert "Falta parámetro de red AWS" in data["error"]

def test_provision_family_missing_storage_params():
    """Test error cuando faltan parámetros de almacenamiento"""
    response = client.post("/provision_resource_family", json={
        "provider": "azure",
        "vm_params": {
            "size": "Standard_B1s",
            "resource_group": "rg-test",
            "image": "ubuntu-20.04"
        },
        "network_params": {
            "virtualNetwork": "vnet-test",
            "subnetName": "subnet-test",
            "networkSecurityGroup": "nsg-test"
        },
        "storage_params": {
            "diskSku": "Standard_LRS"
            # Faltan sizeGB y managedDisk
        }
    })
    
    data = response.json()
    assert data["success"] is False
    assert "Falta parámetro de almacenamiento Azure" in data["error"]

def test_provision_family_unsupported_provider():
    """Test error con proveedor no soportado"""
    response = client.post("/provision_resource_family", json={
        "provider": "oracle",
        "vm_params": {"instance_type": "test"},
        "network_params": {"network": "test"},
        "storage_params": {"storage": "test"}
    })
    
    data = response.json()
    assert data["success"] is False
    assert "no soportado" in data["error"]

def test_get_supported_providers():
    """Test endpoint de proveedores soportados"""
    response = client.get("/supported_providers")
    data = response.json()
    
    assert response.status_code == 200
    assert "providers" in data
    assert "aws" in data["providers"]
    assert "azure" in data["providers"]
    assert "gcp" in data["providers"]
    assert "onpremise" in data["providers"]

# ============= TESTS DE CONSISTENCIA =============

def test_resource_family_consistency():
    """Test que verifica que todos los recursos pertenecen al mismo proveedor"""
    response = client.post("/provision_resource_family", json={
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
            "encrypted": True
        }
    })
    
    data = response.json()
    assert data["success"] is True
    
    # Verificar que todos los resource_ids contienen el prefijo del proveedor
    for resource in data["resources"]:
        assert "aws" in resource["resource_id"].lower()