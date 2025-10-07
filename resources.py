# resources.py - Definición de recursos base y específicos por proveedor

from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional

# ============= CLASES BASE ABSTRACTAS =============

class NetworkResource(ABC):
    """Clase base abstracta para recursos de red"""
    
    @abstractmethod
    def create_network(self, params: dict) -> tuple[bool, Optional[str], Optional[str]]:
        """Crear recurso de red. Retorna (éxito, id_recurso, error)"""
        pass
    
    @abstractmethod
    def get_network_info(self) -> dict:
        """Obtener información del recurso de red creado"""
        pass

class StorageResource(ABC):
    """Clase base abstracta para recursos de almacenamiento"""
    
    @abstractmethod
    def create_storage(self, params: dict) -> tuple[bool, Optional[str], Optional[str]]:
        """Crear recurso de almacenamiento. Retorna (éxito, id_recurso, error)"""
        pass
    
    @abstractmethod
    def get_storage_info(self) -> dict:
        """Obtener información del recurso de almacenamiento creado"""
        pass

class VMResource(ABC):
    """Clase base abstracta para recursos de máquinas virtuales"""
    
    @abstractmethod
    def create_vm(self, params: dict, network_id: str, storage_id: str) -> tuple[bool, Optional[str], Optional[str]]:
        """Crear VM asociada a red y almacenamiento. Retorna (éxito, id_vm, error)"""
        pass
    
    @abstractmethod
    def get_vm_info(self) -> dict:
        """Obtener información de la VM creada"""
        pass

# ============= IMPLEMENTACIONES AWS =============

class AWSNetwork(NetworkResource):
    def __init__(self):
        self.network_id = None
        self.network_info = {}
        
    def create_network(self, params: dict) -> tuple[bool, Optional[str], Optional[str]]:
        required = ["vpcId", "subnet", "securityGroup"]
        for r in required:
            if r not in params:
                return False, None, f"Falta parámetro de red AWS: {r}"
        
        # Simulación de creación
        self.network_id = f"aws-net-{hash(str(params)) % 1000}"
        self.network_info = {
            "vpc_id": params["vpcId"],
            "subnet": params["subnet"],
            "security_group": params["securityGroup"],
            "status": "disponible"
        }
        return True, self.network_id, None
    
    def get_network_info(self) -> dict:
        return self.network_info

class AWSStorage(StorageResource):
    def __init__(self):
        self.storage_id = None
        self.storage_info = {}
        
    def create_storage(self, params: dict) -> tuple[bool, Optional[str], Optional[str]]:
        required = ["volumeType", "sizeGB", "encrypted"]
        for r in required:
            if r not in params:
                return False, None, f"Falta parámetro de almacenamiento AWS: {r}"
        
        # Simulación de creación
        self.storage_id = f"aws-vol-{hash(str(params)) % 1000}"
        self.storage_info = {
            "volume_type": params["volumeType"],
            "size_gb": params["sizeGB"],
            "encrypted": params["encrypted"],
            "status": "disponible"
        }
        return True, self.storage_id, None
    
    def get_storage_info(self) -> dict:
        return self.storage_info

class AWSVM(VMResource):
    def __init__(self):
        self.vm_id = None
        self.vm_info = {}
        
    def create_vm(self, params: dict, network_id: str, storage_id: str) -> tuple[bool, Optional[str], Optional[str]]:
        required = ["instance_type", "region", "ami"]
        for r in required:
            if r not in params:
                return False, None, f"Falta parámetro de VM AWS: {r}"
        
        # Simulación de creación
        self.vm_id = f"aws-vm-{hash(str(params) + network_id + storage_id) % 1000}"
        self.vm_info = {
            "instance_type": params["instance_type"],
            "region": params["region"],
            "ami": params["ami"],
            "network_id": network_id,
            "storage_id": storage_id,
            "status": "aprovisionada"
        }
        return True, self.vm_id, None
    
    def get_vm_info(self) -> dict:
        return self.vm_info

# ============= IMPLEMENTACIONES AZURE =============

class AzureNetwork(NetworkResource):
    def __init__(self):
        self.network_id = None
        self.network_info = {}
        
    def create_network(self, params: dict) -> tuple[bool, Optional[str], Optional[str]]:
        required = ["virtualNetwork", "subnetName", "networkSecurityGroup"]
        for r in required:
            if r not in params:
                return False, None, f"Falta parámetro de red Azure: {r}"
        
        self.network_id = f"azure-net-{hash(str(params)) % 1000}"
        self.network_info = {
            "virtual_network": params["virtualNetwork"],
            "subnet_name": params["subnetName"],
            "network_security_group": params["networkSecurityGroup"],
            "status": "disponible"
        }
        return True, self.network_id, None
    
    def get_network_info(self) -> dict:
        return self.network_info

class AzureStorage(StorageResource):
    def __init__(self):
        self.storage_id = None
        self.storage_info = {}
        
    def create_storage(self, params: dict) -> tuple[bool, Optional[str], Optional[str]]:
        required = ["diskSku", "sizeGB", "managedDisk"]
        for r in required:
            if r not in params:
                return False, None, f"Falta parámetro de almacenamiento Azure: {r}"
        
        self.storage_id = f"azure-disk-{hash(str(params)) % 1000}"
        self.storage_info = {
            "disk_sku": params["diskSku"],
            "size_gb": params["sizeGB"],
            "managed_disk": params["managedDisk"],
            "status": "disponible"
        }
        return True, self.storage_id, None
    
    def get_storage_info(self) -> dict:
        return self.storage_info

