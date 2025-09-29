import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

# Casos de prueba para cada proveedor

def test_provision_aws_exito():
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
    assert data["success"] is True
    assert data["vm_id"] == "aws-vm-123"
    assert data["error"] is None

def test_provision_aws_error():
    response = client.post("/provision_vm", json={
        "provider": "aws",
        "params": {
            "instance_type": "t2.micro",
            "region": "us-east-1",
            "vpc": "vpc-123"
            # Falta 'ami'
        }
    })
    data = response.json()
    assert data["success"] is False
    assert data["vm_id"] is None
    assert "Falta parámetro AWS" in data["error"]

def test_provision_azure_exito():
    response = client.post("/provision_vm", json={
        "provider": "azure",
        "params": {
            "size": "Standard_B1s",
            "resource_group": "rg-1",
            "image": "img-2",
            "vnet": "vnet-3"
        }
    })
    data = response.json()
    assert data["success"] is True
    assert data["vm_id"] == "azure-vm-456"
    assert data["error"] is None

def test_provision_gcp_exito():
    response = client.post("/provision_vm", json={
        "provider": "gcp",
        "params": {
            "machine_type": "n1-standard-1",
            "zone": "us-central1-a",
            "disk": "disk-1",
            "project": "proj-2"
        }
    })
    data = response.json()
    assert data["success"] is True
    assert data["vm_id"] == "gcp-vm-789"
    assert data["error"] is None

def test_provision_onpremise_exito():
    response = client.post("/provision_vm", json={
        "provider": "onpremise",
        "params": {
            "cpu": 4,
            "ram": 16,
            "disk": 100,
            "network": "eth0"
        }
    })
    data = response.json()
    assert data["success"] is True
    assert data["vm_id"] == "onprem-vm-001"
    assert data["error"] is None

def test_provision_proveedor_no_soportado():
    response = client.post("/provision_vm", json={
        "provider": "oracle",
        "params": {}
    })
    data = response.json()
    assert data["success"] is False
    assert data["vm_id"] is None
    assert "Proveedor" in data["error"]
