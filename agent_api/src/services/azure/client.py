import os
import time
import requests
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from loguru import logger

class AzureTranscriptionClient:
    def __init__(self, speech_key, speech_region, storage_conn_str, container_name="audio-blob"):
        self.speech_key = speech_key
        self.speech_region = speech_region
        self.storage_conn_str = storage_conn_str
        self.container_name = container_name
        self.base_url = f"https://{speech_region}.api.cognitive.microsoft.com/speechtotext/v3.2"
        self.session = self._get_retry_session()

    def _get_retry_session(self):
        """Creates a requests session with automatic retry logic."""
        session = requests.Session()
        retry = Retry(
            total=5, 
            backoff_factor=2, 
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        return session

    def upload_file(self, file_obj, filename):
        """Uploads a file-like object to Azure Blob Storage."""
        try:
            logger.info(f"Streaming {filename} to Azure Blob Storage...")
            blob_service_client = BlobServiceClient.from_connection_string(self.storage_conn_str)
            blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=filename)
            
            file_obj.seek(0)
            blob_client.upload_blob(
                file_obj, 
                overwrite=True, 
                max_concurrency=4, 
                connection_timeout=600
            )
            logger.info(f"Upload complete: {filename}")
        except Exception as e:
            logger.error(f"Upload Failed: {str(e)}")
            raise e

    def _generate_sas_url(self, blob_name):
        blob_service_client = BlobServiceClient.from_connection_string(self.storage_conn_str)
        blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
        
        sas_token = generate_blob_sas(
            account_name=blob_service_client.account_name,
            account_key=blob_service_client.credential.account_key,
            container_name=self.container_name,
            blob_name=blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=2)
        )
        return f"{blob_client.url}?{sas_token}"

    def _delete_blob(self, blob_name):
        try:
            blob_service_client = BlobServiceClient.from_connection_string(self.storage_conn_str)
            blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
            blob_client.delete_blob()
            logger.info(f"Cleanup: Deleted blob {blob_name}")
        except Exception as e:
            logger.error(f"Cleanup Failed: {str(e)}")

    def run_transcription(self, blob_name):
        """Orchestrates the full transcription workflow."""
        try:
            # 1. Generate SAS
            file_url = self._generate_sas_url(blob_name)

            # 2. Submit Job (Configured for Universal Model + Code Switching)
            job_data = {
                "contentUrls": [file_url],
                "displayName": f"Batch_{blob_name}",
                "locale": "en-US", # Fallback default
                "properties": {
                    "wordLevelTimestampsEnabled": True,
                    "timeToLiveHours": 1,
                    # Universal Model Feature: Language Detection
                    "candidateLocales": ["en-US", "ta-IN"], 
                }
            }
            
            headers = {
                "Ocp-Apim-Subscription-Key": self.speech_key, 
                "Content-Type": "application/json"
            }

            logger.info(f"Submitting Universal Job for {blob_name}...")
            response = self.session.post(f"{self.base_url}/transcriptions", headers=headers, json=job_data)

            if response.status_code != 201:
                logger.error(f"FATAL: Job Submission Failed. {response.text}")
                return

            job_url = response.json()['self']
            job_id = job_url.split('/')[-1]
            logger.info(f"Job Created. ID: {job_id}. Polling...")

            # 3. Polling Loop
            while True:
                time.sleep(10)
                try:
                    status_res = self.session.get(job_url, headers=headers)
                    status_data = status_res.json()
                    status = status_data['status']
                    
                    logger.info(f"Job {job_id} Status: {status}")
                    
                    if status == "Succeeded":
                        self._process_results(status_data, headers, blob_name)
                        break
                    elif status == "Failed":
                        err = status_data.get('properties', {}).get('error', 'Unknown Error')
                        logger.error(f"Job {job_id} Failed: {err}")
                        break
                
                except requests.exceptions.ConnectionError:
                    logger.warning("Connection dropped. Reconnecting in 5s...")
                    time.sleep(5)
                    continue

            # 4. Cleanup
            self._delete_blob(blob_name)

        except Exception as e:
            logger.error(f"Workflow Error: {str(e)}", exc_info=True)

    def _process_results(self, status_data, headers, blob_name):
        try:
            files_url = status_data['links']['files']
            files_data = self.session.get(files_url, headers=headers).json()
            
            content_url = next(v['links']['contentUrl'] for v in files_data['values'] if v['kind'] == 'Transcription')
            result_data = self.session.get(content_url).json()

            full_text = ""
            if 'combinedRecognizedPhrases' in result_data and result_data['combinedRecognizedPhrases']:
                full_text = result_data['combinedRecognizedPhrases'][0]['display']
            elif 'combinedPhrases' in result_data and result_data['combinedPhrases']:
                full_text = result_data['combinedPhrases'][0]['text']
            elif 'phrases' in result_data:
                full_text = " ".join([p.get('display', p.get('text', '')) for p in result_data['phrases']])
            else:
                full_text = "[Error: No text found]"

            output_filename = f"{blob_name}.txt"
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(full_text)
            
            logger.info("--- TRANSCRIPTION COMPLETE ---")
            logger.info(f"Saved to: {os.path.abspath(output_filename)}")

        except Exception as e:
            logger.error(f"Result Processing Error: {str(e)}")