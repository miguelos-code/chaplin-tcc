# 🧠 Memória do Sistema: Chaplin-TCC

> **Data de Atualização**: 26/06/2026
> **Objetivo**: Registro de segurança compilando absolutamente tudo o que foi feito, alterado e diagnosticado no sistema até o momento. Serve como ponto de restauração de contexto caso a sessão seja interrompida.

---

## ⚙️ 1. Ambiente e Configuração Inicial
- O sistema foi inicializado usando **Django 5.0.3** com banco de dados local **SQLite** (`db.sqlite3`).
- As dependências foram instaladas com sucesso a partir do `requirements.txt`.
- O servidor de desenvolvimento foi rodado com sucesso em `http://localhost:8000`.
- **Testes**: Executamos a suíte de testes do Django e **7/7 testes passaram** sem falhas, confirmando que a base lógica de modelos está íntegra.
- **[26/06/2026]**: Servidor de desenvolvimento reiniciado e estado da memória validado.

## 🛠️ 2. Alterações de Código Realizadas (Changelog)

### `Banco de Dados (db.sqlite3)`
- **Fix do Nome de Usuário**: O `username` "bruno.ferreira" foi renomeado para "misael.jesus" para condizer com o nome da pessoa configurado na conta ("Misael De Jesus"), garantindo consistência no login.
- **Fix das Imagens Quebradas**: Os caminhos das imagens (`photo`) na tabela `TaskEvidence` apontavam para nomes de arquivos temporários gerados por script (ex: `task_6_corredor_escuro_...png`), mas os arquivos reais em `media/evidences/` tinham outros nomes (ex: `lampada_queimada_corredor.png`). Foi criado e executado um script (`fix_images.py`) para atualizar os caminhos no banco de dados e sincronizá-los com os arquivos reais, corrigindo as imagens quebradas nas evidências das tarefas.

### `apps/users/forms.py` & `apps/users/views.py`
- **Fix de Omissão de Campos**: O `AdminUserCreateForm` não continha declaração para CPF e CNPJ, impedindo que o admin gerenciasse esses dados. Os campos foram adicionados no form com as classes `mask-cpf` e `mask-cnpj`.
- **Fix de Views**: As views `admin_user_create_view` e `admin_user_edit_view` foram alteradas para resgatar corretamente CPF, CNPJ e Telefone no método POST e salvá-los no modelo `UserProfile`.

### `apps/tasks/views.py`
- **Fix do Perfil**: A função `settings_view` foi atualizada para gravar no banco de dados o CPF e o CNPJ alterados pelo próprio usuário no menu de configurações.

### `apps/users/templates/users/admin/` & `templates/tasks/settings.html`
- **Fix de Interface e Máscaras**: Os templates `create.html` e `edit.html` (Admin) e `settings.html` (Perfil) sofreram adição de blocos HTML cruciais para exibir os inputs de Telefone, CPF e CNPJ. A classe `mask-phone` foi devidamente atrelada ao input de telefone em `settings.html`, e os campos de documentação agora respeitam a lógica do `IMask` nativo do projeto.

### `apps/tasks/forms.py`
- **Fix de Alinhamento e UI**: Adicionado uma altura fixa unificada (`h-[42px]`) em todas as classes Tailwind de widgets (`TextInput`, `DateInput`, `Select`, `FileInput`) do `TaskForm` e `TaskEvidenceForm`. Isso corrige o desalinhamento visual quando inputs diferentes são colocados lado a lado no layout responsivo. O `TaskEvidenceForm` também recebeu suporte completo às classes de Dark Mode.

### `templates/shared/base_dashboard.html`
- **Fix de Incongruência no Sidebar**: O campo que renderizava o rodapé do menu lateral foi atualizado de `{{ user.username }}` para `{{ user.first_name|default:user.username }}`. Isso garante que a aplicação sempre priorize exibir o nome do usuário amigável, assim como acontece no cabeçalho superior.

### `chaplin_project/settings.py`
- Limpeza de um erro de sintaxe solto (a string solta `default_` na linha 159 foi removida para impedir erro 500 no carregamento das configurações de e-mail).

### `templates/tasks/edit.html`
- **Fix do Dark Mode**: O formulário de edição de tarefas tinha fundo branco ilegível no modo escuro. Foram injetadas as classes do TailwindCSS (`dark:bg-gray-900`, `dark:border-gray-800`, `dark:text-white`, `dark:text-gray-300`) nos cartões e labels do formulário.
- Alteração manual pelo usuário (UI/UX): Remoção do emoji 📍 no subtítulo de endereço, alterado de `"📍 Endereço Completo (via CEP)"` para `"Endereço Completo"`.

