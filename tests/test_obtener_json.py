import sys
import os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(root, "src"))

import pytest
from obtener_json import extraer_datos_recibo
from fixtures_recibos import CASOS_RECIBO


class TestObtenerJson:
    @pytest.mark.parametrize("nombre, caso", CASOS_RECIBO.items())
    def test_extraccion_recibo(self, nombre, caso):
        input_data = caso["input"]
        esperado = caso["esperado"]

        resultado = extraer_datos_recibo(input_data)

        assert resultado is not None, f"Falló para {nombre}: resultado None"

        for campo, valor_esperado in esperado.items():
            assert campo in resultado, f"Falló para {nombre}: campo '{campo}' no encontrado. Resultado: {resultado}"
            assert resultado[campo] == valor_esperado, (
                f"Falló para {nombre}, campo '{campo}': "
                f"esperado={valor_esperado}, obtenido={resultado.get(campo)}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
