import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import datetime
import base64
import ntpath


#SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.modify']

SCOPES = ["https://mail.google.com/"] # All permissions

CREDENTIALS_API_JSON = os.path.join('credentials.json')

USER_TOKEN_FILE = os.path.join('user_token.json')


# Retorna o objeto que permite o uso da API do Gmail
def create_gmail_service(creds):
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"Erro ao contruir GmailAPI service: {e}")
        return


# User auth via browser
def login_gmail_api():
    # credential.json é o arquivo da conta onde foi ativada a API do gmail
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_API_JSON, SCOPES)
    creds = flow.run_local_server(port=0)
    return creds


# Salva o token de usuario para que não seja necessário logar novamente via navegador
def save_token(creds):
    user_token = 'user_token.json'

    with open(user_token, 'w') as token_file:
        try:
            token_file.write(creds.to_json())
            print(f"Token criado com sucesso")
        except Exception as e:
            print(f"Erro ao salvar token de usuário: {e}")
    return user_token


# Após a autenticação do usuário, é possivel adquirir seu endereço de email, graças as permissões do SCOPES
def get_user_email(gmail_service):
    info_conta = gmail_service.users().getProfile(userId='me').execute()
    print(info_conta)
    email = info_conta.get('emailAddress')
    return email

# Refresh and validate token
def refresh_user_token(USER_TOKEN_FILE):
    creds = None

    # O arquivo token.json armazena as credenciais do usuário e é criado automaticamente após a primeira execução
    if os.path.exists(USER_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE)

    # Se não houver credenciais válidas disponíveis, solicita que o usuário faça login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print(f"Refresh user token")
                creds = creds.refresh(Request())
                if creds:
                    print(f"Token atualizado com sucesso ")
            except Exception as e:
                print(f"Erro ao dar Refresh no token: {e}")
    return creds


# Marca um email como lido
def mark_email_read(service, user_id, message_id):
    try:
        service.users().messages().modify(userId=user_id, id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()
        print("E-mail marcado como lido")
    except Exception as e:
        print(f"Erro ao marcar email como lido: {e}")


# Envia email utilizando a API do Gmail
def send_email_api(gmail_service, arquivo_anexo, destinatario):
    mensagem = MIMEMultipart(arquivo_anexo)
    mensagem['to'] = destinatario
    mensagem['subject'] = "This is a happy email :)"

    # Colocar o maximo de informações uteis que eu conseguir extrair do computador
    corpo_mensagem = MIMEText(f"Conjunto de prints: {datetime.now()}")
    mensagem.attach(corpo_mensagem)

    attachment_name = ntpath.basename(arquivo_anexo)

    # Anexo
    with open(arquivo_anexo, "rb") as anexo:
        conteudo_anexo = MIMEApplication(anexo.read(), _subtype="xz")
        anexo.close()
        conteudo_anexo.add_header('Content-Disposition', 'attachment', filename=attachment_name)
        mensagem.attach(conteudo_anexo)

    m = {'raw': base64.urlsafe_b64encode(mensagem.as_bytes()).decode()}

    try:
        resultado = gmail_service.users().messages().send(userId="me", body=m).execute()
        print(resultado)
        print(f'E-mail enviado com sucesso! Message Id: {resultado["id"]}')
        return True

    except Exception as e:
        print(f"Error to send e-mail: {e}")
        return


# Baixa um anexo
def download_attachments(service, user_id, message_id, diretorio):
    try:
        message = service.users().messages().get(userId=user_id, id=message_id).execute()

        for part in message['payload']['parts']:
            if 'filename' in part and part['filename']:
                nome_anexo = part['filename']
                print('nome_anexo: ', nome_anexo)

                # Obter os dados binários do anexo
                if 'body' in part and 'attachmentId' in part['body']:
                    attachment = service.users().messages().attachments().get(
                        userId=user_id,
                        messageId=message_id,
                        id=part['body']['attachmentId']
                    ).execute()

                    dados_base64 = attachment['data']
                    dados_bytes = base64.urlsafe_b64decode(dados_base64)

                    nome_anexo = os.path.basename(os.path.normpath(nome_anexo))

                    # Construir o caminho completo para salvar o anexo
                    full_path = os.path.join(diretorio, nome_anexo)
                    print(f'fullpath {full_path}')

                    # Decodificar e salvar o conteúdo do anexo
                    with open(full_path, 'wb') as arquivo:
                        arquivo.write(dados_bytes)
                        print(f"Δ Anexo '{nome_anexo}' baixado com sucesso.\n"
                              f"Δ Salvo em: {full_path}")

        return True

    except Exception as e:
        print(f"Error to download attachment {e}")
        return False




