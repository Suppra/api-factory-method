class AWSProvider:
    def create_vm(self, params):
        # Validación específica AWS
        required = ["instance_type", "region", "vpc", "ami"]
        for r in required:
            if r not in params:
                return False, None, f"Falta parámetro AWS: {r}"
        # Simulación de creación
        return True, "aws-vm-123", None
