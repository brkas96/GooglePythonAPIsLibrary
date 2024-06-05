from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import io
import os

API_CREDENTIAL = os.path.join('credentials.json')


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


'''Escreve em algum arquivo do Google Drive sem baixa-lo localmente, ou seja, diretamente no GD. O arquivo deve
ser um arquivo de texto.'''
def write_file(drive_service, file_id, new_content):
    media_body = MediaIoBaseUpload(io.BytesIO(new_content.encode('utf-8')), mimetype='text/plain', resumable=True)
    drive_service.files().update(
        fileId=file_id,
        media_body=media_body
    ).execute()

# Lê um arquivo de texto no Google Drive e retornar todas linhas
def read_file(drive_service, file_name):

    query = f"name = '{file_name}'"

    if drive_service is not None:
        # Procurar o arquivo com o nome específico
        results = drive_service.files().list(q=query).execute()
        files = results.get('files', [])

        if not files:
            print(f"File '{file_name}' not found.")
            return
        else:
            file_id = files[0]['id']
            request = drive_service.files().get_media(fileId=file_id)
            content = request.execute()

            lines = content.split(b'\n')
            return lines
    else:
        return


# Pesquisa um arquivo no GoogleDrive pelo nome
def search_file_by_name(service, file_name):
    # Procurar o arquivo com o nome específico
    query = f"name = '{file_name}'"
    results = service.files().list(q=query).execute()
    print(results)
    files = results.get('files', [])
    return files


'''Faz o upload de um arquivo. Caminho do arquivo especificado em file_path. ID da pasta presente no GoogleDrive
especificado em drive_folder_id.'''
def upload_selected_file(drive_service, file_path, drive_folder_id):
    try:
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [drive_folder_id],  # Adiciona o novo arquivo à pasta especificada
        }

        media = MediaFileUpload(file_path, mimetype='application/octet-stream', resumable=True)

        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        return f'Upload completo! Arquivo ID: {file["id"]}'

    except Exception as e:
        return f'Error {e}'

'''Pesquisa um arquivo no Google Drive pelo nome, e baixa ele na pasta raiz onde o script está sendo executado'''
def download_selected_file(drive_service, files):
    if files:
        for file in files:
            # Baixar o primeiro arquivo encontrado
            # file_id = file[0]['id']
            file_id = file['id']
            file_name = file['name']  # Obter o nome do arquivo

            try:
                request = drive_service.files().get_media(fileId=file_id)
            except Exception as e:
                print(f"Erro ao fazer solicitação a api do GoogleDrive: {e}")
            # Criar um objeto BytesIO para armazenar o conteúdo do arquivo
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            try:
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Download {int(status.progress() * 100)}%")

                # Salvar o conteúdo do arquivo no disco
                with open(file_name, 'wb') as arquivo:
                    arquivo.write(file_content.getvalue())

                print(f"File '{file}' has been successfully downloaded.")
                return True

            except Exception as e:
                print(f"Error ao baixar arquivo: {e}")
                return False