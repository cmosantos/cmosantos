# remote-job-radar

Projeto Python que coleta vagas remotas na Himalayas, aplica filtros de compatibilidade e envia alertas no Telegram.

## Arquitetura (v1)

- `main.py`: orquestra o fluxo (coleta -> filtro -> pontuação -> deduplicação -> Telegram).
- `remote_job_radar/collector.py`: integra com a API pública da Himalayas.
- `remote_job_radar/filters.py`: aplica regras de recência, localização, exclusão e modalidade.
- `remote_job_radar/scorer.py`: calcula pontuação de compatibilidade (0 a 100).
- `remote_job_radar/storage.py`: persiste histórico de vagas enviadas em JSON.
- `remote_job_radar/telegram_client.py`: monta e envia mensagens para Telegram.
- `tests/`: testes básicos de filtros e pontuação.

## Estrutura de pastas

```text
remote-job-radar/
├── .env.example
├── .gitignore
├── README.md
├── main.py
├── requirements.txt
├── data/
├── remote_job_radar/
│   ├── __init__.py
│   ├── collector.py
│   ├── filters.py
│   ├── scorer.py
│   ├── storage.py
│   └── telegram_client.py
└── tests/
    ├── test_filters.py
    └── test_scorer.py
```

## Requisitos

- Python 3.12
- Variáveis de ambiente:
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_CHAT_ID`

## Como criar um bot no Telegram

1. Abra o Telegram e procure por **@BotFather**.
2. Envie `/newbot`.
3. Defina nome e username do bot.
4. Copie o token gerado (ele será usado em `TELEGRAM_BOT_TOKEN`).

## Como descobrir o Chat ID

1. Envie uma mensagem para o seu bot no Telegram (pode ser "oi").
2. Acesse no navegador (substituindo o token):

```text
https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getUpdates
```

3. No JSON retornado, localize `message.chat.id`.
4. Use esse valor em `TELEGRAM_CHAT_ID`.

## Como cadastrar os GitHub Secrets

No repositório GitHub:

1. Vá em **Settings** -> **Secrets and variables** -> **Actions**.
2. Clique em **New repository secret**.
3. Crie:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

## Como testar localmente

```bash
cd remote-job-radar
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Defina as variáveis de ambiente no shell:

```bash
export TELEGRAM_BOT_TOKEN="seu_token"
export TELEGRAM_CHAT_ID="seu_chat_id"
```

Execute o projeto:

```bash
python main.py
```

Execute os testes:

```bash
pytest
```

## Como executar manualmente no GitHub Actions

1. Abra a aba **Actions** no repositório.
2. Selecione o workflow **Remote Job Radar**.
3. Clique em **Run workflow**.
4. Aguarde a conclusão e consulte os logs.

## Observações

- O histórico de vagas já enviadas é salvo em `data/sent_jobs.json`.
- Só envia vagas com pontuação mínima 70.
- Regras de filtro da v1:
  - últimas 24h;
  - remoto compatível (Brazil/LATAM/Américas/Worldwide/Global/Anywhere);
  - exclusão de vagas restritas somente a US/Canadá/Europa;
  - exclusão de cargos de direção/gestão sênior, vendas, desenvolvimento de software e vagas presenciais/híbridas.
- Fonte dos dados: Himalayas.
