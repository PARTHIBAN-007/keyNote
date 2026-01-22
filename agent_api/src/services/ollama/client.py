import httpx
from typing import Any,Dict,List,Optional
from loguru import logger
import json
from src.config import Settings
from src.excetions import OllamaException,OllamaConnectionError,OllamaTimeoutError

class OllamClient:
    def __init__(self,settings:Settings):
        self.base_url = settings.ollama_host
        self.timeout = httpx.Timeout(float(settings.ollama_timeout))

    
    async def health_check(self)->Dict[str, Any]:
        """Check if ollama service is healthy and running"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/version")

                if response.status_code==200:
                    version_info = response.json()
                    return {
                        "status": "Healthy",
                        "message": "Ollama Service is running",
                        "version": version_info.get("version","unknown")
                    }
                
                else:
                    raise OllamaException(f"Ollama health check failed with status code {response.status_code}")
        except httpx.ConnectError as e:
            raise OllamaException(f"Failed to connect to ollama service: {str(e)}")
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(f"Ollama service timeout : {e}")
        except Exception as e:
            raise OllamaException(f"Ollama Health Check Failed: {str(e)}")
        

    async def list_models(self)-> List[Dict[str,Any]]:
        """Get the list of available models from ollama service"""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/tags")

                if response.status_code == 200:
                    data = response.json()
                    return data.get("models",[])
                else:
                    raise OllamaConnectionError(f"Failed to list models: {response.status_code}")
                
        except httpx.ConnectError as e:
            raise OllamaConnectionError(f"Failed to connect to ollama service: {str(e)}")
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(f"Ollama service timout : {e}")
        except Exception as e:
            raise OllamaException(f"Error listing models from ollama: {str(e)}")
        
    async def generate_text(self,model:str,prompt:str,stream:bool =False,**kwargs)-> Optional[Dict[str,Any]]:
        """ 
        Generate text from the model.
        Args:
            model (str): Model Name
            prompt (str): Input Prompt
            stream (bool): Whether to stream the response or not.
            **kwargs: Additional paramters for generation.
        """

        try:
            async with httpx.AsyncClient(timeout= self.timeout) as client:
                data = {
                    "model": model,
                    "prompt": prompt,
                    "stream": stream,
                    **kwargs
                }

                logger.info(f"Sending generation request to ollama: model = {model} , stream = {stream},  kwargs = {kwargs}")

                response = await client.post(f"{self.base_url}/api/generate",json=data)

                if response.status_code==200:
                    result = response.json()


                    usage_metadata = {}

                    if "prompt_eval_count" in result:
                        usage_metadata["prompt_token"] = result["prompt_eval_count"]
                    if "eval_count" in result:
                        usage_metadata["completion_token"] = result["eval_count"]

                    if usage_metadata:
                        usage_metadata["total_tokens"] = (
                            usage_metadata.get("prompt_token",0) + usage_metadata.get("completion_token",0)
                        )

                    
                    if "total_duration" in result:
                        usage_metadata["latency_ms"] = round(result["total_duration"]/1_000_000 ,2)

                    if "prompt_eval_duration" in result:
                        usage_metadata["prompt_eval_duration_ms"] = round(result["prompt_eval_duration"] / 1_000_000, 2)
                    if "eval_duration" in result:
                        usage_metadata["eval_duration_ms"] = round(result["eval_duration"] / 1_000_000, 2)
                    
                    result["usage_metadata"] = usage_metadata

                    logger.debug(f"usage Metadata: {usage_metadata}")

                    return result
                else:
                    raise OllamaException(f"Generation failed with status code {response.status_code}")
        except httpx.ConnectionError as e:
            raise OllamaConnectionError(f"Failed to connect to ollama service: {str(e)}")
        except httpx.TimeoutError as e:
            raise OllamaTimeoutError(f"Ollama service timeout : {e}")
        except Exception as e:  
            raise OllamaException(f"Error Generating text from ollama: {str(e)}")
        
    async def stream_generate_text(self,model:str,prompt:str,**kwargs):
        """
        Generate text with streaming response.

        Args:
            model: Model name to use
            prompt: Input prompt for generation
            **kwargs: Additional generation parameters

        Yields:
            JSON chunks from streaming response
        """

        try:
            async with httpx.AsyncClient(timeout = self.timeout) as client:
                data = {
                    "model": model,
                    "prompt": prompt,
                    "stream": True,
                    **kwargs
                }

                logger.info(f"Sending Streaming generation request to ollama model: {model}, kwargs: {kwargs}")

                async with client.stream("POST",f"{self.base_url}/api/generate",json=data) as response:
                    if response.status_code != 200:
                        raise OllamaException(f"Streaming generation failed with status code {response.status_code}")
                    
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                chunk = json.loads(line)
                                yield chunk
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to decode JSON chunk: {line}")
                                continue

        except httpx.ConnectError as e:
            raise OllamaConnectionError(f"Failed to connect to ollama service: {str(e)}")
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(f"Ollama service timeout: {e}")
        except Exception as e:
            raise OllamaException(f"Error in streaming generation from ollama: {str(e)}")
    


                

