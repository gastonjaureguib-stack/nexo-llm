
class LLMError(Exception):
    """Error general de Nexo LLM."""
    pass


class LLMAuthenticationError(LLMError):
    """La API rechazó las credenciales."""
    pass


class LLMConnectionError(LLMError):
    """No fue posible establecer conexión con la API."""
    pass


class LLMRateLimitError(LLMError):
    """Se alcanzó el límite de solicitudes de la API."""
    pass


class LLMAPIError(LLMError):
    """La API devolvió un error no contemplado."""
    pass
