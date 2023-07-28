# pip install azure-storage-file-datalake azure-identity

import os
from azure.storage.filedatalake import (
    DataLakeServiceClient,
    DataLakeDirectoryClient,
    FileSystemClient
)
from azure.identity import DefaultAzureCredential

class Azure_Manipulation:

    def get_service_client_sas(self, sas_token: str, sas_url: str) -> DataLakeServiceClient:
        account_url = sas_url
        # The SAS token string can be passed in as credential param or appended to the account URL
        service_client = DataLakeServiceClient(account_url, credential=sas_token)

        return service_client
    
    def append_data_to_file(self, directory_client: DataLakeDirectoryClient, file_name: str):
        file_client = directory_client.get_file_client(file_name)
        file_size = file_client.get_file_properties().size
        
        data = b"Data to append to end of file"
        file_client.append_data(data, offset=file_size, length=len(data))

        file_client.flush_data(file_size + len(data))

    def list_directory_contents(self, file_system_client: FileSystemClient, directory_name: str):
        paths = file_system_client.get_paths(path=directory_name)

        for path in paths:
            print(path.name + '\n')

    def download_file_from_directory(self, directory_client: DataLakeDirectoryClient, local_path: str, file_name: str):
        file_client = directory_client.get_file_client(file_name)

        with open(file=os.path.join(local_path, file_name), mode="wb") as local_file:
            download = file_client.download_file()
            local_file.write(download.readall())
            local_file.close()

if __name__ == '__main__':
    # StoreAccount = "safactoreddatathon"
    SAS_Token = "sp=r&st=2023-07-21T22:27:46Z&se=2023-08-19T06:27:46Z&sv=2022-11-02&sr=c&sig=VF6y7LwGSmTHpKbOwGhy6DKUxn5HYZTK4wuvA22Q%2FWI%3D'"
    SAS_URL =   "https://safactoreddatathon.blob.core.windows.net/source-files?sp=r&st=2023-07-21T22:27:46Z&se=2023-08-19T06:27:46Z&sv=2022-11-02&sr=c&sig=VF6y7LwGSmTHpKbOwGhy6DKUxn5HYZTK4wuvA22Q%2FWI%3D"

    AM = Azure_Manipulation()

    AM.get_service_client_sas(SAS_Token,SAS_URL)
    # AM.list_directory_contents()



