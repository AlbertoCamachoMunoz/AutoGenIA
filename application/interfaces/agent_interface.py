from abc import ABC, abstractmethod

class AgentInterface(ABC):
    """
    Interfaz base que define el contrato genérico para todos los agentes del sistema.

    Los agentes pueden representar funcionalidades como mensajería, scraping, consultas a APIs, etc.
    Cada agente debe implementar este contrato para integrarse con AutoGen u otros orquestadores.
    """

    @abstractmethod
    def run(self, input_data: str) -> str:
        """
        Ejecuta la acción principal del agente con base en la entrada proporcionada.

        Args:
            input_data (str): Información de entrada que el agente debe procesar.

        Returns:
            str: Resultado generado por el agente tras ejecutar su lógica.
        """
        pass
