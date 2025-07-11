# Projeto 2 - Comprehensive Data Integration & Research Assessment

Dashboard interativo desenvolvido em Python usando Streamlit, pandas e plotly para análise e visualização de dados do corpo docente da faculdade IPT.

## ✨ Funcionalidades

- Visualização de informações do corpo docente em gráficos dinâmicos
- Distribuição por categoria, vínculo e outras características
- Filtros e seleção interativa de dados
- Leitura de arquivos CSV (detecta delimitador automaticamente)
- Interface simples e responsiva acessível via navegador

## 🚀 Como rodar o projeto

1. **Clone o repositório**

   ```bash
   git clone https://github.com/seu-usuario/seu-repo.git
   cd seu-repo
   ```

2. **(Opcional) Crie um ambiente virtual**

   ```bash
   python -m venv .venv
   # Ative o ambiente virtual:
   source .venv/bin/activate    # Linux/Mac
   .venv\Scripts\activate       # Windows
   ```

3. **Instale as dependências**

   ```bash
   pip install -r requirements.txt
   ```
   Se não tiver o arquivo `requirements.txt`, instale manualmente:

   ```bash
   pip install streamlit pandas plotly
   ```

4. **Adicione os arquivos CSV necessários na raiz do projeto**
   - Exemplo: `faculdade_completo.csv`, `quem_e_quem.csv`,`google_scholar_busca_automatica.csv`, `scrapping_scopus_metrics_limpo.csv`, `faculdade_completo.csv`.

5. **Execute o dashboard**

   ```bash
   streamlit dashboard.py
   ```
   *Troque `dashboard.py` pelo nome do arquivo principal do seu projeto, se for diferente.*

## 🗂 Estrutura dos arquivos

```
.
├── app.py                   # Script principal do dashboard
├── faculdade_completo.csv   # Base de dados principal
├── quem_e_quem.csv         # (Opcional) Base complementar
├── requirements.txt         # Lista de dependências
└── README.md                # Este arquivo
```

## ⚙️ Pré-requisitos

- Python 3.8 ou superior
- Pip


## 👤 Autor

Desenvolvido por Lucas Machado  
Mestrando em Engenharia de Computação | IPT

Contato: aluno26905@ipt.pt