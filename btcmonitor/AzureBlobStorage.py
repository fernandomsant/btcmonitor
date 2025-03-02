from azure.storage.blob import BlobServiceClient, BlobType
from azure.core.exceptions import AzureError, ResourceExistsError
import time

class AzureBlobStorage:
    def __init__(self, conn_str, container_name, blob_path):
        self.conn_str = conn_str
        self.container_name = container_name
        self.blob_path = blob_path
        self.is_connected = False
    
    def connect_to_storage(self, retries=5, delay=3):
        attempt = 0
        while attempt < retries:
            try:
                service_client = BlobServiceClient.from_connection_string(self.conn_str)
                try:
                    print('Criando container ...')
                    service_client.create_container(self.container_name)
                    print('Novo container criado.')
                except ResourceExistsError as e:
                    print('Container já existente ...')
                finally:
                    self.blob_client = service_client.get_blob_client(self.container_name, self.blob_path)
                    if self.blob_client.exists():
                        print('Blob já existente ...')
                        if self.blob_client.get_blob_properties().blob_type != BlobType.APPENDBLOB:
                            raise Exception('Blob existe, porém não é do tipo append. Altere o caminho do blob e reinicie o programa.')
                    else:
                        print('Criando blob ...')
                        self.blob_client.create_append_blob()
                        print('Novo blob criado.')
                self.is_connected = True
                return
            except ValueError as e:
                print(f"Erro de valor na string de conexão: {e}")
            except AzureError as e:
                print(f"Erro ao se conectar ao Azure Blob Storage: {e}")
            except Exception as e:
                print(f"Erro inesperado: {e}")
            attempt += 1
            if attempt < retries:
                print(f"Tentando novamente... ({attempt}/{retries})")
                time.sleep(delay)
        
    def push(self, data):
        try: 
            self.blob_client.append_block(data.encode('utf-8'))
        except Exception as e:
            print(f'Ocorreu um erro, tentando reconectar: {e}')
            self.connect_to_storage(retries=5, delay=3)