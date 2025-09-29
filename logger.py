import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vm_api")

SENSITIVE_KEYS = {"password", "token", "secret", "key"}

def safe_log(msg, params):
    filtered = {k: ("***" if k.lower() in SENSITIVE_KEYS else v) for k, v in params.items()}
    logger.info(f"{msg}: {filtered}")
