# 🐾 CAPI_BUSQUE

**Capi_Busque** é um sistema inteligente desenvolvido em Django focado em otimizar a entrada de estudantes nas universidades públicas da Região Metropolitana de Belém e estado do Pará (**UFPA, UEPA, IFPA e UFRA**).

O algoritmo da plataforma cruza o perfil socioeconômico do candidato (renda, origem escolar, cor/raça, deficiência) com um extenso banco de dados de notas de corte de processos seletivos anteriores, indicando com exatidão **qual cota o aluno tem direito** e qual delas exige a **menor nota para aprovação**.

## 🚀 Funcionalidades Principais

- **Simulador de Cotas Inteligente:** O candidato informa suas características (ex: "Escola Pública", "Renda até 1 salário mínimo", "Pardo") e o sistema vasculha o banco de dados para encontrar em qual cota ele se encaixa.
- **Análise Histórica de Notas:** As vagas listadas e suas respectivas notas mínimas/máximas são baseadas em dados reais das últimas chamadas.
- **Efeito Cascata:** O algoritmo mostra não só a cota principal recomendada, mas também as outras cotas em que o candidato tem o direito legal de concorrer (ex: Ampla Concorrência).
- **Calculadora TRI Simples:** Uma ferramenta que permite estimar a nota final baseada em acertos brutos (0 a 45) nas áreas de conhecimento do ENEM, usando simulações Otimistas (coerência alta na prova) para comparar com os cursos favoritados.
- **Gerenciador de Favoritos:** Crie uma conta gratuitamente e salve seus cursos de interesse para compará-los futuramente na calculadora TRI.
- **Alerta de Sobras:** Sistema dedicado para indicar quais cursos da universidade costumam ter "sobras" de vagas (onde basta ter não zerado no ENEM para passar).
- **Dicionário de Cotas:** Um guia que destrincha a "sopa de letrinhas" dos editais das universidades, explicando o que significa cada código (L1, L2, L3, [AC], [EPPI], etc).

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python + Django
- **Frontend:** HTML5, CSS3 Nativo (Interface Cyberpunk/Hacker), JavaScript Vanilla
- **Banco de Dados:** SQLite (padrão)
- **Estrutura de Dados:** Processamento off-line de grandes arquivos JSON/PDF transformados no motor de cotas do sistema.

## ⚙️ Como executar o projeto localmente

1. Clone o repositório:
```bash
git clone https://github.com/rodrigosousa64/capi_busque.git
cd capi_busque
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute as migrações:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Rode o servidor de desenvolvimento:
```bash
python manage.py runserver
```

Acesse no seu navegador: `http://127.0.0.1:8000`

---
*// Capi_Busque acha pra você!*