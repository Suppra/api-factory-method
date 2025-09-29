class GCPProvider:
    def create_vm(self, params):
        required = ["machine_type", "zone", "disk", "project"]
        for r in required:
            if r not in params:
                return False, None, f"Falta parámetro GCP: {r}"
        return True, "gcp-vm-789", None