class AzureVM(VMResource):
    def __init__(self):
        self.vm_id = None
        self.vm_info = {}
        
    def create_vm(self, params: dict, network_id: str, storage_id: str) -> tuple[bool, Optional[str], Optional[str]]:
        required = ["size", "resource_group", "image"]
        for r in required:
            if r not in params:
                return False, None, f"Falta parámetro de VM Azure: {r}"
        
        self.vm_id = f"azure-vm-{hash(str(params) + network_id + storage_id) % 1000}"
        self.vm_info = {
            "size": params["size"],
            "resource_group": params["resource_group"],
            "image": params["image"],
            "network_id": network_id,
            "storage_id": storage_id,
            "status": "aprovisionada"
        }
        return True, self.vm_id, None
    
    def get_vm_info(self) -> dict:
        return self.vm_info

# ============= IMPLEMENTACIONES GCP =============

class GCPNetwork(NetworkResource):
    def __init__(self):
        self.network_id = None
        self.network_info = {}
        
    def create_network(self, params: dict) -> tuple[bool, Optional[str], Optional[str]]:
        required = ["networkName", "subnetworkName", "firewallTag"]
        for r in required:
            if r not in params:
                return False, None, f"Falta parámetro de red GCP: {r}"
        
        self.network_id = f"gcp-net-{hash(str(params)) % 1000}"
        self.network_info = {
            "network_name": params["networkName"],
            "subnetwork_name": params["subnetworkName"],
            "firewall_tag": params["firewallTag"],
            "status": "disponible"
        }
        return True, self.network_id, None
    
    def get_network_info(self) -> dict:
        return self.network_info

class GCPStorage(StorageResource):
    def __init__(self):
        self.storage_id = None
        self.storage_info = {}
        
    def create_storage(self, params: dict) -> tuple[bool, Optional[str], Optional[str]]:
        required = ["diskType", "sizeGB", "autoDelete"]
        for r in required:
            if r not in params:
                return False, None, f"Falta parámetro de almacenamiento GCP: {r}"
        
        self.storage_id = f"gcp-disk-{hash(str(params)) % 1000}"
        self.storage_info = {
            "disk_type": params["diskType"],
            "size_gb": params["sizeGB"],
            "auto_delete": params["autoDelete"],
            "status": "disponible"
        }
        return True, self.storage_id, None
    
    def get_storage_info(self) -> dict:
        return self.storage_info

class GCPVM(VMResource):
    def __init__(self):
        self.vm_id = None
        self.vm_info = {}
        
    def create_vm(self, params: dict, network_id: str, storage_id: str) -> tuple[bool, Optional[str], Optional[str]]:
        required = ["machine_type", "zone", "project"]
        for r in required:
            if r not in params:
                return False, None, f"Falta parámetro de VM GCP: {r}"
        
        self.vm_id = f"gcp-vm-{hash(str(params) + network_id + storage_id) % 1000}"
        self.vm_info = {
            "machine_type": params["machine_type"],
            "zone": params["zone"],
            "project": params["project"],
            "network_id": network_id,
            "storage_id": storage_id,
            "status": "aprovisionada"
        }
        return True, self.vm_id, None
    
    def get_vm_info(self) -> dict:
        return self.vm_info

# ============= IMPLEMENTACIONES ON-PREMISE =============

class OnPremiseNetwork(NetworkResource):
    def __init__(self):
        self.network_id = None
        self.network_info = {}
        
    def create_network(self, params: dict) -> tuple[bool, Optional[str], Optional[str]]:
        required = ["physicalInterface", "vlanId", "firewallPolicy"]
        for r in required:
            if r not in params:
                return False, None, f"Falta parámetro de red OnPremise: {r}"
        
        self.network_id = f"onprem-net-{hash(str(params)) % 1000}"
        self.network_info = {
            "physical_interface": params["physicalInterface"],
            "vlan_id": params["vlanId"],
            "firewall_policy": params["firewallPolicy"],
            "status": "disponible"
        }
        return True, self.network_id, None
    
    def get_network_info(self) -> dict:
        return self.network_info

class OnPremiseStorage(StorageResource):
    def __init__(self):
        self.storage_id = None
        self.storage_info = {}
        
    def create_storage(self, params: dict) -> tuple[bool, Optional[str], Optional[str]]:
        required = ["storagePool", "sizeGB", "raidLevel"]
        for r in required:
            if r not in params:
                return False, None, f"Falta parámetro de almacenamiento OnPremise: {r}"
        
        self.storage_id = f"onprem-stor-{hash(str(params)) % 1000}"
        self.storage_info = {
            "storage_pool": params["storagePool"],
            "size_gb": params["sizeGB"],
            "raid_level": params["raidLevel"],
            "status": "disponible"
        }
        return True, self.storage_id, None
    
    def get_storage_info(self) -> dict:
        return self.storage_info

class OnPremiseVM(VMResource):
    def __init__(self):
        self.vm_id = None
        self.vm_info = {}
        
    def create_vm(self, params: dict, network_id: str, storage_id: str) -> tuple[bool, Optional[str], Optional[str]]:
        required = ["cpu", "ram"]
        for r in required:
            if r not in params:
                return False, None, f"Falta parámetro de VM OnPremise: {r}"
        
        self.vm_id = f"onprem-vm-{hash(str(params) + network_id + storage_id) % 1000}"
        self.vm_info = {
            "cpu": params["cpu"],
            "ram": params["ram"],
            "network_id": network_id,
            "storage_id": storage_id,
            "status": "aprovisionada"
        }
        return True, self.vm_id, None
    
    def get_vm_info(self) -> dict:
        return self.vm_info