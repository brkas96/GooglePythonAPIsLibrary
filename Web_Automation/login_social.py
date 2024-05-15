import webbrowser

# URL para autenticação OAuth do Google
google_oauth_url = "https://accounts.google.com/o/oauth2/auth"

# Parâmetros da autenticação OAuth
params = {
    "client_id": "SEU_CLIENT_ID",
    "redirect_uri": "http://localhost",
    "scope": "openid email profile",
    "response_type": "code",
}

# Construir a URL de autenticação
auth_url = f"{google_oauth_url}?client_id={params['client_id']}&redirect_uri={params['redirect_uri']}&scope={params['scope']}&response_type={params['response_type']}"

# Abrir o navegador para a página de autenticação
webbrowser.open(auth_url)
