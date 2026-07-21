# 🐾 Capi_Busque

> **"Capi acha pra você!"**
>
> 🔗 **Deploy:** [capibusque-production.up.railway.app](https://capibusque-production.up.railway.app/)

**Capi_Busque** é uma plataforma web inteligente desenvolvida em Django para otimizar o ingresso de candidatos nas universidades públicas da Região Metropolitana de Belém e do Pará — **UFPA, UEPA, IFPA e UFRA**.

O sistema cruza o perfil socioeconômico do candidato (origem escolar, renda, raça/cor, deficiência) com um banco de dados histórico de notas de corte, identificando automaticamente **qual cota o candidato tem direito** e qual delas exige a **menor nota de entrada** — maximizando suas chances de aprovação.

---

## 🚀 Funcionalidades

### 🔍 Simulador de Cotas com Efeito Cascata
O coração do sistema. O candidato informa seu perfil socioeconômico e o motor de inferência:
1. Identifica a cota mais específica para cada universidade (UFPA, UEPA, IFPA, UFRA);
2. Aplica o **Algoritmo de Cascata**: gera todas as cotas em que o candidato tem direito legal de concorrer (da mais restrita até a Ampla Concorrência);
3. Realiza uma varredura no histórico de cortes e retorna a **cota de menor nota de entrada**, minimizando o esforço do candidato.

### 🧮 Calculadora TRI (Heurística Otimista)
Estima a nota TRI do ENEM com base no número de acertos brutos por área de conhecimento (0–45), usando tabelas estatísticas históricas. Projeta o **limite superior da nota** (cenário otimista) e compara com os cursos favoritados.

### ⭐ Gerenciador de Favoritos
- Funciona **com ou sem login**: usuários não autenticados usam sessão; usuários logados têm perfil persistido no banco.
- Salva cursos de interesse para comparação direta na Calculadora TRI.

### 📉 Alerta de Vagas Sobrando
Lista cursos com histórico de vagas remanescentes, identificando oportunidades onde **não zerar o ENEM já é suficiente** para ingressar.

### 💬 Sistema de Comentários
Usuários autenticados podem deixar depoimentos sobre a plataforma, com campo de avaliação ("O site te ajudou?") e moderação pelo admin Django.

### 📖 Dicionário de Cotas
Guia completo que traduz a "sopa de letrinhas" dos editais (L1, L2, AC, ERPPI, RI_Q, LB_PPI, Grupo D…), unificando as nomenclaturas divergentes entre as universidades.

---

## 🗺️ Rotas do Projeto

| Rota | App | Descrição |
|---|---|---|
| `/` | `core` | Dashboard com cursos aleatórios em destaque |
| `/regras-cotas/` | `core` | Dicionário de Cotas |
| `/cotas/buscar/` | `cota_min_and_max_enem` | Simulador principal de cotas |
| `/cotas/registro/` | `cota_min_and_max_enem` | Criação de conta |
| `/cotas/login/` | `cota_min_and_max_enem` | Login |
| `/cotas/logout/` | `cota_min_and_max_enem` | Logout |
| `/sobras/` | `vagas_sobrando` | Alerta de vagas sobrando |
| `/favoritos/` | `favoritos` | Lista de cursos favoritados |
| `/favoritos/adicionar/<id>/` | `favoritos` | Adicionar favorito |
| `/favoritos/remover/<id>/` | `favoritos` | Remover favorito |
| `/calculadora/` | `calculadora` | Calculadora TRI com favoritos |
| `/comentarios/` | `comentarios` | Depoimentos de usuários |
| `/admin/` | Django Admin | Painel administrativo |

---

## 🏗️ Arquitetura

O projeto segue o padrão **MVT (Model-View-Template)** do Django com arquitetura **multi-app modular**:

```
capi_busque/
├── core/                        # Configurações centrais, URLs raiz, dashboard e view de regras
├── cota_min_and_max_enem/       # App principal: autenticação, perfil do candidato, busca
│   ├── motor_cotas/             # Módulo Python puro (motor de inferência de cotas)
│   │   ├── verificador_cotas.py # PerfilCandidato (dataclass) + AvaliadorDeCotas + cascata
│   │   ├── buscador_notas.py    # BuscadorDeNotas: query no BD com o perfil e avaliador
│   │   └── categorizador_cursos.py
│   └── management/              # Commands personalizados (ingestão de dados)
├── calculadora/                 # Calculadora TRI com comparação de favoritos
├── favoritos/                   # Gerenciamento de favoritos (sessão + DB)
├── comentarios/                 # Sistema de depoimentos com moderação
├── vagas_sobrando/              # Filtro de cursos com vagas remanescentes
└── pipeline_dados/              # ETL offline: extração e normalização de JSONs/PDFs das bancas
```

### Motor de Cotas (`motor_cotas/`)

O módulo `motor_cotas` é **desacoplado do Django** — é Python puro, importado como biblioteca pelas views. Contém:

- **`PerfilCandidato`** (dataclass): encapsula `escola_publica`, `renda_sm`, `raca`, `pcd`.
- **`AvaliadorDeCotas`**: implementa a lógica específica de cada instituição:
  - **IFPA** → categorias `RI_` (renda inferior) e `IR_` (independente de renda)
  - **UFPA** → acrônimos (`E`, `ER`, `EPPI`, `ERPPI`, `EPCD`, `ERPCD`, `ERQ`, `EQ`, `PCDA`, `AC`)
  - **UEPA** → grupos alfabéticos (`A` a `J`)
  - **UFRA** → prefixos SiSU (`LB_` / `LI_`)
- **`obter_cascata_de_cotas(faculdade)`**: gera a lista ordenada de cotas válidas, relaxando progressivamente as restrições do perfil até chegar na Ampla Concorrência.
- **`BuscadorDeNotas`**: recebe o perfil e executa as queries no banco, retornando a cota de menor nota histórica de corte.

### Modelos de Dados

- **`CourseOffering`**: oferta de curso (instituição, nome, campus, turno, vagas preenchidas, vagas sobrando).
- **`QuotaData`**: detalha cada cota de uma oferta — `quota_code`, `previous_cutoff`, `historical_max_score`, campos booleanos semânticos (`is_ppi`, `requer_renda_baixa`, `is_quilombola`…).
- **`PerfilCandidatoDB`**: perfil socioeconômico do usuário autenticado (1-to-1 com `User`).
- **`Comentario`**: depoimento com texto, avaliação e flag de moderação (`ativo`).

### Estratégia de Autenticação / Sessão

A busca funciona para **usuários anônimos e autenticados**:

| Situação | Perfil | Favoritos |
|---|---|---|
| Usuário anônimo | `request.session` | `request.session` |
| Usuário autenticado | `PerfilCandidatoDB` (banco) | `request.session` |

---

## 🛠️ Stack Tecnológico

| Camada | Tecnologia |
|---|---|
| Backend | Python 3 + Django |
| Frontend | HTML5 semântico, CSS3 Nativo (tema Cyberpunk/Hacker), JavaScript Vanilla |
| Banco de Dados | SQLite (desenvolvimento) / PostgreSQL-ready via ORM |
| Deploy | Railway |
| Autenticação | Django Auth (`User`, `AuthenticationForm`) |

---

## ⚙️ Como executar localmente

**1. Clone o repositório:**
```bash
git clone https://github.com/rodrigosousa64/capi_busque.git
cd capi_busque
```

**2. Crie e ative o ambiente virtual:**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

**3. Instale as dependências:**
```bash
pip install -r requirements.txt
```

**4. Execute as migrações:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**5. (Opcional) Popule o banco via pipeline de dados:**
```bash
# Consulte os management commands em cota_min_and_max_enem/management/
python manage.py <nome_do_command>
```

**6. Inicie o servidor de desenvolvimento:**
```bash
python manage.py runserver
```

Acesse: `http://127.0.0.1:8000`

---

*// Capi_Busque acha pra você!*

