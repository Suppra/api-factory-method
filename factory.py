from providers.aws import AWSProvider
from providers.azure import AzureProvider
from providers.gcp import GCPProvider
from providers.onpremise import OnPremiseProvider

class VMFactory:
    _providers = {
        'aws': AWSProvider,
        'azure': AzureProvider,
        'gcp': GCPProvider,
        'onpremise': OnPremiseProvider
    }

    @classmethod
    def get_provider(cls, name):
        provider_cls = cls._providers.get(name)
        if not provider_cls:
            raise ValueError(f"Proveedor '{name}' no soportado")
        return provider_cls()

    @classmethod
    def register_provider(cls, name, provider_cls):
        cls._providers[name] = provider_cls
