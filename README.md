# Sistema de Automação Blogger → LinkedIn

@CanalQb - Sistema automatizado para postar links do Blogger no LinkedIn diariamente.

## 📋 Visão Geral

Este sistema busca automaticamente posts do seu blog Blogger e os publica no LinkedIn, postando do mais antigo para o mais novo. Funciona via GitHub Actions com execução diária agendada.

## 🚀 Funcionalidades

- ✅ Busca posts do Blogger via API
- ✅ Posta automaticamente no LinkedIn
- ✅ Rastreia posts já publicados
- ✅ Execução diária automática (09:00 UTC)
- ✅ Suporte a execução manual
- ✅ Logs detalhados
- ✅ Credenciais seguras via GitHub Secrets

## 📁 Estrutura do Projeto

```
.
├── config.yml                          # Configuração do sistema
├── blogger_fetcher.py                 # Script para buscar posts do Blogger
├── linkedin_poster.py                 # Script para postar no LinkedIn
├── main.py                            # Script principal de integração
├── requirements.txt                   # Dependências Python
├── .github/
│   └── workflows/
│       └── blogger-to-linkedin.yml    # Workflow GitHub Actions
├── published_posts.json               # Rastreia posts publicados (gerado automaticamente)
└── automation.log                     # Logs de execução (gerado automaticamente)
```

## 🔧 Configuração

### 1. Configurar GitHub Secrets

No seu repositório GitHub, vá em **Settings** > **Secrets and variables** > **Actions** > **New repository secret** e adicione os seguintes secrets:

| Secret Name | Descrição | Como obter |
|-------------|-----------|------------|
| `BLOGGER_BLOG_ID` | ID do seu blog Blogger | URL do blog: `https://www.blogger.com/blogger.g?blogID=SEU_BLOG_ID` |
| `BLOGGER_API_KEY` | API Key do Google Blogger API | [Google Cloud Console](https://console.cloud.google.com/) > APIs & Services > Credentials |
| `LINKEDIN_CLIENT_ID` | Client ID do LinkedIn App | [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps) |
| `LINKEDIN_CLIENT_SECRET` | Client Secret do LinkedIn App | LinkedIn Developer Portal > Authentication |
| `LINKEDIN_REDIRECT_URI` | URL de redirecionamento OAuth | URL configurada no LinkedIn Developer Portal |
| `LINKEDIN_ACCESS_TOKEN` | Access Token do LinkedIn | Obtido via fluxo OAuth 2.0 |
| `LINKEDIN_REFRESH_TOKEN` | Refresh Token do LinkedIn | Obtido via fluxo OAuth 2.0 |

### 2. Obter Blogger Blog ID

1. Acesse seu blog no Blogger
2. Vá para **Configurações** > **Básico**
3. O Blog ID está na URL: `https://www.blogger.com/blogger.g?blogID=1234567890`

### 3. Obter Blogger API Key

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione existente
3. Vá para **APIs & Services** > **Library**
4. Busque por "Blogger API" e habilite
5. Vá para **APIs & Services** > **Credentials**
6. Clique em **Create Credentials** > **API Key**
7. Copie a API Key

### 4. Obter LinkedIn Credenciais

1. Acesse [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps)
2. Crie um novo aplicativo
3. Adicione produtos: "Sign In with LinkedIn using OpenID Connect" e "Share on LinkedIn"
4. Configure redirect URI
5. Copie Client ID e Client Secret
6. Execute fluxo OAuth 2.0 para obter Access Token e Refresh Token

## 📦 Instalação

### Localmente

```bash
# Clone o repositório
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO

# Instale dependências
pip install -r requirements.txt

# Configure o config.yml com suas credenciais
# (ou use variáveis de ambiente)

# Execute manualmente
python main.py
```

### GitHub Actions

1. Faça push do código para o GitHub
2. Configure os GitHub Secrets conforme acima
3. O workflow executará automaticamente às 09:00 UTC
4. Para execução manual, vá em **Actions** > **Blogger to LinkedIn Automation** > **Run workflow**

## ⚙️ Configuração Avançada

Edite `config.yml` para personalizar:

```yaml
posting:
  frequency: "daily"           # daily, weekly, monthly
  time: "09:00"                # Horário de postagem (UTC)
  timezone: "America/Sao_Paulo"  # Fuso horário
  max_posts_per_day: 1         # Máximo de posts por dia
  post_order: "oldest_first"    # oldest_first, newest_first
  skip_published: true         # Pular posts já publicados

post_template:
  headline: "🚀 Novo post no @CanalQb!"
  commentary: "Acabei de publicar um novo conteúdo sobre {title}. Confira agora!"
  hashtags: "#tecnologia #automacao #desenvolvimento #CanalQb"
  visibility: "PUBLIC"          # PUBLIC, CONNECTIONS
```

## 📊 Como Funciona

1. **Agendamento:** GitHub Actions executa diariamente às 09:00 UTC
2. **Busca:** Script busca posts do Blogger via API
3. **Seleção:** Seleciona o post mais antigo não publicado
4. **Formatação:** Aplica template de postagem
5. **Publicação:** Posta no LinkedIn via API
6. **Rastreamento:** Salva URL do post em `published_posts.json`
7. **Logs:** Registra tudo em `automation.log`

## 🔍 Troubleshooting

### Erro: "Access token expired"

O sistema tenta renovar automaticamente usando o refresh token. Se falhar:
1. Execute o fluxo OAuth 2.0 novamente
2. Atualize os secrets `LINKEDIN_ACCESS_TOKEN` e `LINKEDIN_REFRESH_TOKEN`

### Erro: "No posts to publish"

Todos os posts já foram publicados. Para resetar:
1. Delete o artifact `published-posts` no GitHub Actions
2. Ou edite manualmente `published_posts.json`

### Erro: "Blogger API quota exceeded"

A API do Blogger tem limites de quota. Aguarde o reset diário ou aumente a quota no Google Cloud Console.

## 📝 Logs

- **GitHub Actions:** Veja os logs na aba **Actions** do repositório
- **Arquivo local:** `automation.log` (se executado localmente)
- **Artifacts:** Logs são salvos como artifacts no GitHub Actions

## 🔒 Segurança

- ✅ Credenciais armazenadas em GitHub Secrets
- ✅ Nunca commitar credenciais no código
- ✅ Tokens expiram automaticamente
- ✅ Refresh token usado para renovação segura

## 📄 Licença

Este projeto é parte do ecossistema @CanalQb.

## 🤝 Suporte

Para suporte, visite [canalqb.com.br](https://canalqb.com.br) ou o canal [@CanalQb no YouTube](https://www.youtube.com/channel/UCdOA_1KzXHIp3gmVyyYv2sg).
