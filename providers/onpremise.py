class OnPremiseProvider:
    def create_vm(self, params):
        required = ["cpu", "ram", "disk", "network"]
        for r in required:
            if r not in params:
                return False, None, f"Falta parámetro OnPremise: {r}"
        return True, "onprem-vm-001", None
