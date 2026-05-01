"""
importar_para_db.py — Atalho para importar os JSONs de dados_processados/ para o banco.

USO:
    python pipeline_dados/scripts/importar_para_db.py

Isso é equivalente a rodar:
    python manage.py import_course_data
"""

import os
import subprocess
import sys

# Raiz do projeto Django (dois níveis acima de scripts/)
RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    print("Iniciando importação para o banco de dados...")
    result = subprocess.run(
        [sys.executable, "manage.py", "import_course_data"],
        cwd=RAIZ_PROJETO
    )
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
