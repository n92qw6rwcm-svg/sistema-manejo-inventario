"""
Configuración de rutas para test
Se agregó para solucionar el ruteo entre módulos. 
Además, creo que es la repsuesta a un cuestionamiento que surgió hace tiempo: 
¿Cómo solucionar el ruteo entre carpetas? 
No es una respuesta absolutista, es una solución. 
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
