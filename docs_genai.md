# Registro de IA e validação humana — Topic 2

**IA escolhida:** ChatGPT (GPT-6). **Stack:** Python + Pytest + Requests.

## Prompts aplicados (registro sintetizado e fiel à tarefa)
1. **Papel/contexto:** "Atue como QA Automation sênior. API ServeRest Compass UOL, plano Topic 1, Python/Pytest/Requests."
2. **Objetivo:** "Implemente API-01 a API-24, cenários positivos, negativos e limites, usando fixtures isoladas, autenticação real e limpeza de dados."
3. **Restrições:** "Não invente rotas; use Swagger; asserts explícitos; não compartilhar tokens; integração deve ser opt-in."
4. **Refatoração:** "Extraia cliente HTTP e fixtures de usuário/admin/produto; parametrização sem multiplicar fixtures desnecessariamente."
5. **Revisão:** "Inspecione divergências de status, regras de estoque, criação via PUT, resultado de ausência de carrinho, acesso de usuário comum e evidência de execução."
6. **Documentação:** "Gere README, matriz rastreável e comandos JUnit; declare claramente testes não executados."

## Revisões e ajustes humanos/curadoria QA
- A1: substituído cadastro hardcoded por email e produto com UUID para evitar colisões.
- A2: autenticação real via POST /login; conferência de prefixo Bearer.
- A3: privilégios do produto: somente admin, usuário normal esperado 403.
- A4: DELETE de carrinho: concluir não repõe estoque; cancelar repõe.
- A5: GET por ID inexistente usa 400 documentado, em vez de assumir 404.
- A6: PUT do ServeRest pode criar um novo registro, logo não assumir 404 geral.
- A7: conftest usa cleanup em fixtures; após concluir, desconto no estoque é esperado.
- A8: testes de integração opt-in evitam escrita acidental no host público.
- A9: testes offline de contrato interno são discriminados dos de integração.
- A10: evidência de indisponibilidade de DNS não é rotulada como falha funcional da API.

## Limitações e próximos passos
Executar integração real num ambiente com acesso à URL alvo; revisar eventuais diferenças na variante Compass; obter screenshot/report real e publicar o repositório. Não há alegação de aprovação dos testes live sem execução.
