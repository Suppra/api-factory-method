from fastapi import FastAPI, HTTPException
from models import VMRequest, VMResponse
from factory import VMFactory
from logger import safe_log

app = FastAPI()

@app.post("/provision_vm", response_model=VMResponse)
def provision_vm(request: VMRequest):
    provider_name = request.provider.lower()
    params = request.params
    safe_log(f"Solicitud aprovisionamiento {provider_name}", params)
    try:
        provider = VMFactory.get_provider(provider_name)
        success, vm_id, error = provider.create_vm(params)
        if success:
            return VMResponse(success=True, vm_id=vm_id)
        else:
            return VMResponse(success=False, error=error)
    except Exception as e:
        return VMResponse(success=False, error=str(e))
