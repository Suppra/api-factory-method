import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

# ============= CASOS DE PRUEBA PARA FAMILIAS DE RECURSOS =============

def test_provision_aws_resource_family_success():
    """Prueba exitosa de aprovisionamiento de familia de recursos AWS"""
    response = client.post("/provision_resource_family", json={
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
            "encrypted": True
        }
    })
    
    data = response.json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["provider"] == "AWS"
    assert len(data["resources"]) == 3
    
    # Verificar que se crearon los tres tipos de recursos
    resource_types = [r["resource_type"] for r in data["resources"]]
    assert "network" in resource_types
    assert "storage" in resource_types
    assert "vm" in resource_types

def test_provision_azure_resource_family_success():
    """Prueba exitosa de aprovisionamiento de familia de recursos Azure"""
    response = client.post("/provision_resource_family", json={
        "provider": "azure",
        "vm_params": {
            "size": "Standard_B1s",
            "resource_group": "rg-test",
            "image": "Ubuntu20.04"
        },
        "network_params": {
            "virtualNetwork": "vnet-test",
            "subnetName": "subnet-test",
            "networkSecurityGroup": "nsg-test"
        },
        "storage_params": {
            "diskSku": "Premium_LRS",
            "sizeGB": 50,
            "managedDisk": True
        }
    })
    
    data = response.json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["provider"] == "Azure"
    assert len(data["resources"]) == 3

def test_provision_gcp_resource_family_success():
    """Prueba exitosa de aprovisionamiento de familia de recursos GCP"""
    response = client.post("/provision_resource_family", json={
        "provider": "gcp",
        "vm_params": {
            "machine_type": "n1-standard-1",
            "zone": "us-central1-a",
            "project": "my-project"
        },
        "network_params": {
            "networkName": "default",
            "subnetworkName": "default",
            "firewallTag": "web-server"
        },
        "storage_params": {
            "diskType": "pd-ssd",
            "sizeGB": 30,
            "autoDelete": True
        }
    })
    
    data = response.json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["provider"] == "Google Cloud"
    assert len(data["resources"]) == 3

def test_provision_onpremise_resource_family_success():
    """Prueba exitosa de aprovisionamiento de familia de recursos On-Premise"""
    response = client.post("/provision_resource_family", json={
        "provider": "onpremise",
        "vm_params": {
            "cpu": 4,
            "ram": 16
        },
        "network_params": {
            "physicalInterface": "eth0",
            "vlanId": 100,
            "firewallPolicy": "default"
        },
        "storage_params": {
            "storagePool": "pool1",
            "sizeGB": 100,
            "raidLevel": "RAID5"
        }
    })
    
    data = response.json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["provider"] == "On-Premise"
    assert len(data["resources"]) == 3

def test_provision_unsupported_provider():
    """Prueba de error con proveedor no soportado"""
    response = client.post("/provision_resource_family", json={
        "provider": "oracle",
        "vm_params": {},
        "network_params": {},
        "storage_params": {}
    })
    
    data = response.json()
    assert response.status_code == 200
    assert data["success"] is False
    assert "oracle" in data["error"].lower()

def test_provision_missing_network_params():
    """Prueba de error por parámetros faltantes en red"""
    response = client.post("/provision_resource_family", json={
        "provider": "aws",
        "vm_params": {
            "instance_type": "t2.micro",
            "region": "us-east-1",
            "ami": "ami-123456"
        },
        "network_params": {
            "vpcId": "vpc-abc123"
            # Faltan subnet y securityGroup
        },
        "storage_params": {
            "volumeType": "gp2",
            "sizeGB": 20,
            "encrypted": True
        }
    })
    
    data = response.json()
    assert response.status_code == 200
    assert data["success"] is False
    assert "red" in data["error"].lower()

def test_provision_missing_storage_params():
    """Prueba de error por parámetros faltantes en almacenamiento"""
    response = client.post("/provision_resource_family", json={
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
            "volumeType": "gp2"
            # Faltan sizeGB y encrypted
        }
    })
    
    data = response.json()
    assert response.status_code == 200
    assert data["success"] is False
    assert "almacenamiento" in data["error"].lower()

def test_provision_missing_vm_params():
    """Prueba de error por parámetros faltantes en VM"""
    response = client.post("/provision_resource_family", json={
        "provider": "aws",
        "vm_params": {
            "instance_type": "t2.micro"
            # Faltan region y ami
        },
        "network_params": {
            "vpcId": "vpc-abc123",
            "subnet": "subnet-def456",
            "securityGroup": "sg-ghi789"
        },
        "storage_params": {
            "volumeType": "gp2",
            "sizeGB": 20,
            "encrypted": True
        }
    })
    
    data = response.json()
    assert response.status_code == 200
    assert data["success"] is False
    assert "vm" in data["error"].lower()

def test_get_supported_providers():
    """Prueba del endpoint de proveedores soportados"""
    response = client.get("/supported_providers")
    
    data = response.json()
    assert response.status_code == 200
    assert "providers" in data
    assert "aws" in data["providers"]
    assert "azure" in data["providers"]
    assert "gcp" in data["providers"]
    assert "onpremise" in data["providers"]

# ============= CASOS DE PRUEBA PARA ENDPOINT ORIGINAL (COMPATIBILIDAD) =============

def test_original_provision_vm_aws_success():
    """Prueba del endpoint original para VM individual"""
    response = client.post("/provision_vm", json={
        "provider": "aws",
        "params": {
            "instance_type": "t2.micro",
            "region": "us-east-1",
            "vpc": "vpc-123",
            "ami": "ami-456"
        }
    })
    data = response.json()
    assert response.status_code == 200
    assert data["success"] is True
    assert data["vm_id"] == "aws-vm-123"