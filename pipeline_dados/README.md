# Pipeline de Dados

Área centralizada para gerenciar o fluxo de dados do sistema de cotas.

## Fluxo de Trabalho

```
brutos/          →    scripts/extrair_pdf.py    →    dados_processados/    →    Banco de Dados
(PDFs aqui)           (converte para JSON)           (JSONs organizados)        (manage.py import_course_data)
```

## Pastas

- **`brutos/`** — NÃO rastreado pelo git. Coloque os PDFs dos listões aqui.
- **`dados_processados/`** — Rastreado pelo git. JSONs organizados por instituição/ano/turno.
- **`scripts/`** — Scripts de automação.

## Estrutura de `dados_processados/`

```
dados_processados/
└── {INSTITUICAO}/          ex: UFPA, IFPA, UEPA, UFRA
    └── {ANO}/              ex: 2026, 2027
        └── {TURNO}/        ex: matutino, vespertino, noturno, nao_informado
            └── {curso}_{campus}.json
```

## Formato do JSON

```json
{
    "institution": "UFPA",
    "year_reference": 2026,
    "offerings": [
        {
            "course": "Nome Do Curso",
            "campus": "Belém",
            "degree": "Bacharelado",
            "shift": "Matutino",
            "total_spots_filled": 40,
            "competition_data": [
                {
                    "quota_code": "AC",
                    "description": "Ampla Concorrência",
                    "spots": 20,
                    "previous_cutoff": 750.50,
                    "historical_max_score": 810.20
                }
            ]
        }
    ]
}
```

## Códigos de Cota por Instituição

### IFPA
`AC`, `L1`, `L2`, `L3`, `L4`, `L5`, `L6`, `L7`, `L8`

### UFPA
`AC`, `PCDA`, `E`, `EPCD`, `EQ`, `EPPI`, `ER`, `ERPCD`, `ERQ`, `ERPPI`

### UEPA
`A`, `B`, `C`, `D`, `E`, `F`, `G`, `H`, `I`, `J`

### UFRA
`AC`, `LB_EP`, `LB_PPI`, `LB_Q`, `LB_PCD`, `LI_EP`, `LI_PPI`, `LI_PCD`

## Como importar para o banco

```bash
# Da pasta raiz do projeto Django:
python manage.py import_course_data
```