## 🗄️ 3. Banco de Dados e Carga de Dados (População)
Um expurgo completo foi feito no banco de dados antigo, e inserimos dados altamente realistas para simular um ambiente de produção (Manutenção Predial).

### Acesso e Usuários (Senha Padrão: `chaplin123`)
Foram configurados 8 usuários baseados no modelo de RBAC (Controle de Acesso Baseado em Papéis):
1. `admin` (Administrador) - Acesso total
2. `gestor` (Gestor do Prédio)
3. `lider` (Líder de Equipe)
4. `colaborador` (Colaborador - Elétrica)
5. `maria.santos` (Colaborador - Hidráulica)
6. `pedro.costa` (Colaborador - Civil)
7. `ana.lima` (Colaborador - Climatização)
8. `bruno.ferreira` (Colaborador - Serralheria)

### Especialidades Criadas
`Elétrica`, `Hidráulica`, `Civil`, `Climatização`, `Serralheria`.

### Tarefas (12 no total, com evidências fotográficas)
1. **[ABERTA]** #6 - Lâmpada queimada no corredor do 3º andar (Foto: Corredor escuro)
2. **[ABERTA]** #7 - Vazamento na tubulação do banheiro masculino (Foto: Água sob a pia)
3. **[ALOCADA]** #8 - Rachadura na parede da escadaria (Foto: Rachadura diagonal)
4. **[ALOCADA]** #9 - Tomada danificada na sala de reuniões 201 (Foto: Fios expostos)
5. **[ALOCADA]** #10 - Limpeza do filtro do ar-condicionado (Foto: Filtro sujo)
6. **[CONCLUIDA]** #11 - Maçaneta quebrada (Foto pós-conserto: Maçaneta nova)
7. **[CONCLUIDA]** #12 - Reparo do elevador social (Foto pós-conserto: Painel consertado)
8. **[FINALIZADA]** #13 - Substituição de forro (Foto pós-conserto: Forro novo branco)
9. **[ABERTA]** #14 - Pintura desgastada no hall (Foto gerada por script: Parede descascando)
10. **[FINALIZADA]** #15 - Troca de lâmpadas LED (Foto pós-conserto: Garagem bem iluminada)
11. **[ALOCADA]** #16 - Revisão do sistema hidráulico (Foto gerada por script: Canos e manômetro)
12. **[ABERTA]** #17 - Corrimão na rampa (Foto gerada por script: Rampa vazia)

> *Nota sobre imagens*: Como atingimos a cota da IA geradora, 9 imagens foram criadas nativamente e 3 foram geradas de forma procedimental utilizando a biblioteca `Pillow` do Python.

## ⚠️ 4. Débitos Técnicos e Bugs Descobertos (Ainda NÃO corrigidos)
Durante a inspeção sênior, identificamos itens importantes que o usuário precisa decidir quando corrigir:

**Bugs Críticos na Lógica**
1. **Edição Fake de Foto**: Na view de edição de tarefa, se o usuário fizer upload de uma nova foto, o código ignora silenciosamente. Não atualiza a evidência (porque `TaskForm` possui o campo foto que não pertence ao modelo `Task`).
2. **Bloqueio de Edição (Data)**: A função `clean_due_date` impede salvar edições de tarefas antigas/concluídas se a data de vencimento estiver no passado.
3. **Pulo de Status**: Uma tarefa "Aberta" pode ser "Concluída" diretamente pulando a etapa "Alocada".
4. **Conclusão sem foto**: É possível concluir tarefas preenchendo apenas um texto, o envio da foto não está sendo forçado na view.

**Segurança (Vulnerabilidades)**
1. Logout está sendo feito via método HTTP GET (Vulnerável a CSRF).
2. Marcação de Notificação como Lida está aceitando HTTP GET (Vulnerável a CSRF).
3. Na área de edição de Admin, dados como nome e email são salvos sem passar por higienização (`strip_tags`), permitindo injeção de HTML.

## 🚀 5. Próximos Passos Sugeridos
Se houver uma perda de contexto, o desenvolvedor deve focar em:
1. Arrumar a **Máquina de Estados** das tarefas (garantir que não pulem etapas).
2. Corrigir os bugs críticos nos forms/views mencionados na seção 4.
3. Fazer ajustes finos de layout.
