class AzureProvider:
    def create_vm(self, params):
        required = ["size", "resource_group", "image", "vnet"]
        for r in required:
            if r not in params:
                return False, None, f"Falta parámetro Azure: {r}"
        return True, "azure-vm-456", None
