# infrastructure/agents/wikipedia/wikipedia_agent.py

import requests
import mwparserfromhell

from application.interfaces.agent_interface import AgentInterface


class WikipediaAgent(AgentInterface):
    """
    Agente encargado de consultar y extraer el contenido de una página de Wikipedia.

    Este agente implementa el contrato definido en `AgentInterface`, y utiliza la API pública de Wikipedia
    para obtener el contenido de un artículo dado su título. Posteriormente, limpia el contenido usando
    `mwparserfromhell` para eliminar wikitexto, plantillas y etiquetas.

    Método principal:
        - run(input_data: str) -> str: Ejecuta la consulta para el artículo indicado y retorna su contenido limpio.
    """

    def run(self, input_data: str) -> str:
        """
        Ejecuta la consulta al artículo de Wikipedia con el título dado.

        Args:
            input_data (str): Título del artículo de Wikipedia (ej. "Albert Einstein").

        Returns:
            str: Contenido limpio del artículo (texto plano).

        Raises:
            RuntimeError: Si el artículo no existe o no se pudo obtener contenido válido.
        """
        try:
            response = requests.get(
                url="https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "format": "json",
                    "titles": input_data,
                    "prop": "revisions",
                    "rvprop": "content",
                },
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            page = next(iter(data["query"]["pages"].values()))

            # Validación básica
            if "revisions" not in page or not page["revisions"]:
                raise RuntimeError(f"No se encontró contenido para: {input_data}")

            wikitext = page["revisions"][0].get("*") or page["revisions"][0].get("slots", {}).get("main", {}).get("*")

            if not wikitext:
                raise RuntimeError(f"Artículo sin contenido accesible: {input_data}")

            parsed = mwparserfromhell.parse(wikitext)
            clean_text = parsed.strip_code()

            return clean_text.strip()

        except Exception as e:
            raise RuntimeError(f"Error al consultar Wikipedia: {str(e)}")
