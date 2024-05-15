from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import io
import os


API_CREDENTIAL = os.path.join('')

# Verifica um token de usuário autenticado, se o token não for mais válido, solicita login novamente para que seja
# gerado um novo token
def verificar_token(token_path):

    try:
        creds = None
        # O arquivo token.json armazena as credenciais do usuário e é criado automaticamente após a primeira execução
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path)

        # Se não houver credenciais válidas disponíveis, deixe o usuário fazer login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print(f"Atualizando token {token_path}")
                creds.refresh(Request())
        return creds
    except Exception as e:
        print(f"Não foi possivel renovar o token: {token_path}, Error: {e}")
        print(f"Requisitando novo token para: {token_path}")
        return None


# Constroi a API do Google Drive
def building_gdrive_api(creds):
    try:
        # Construir e retornar o serviço Google Drive API
        drive_service = build("drive", "v3", credentials=creds, static_discovery=False)
    except Exception as e:
        print(f"Error to build google drive api: {e}")
    return drive_service

# Escreve em algum arquivo do Google Drive sem baixa-lo localmente, ou seja, diretamente no GD
def write_file(drive_service, file_id, new_content):
    media_body = MediaIoBaseUpload(io.BytesIO(new_content.encode('utf-8')), mimetype='text/plain', resumable=True)
    drive_service.files().update(
        fileId=file_id,
        media_body=media_body
    ).execute()

# Encontrar o arquivo usando o nome para pesquisar no Google Drive
def search_file_by_name(service, file_name):
    # Procurar o arquivo com o nome específico
    query = f"name = '{file_name}'"
    results = service.files().list(q=query).execute()
    files = results.get('files', [])
    return files