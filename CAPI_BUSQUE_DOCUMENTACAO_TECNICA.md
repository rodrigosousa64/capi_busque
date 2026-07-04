# Documentação Técnica e Metodológica: Capi_Busque

O **Capi_Busque** é um sistema inteligente de otimização para ingresso universitário, desenvolvido com foco nas universidades da Região Metropolitana de Belém e Pará (UFPA, UEPA, IFPA e UFRA). Este documento detalha a arquitetura tecnológica e as metodologias algorítmicas empregadas no projeto.

## 1. Stack Tecnológico e Arquitetura

A aplicação foi projetada utilizando o padrão arquitetural **MVT (Model-View-Template)** inerente ao framework escolhido, privilegiando modularidade e manutenibilidade.

### Backend
* **Linguagem:** Python
* **Framework Web:** Django
* **Arquitetura Modular (Multi-App):** O projeto não é monolítico em seu domínio, sendo fragmentado em módulos altamente coesos e de baixo acoplamento:
  * `core/`: Configurações centrais, roteamento e templates base.
  * `cota_min_and_max_enem/`: Motor principal de cruzamento de notas e cálculo do Efeito Cascata.
  * `calculadora/`: Lógica de estimativa de Teoria de Resposta ao Item (TRI).
  * `favoritos/` e `comentarios/`: Gerenciamento de estado de usuário logado (CRUD relacional atrelado a IDs de cursos).
  * `vagas_sobrando/` e `pipeline_dados/`: Ingestão, tratamento e modelagem dos dados de ingresso e vagas remanescentes.

### Frontend
* **Tecnologias:** HTML5 semântico, CSS3 Nativo, JavaScript (Vanilla).
* **Diretriz de Design:** Utilização de uma interface de temática "Cyberpunk/Hacker", implementada puramente via CSS/JS nativos para minimizar o *payload* de bibliotecas externas. A escolha por JS Vanilla garante manipulação direta do DOM em tempo real, crucial para os formulários iterativos de entrada de dados do candidato sem overhead de Virtual DOM.

### Banco de Dados
* **SGBD Atual:** SQLite
* **Modelagem:** Estrutura relacional forte, desenhada para representar as complexas associações entre `Candidatos` (perfis), `Cursos`, `Universidades` e os diferentes tipos de `Cotas/Grupos de Concorrência`. Permite migração contínua para SGBDs mais robustos (como PostgreSQL) em ambientes de produção através da camada de abstração do ORM (Object-Relational Mapping) do Django.

---

## 2. Metodologias Algorítmicas e Regras de Negócio

### 2.1 Algoritmo de "Match" de Cotas (Árvore de Decisão e Busca de Custo Mínimo)
O "Simulador de Cotas Inteligente" não é apenas um filtro simples, mas um motor de inferência legal:
1. **Modelagem do Espaço de Estados:** O perfil do candidato é mapeado através de variáveis booleanas e categóricas restritas (Ex: `escola_publica = True`, `renda_per_capita <= 1.5_sm`, `etnia in ['pardo', 'preto', 'indigena']`, `pcd = False`).
2. **Motor de Efeito Cascata:** O algoritmo utiliza regras lógicas fundamentadas nos editais (ex: Lei de Cotas) para expandir as opções de concorrência. Se um candidato se enquadra na cota máxima (L2/L10, por exemplo), o sistema deduz através de herança que ele pode concorrer de forma legítima nas instâncias superiores (Ampla Concorrência, Cotas de Renda, etc.).
3. **Otimização da Escolha:** Após gerar o conjunto de cotas legalmente válidas para o perfil, o sistema realiza uma varredura (query) no histórico das notas de corte e aplica uma função objetivo de minimização: $CotaIdeal = \arg\min (\text{NotaCorte}_{Cota})$ para as cotas validadas. Retornando a "trajetória de menor esforço" para a aprovação.

### 2.2 Pipeline de Ingestão de Dados (Processamento Offline e ETL)
O módulo `pipeline_dados` gerencia o ciclo de vida dos dados históricos dos processos seletivos.
* **Extração:** Coleta de dados dispersos (arquivos JSON e PDFs gerados pelas bancas das instituições).
* **Transformação e Normalização:** O motor de cotas aplica um "Dicionário de Cotas" interno (padronização de códigos divergentes das universidades). Diferentes nomenclaturas para o mesmo critério (Ex: Cotista de Escola Pública Indígena na universidade X vs Y) são unificadas para permitir consultas agregadas limpas no banco de dados.

### 2.3 Calculadora TRI por Heurística Otimista
A implementação de uma simulação da TRI (Teoria de Resposta ao Item) foca na experiência do usuário de maneira performática:
* **Problema:** A TRI oficial do Inep exige acesso ao modelo logístico de 3 parâmetros e respostas item-a-item de toda a base de candidatos, inviável de ser calculado por indivíduos.
* **Solução Heurística:** A aplicação emprega tabelas de correspondência estatísticas históricas baseadas no volume de acertos brutos (0 a 45) por área de conhecimento.
* **Projeção Otimista:** O modelo assume um alto índice de coerência pedagógica nas respostas (ex: acertar fáceis e errar difíceis), traçando o limite superior da nota daquele espectro de acertos e aplicando os pesos do curso desejado para auxiliar na tomada de decisão estratégica do candidato.

### 2.4 Análise Preditiva de Oportunidades ("Alerta de Sobras")
Sistema focado em identificar cursos (frequentemente licenciaturas e algumas engenharias) que possuem um histórico de demanda menor do que a oferta de vagas. A lógica no banco identifica entidades `Curso` cujo critério de corte no histórico foi "Não Zerar a Prova", alertando estrategicamente os candidatos dessas oportunidades garantidas.

---
*Documento gerado para fins de apresentação de arquitetura técnica e validação de engenharia de software da plataforma.*
