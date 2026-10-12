# Automação de Testes API ServeRest — Topic 2 (GenAI)

Projeto educacional de QA com **Python + Pytest + Requests**, estruturado de acordo com o plano da API do Topic 1.

## Requisitos
Python 3.10+; acesso à API `https://compassuol.serverest.dev` ou instância ServeRest compatível.

## Instalação
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Execução
```bash
# Validações offline da suíte, sem API externa
python -m pytest tests/test_local_validation.py -v

# Testes de integração reais; ambiente padrão é o target do exercício
python -m pytest tests/test_live_api.py --run-live -v --junitxml=evidence/junit-live.xml

# Workaround temporario para o certificado invalido do endpoint publico
python -m pytest tests/test_live_api.py --run-live --insecure-live -v

# Trocar API (instância local ou outra autorizada)
BASE_URL=http://localhost:3000 python -m pytest tests/test_live_api.py --run-live -v
```
No Windows PowerShell: `$env:BASE_URL='http://localhost:3000'` antes do comando.
Use `--insecure-live` somente quando o endpoint HTTPS apresentar erro de certificado
e apenas em ambiente de testes autorizado; a verificacao TLS permanece habilitada por padrao.

## Escopo
24 IDs rastreáveis `API-01` a `API-24`, alguns parametrizados. Login, usuários, produtos, carrinho, autenticação, estoque e bordas. Fixtures criam e removem dados isolados; tokens obtidos dinamicamente.

## Avisos
- Testes em `test_live_api.py` ficam **SKIP** sem `--run-live`; não confundir testes offline com validação real da API.
- Os dados do ambiente público podem mudar ou ser reiniciados. Evite testes paralelos com as mesmas contas.
- Cuidado com emissão de relatórios contendo senha/token. Não publique logs de credenciais.
- A API alvo é uma variante Compass UOL. Verifique possíveis diferenças no Swagger específico caso surjam falhas de contrato.
- Executar integração pode criar/modificar dados da aplicação alvo. Usar somente ambiente de testes autorizado.

## Relatórios e IA
Documentação, matrizes e ajustes em `docs_genai.md`; evidências em `evidence/`.
