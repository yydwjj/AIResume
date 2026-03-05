import json
from typing import Dict, List, Optional
from openai import OpenAI

from ..config.settings import config
from .helpers import LLMError


class LLMClient:
    def __init__(self):
        self._client = None
        self._model = None
        self._temperature = None
        self._max_tokens = None
        self._initialized = False
    
    def _ensure_initialized(self):
        if self._initialized:
            return
        
        deepseek_config = config.get_deepseek_config()
        
        self._client = OpenAI(
            api_key=deepseek_config.get('api_key', ''),
            base_url=deepseek_config.get('base_url', 'https://api.deepseek.com')
        )
        self._model = deepseek_config.get('model', 'deepseek-chat')
        self._temperature = deepseek_config.get('temperature', 0.1)
        self._max_tokens = deepseek_config.get('max_tokens', 4000)
        
        self._initialized = True
    
    @property
    def client(self):
        self._ensure_initialized()
        return self._client
    
    @property
    def model(self):
        self._ensure_initialized()
        return self._model
    
    @property
    def temperature(self):
        self._ensure_initialized()
        return self._temperature
    
    @property
    def max_tokens(self):
        self._ensure_initialized()
        return self._max_tokens
    
    def chat(
        self, 
        prompt: str, 
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        发送聊天请求
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature if temperature is not None else self.temperature,
                "max_tokens": max_tokens if max_tokens is not None else self.max_tokens,
            }
            
            if response_format:
                kwargs["response_format"] = response_format
            
            response = self.client.chat.completions.create(**kwargs)
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise LLMError(f"LLM调用失败: {str(e)}")
    
    def chat_with_system(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        发送带系统提示的聊天请求
        """
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature if temperature is not None else self.temperature,
                "max_tokens": max_tokens if max_tokens is not None else self.max_tokens,
            }
            
            response = self.client.chat.completions.create(**kwargs)
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise LLMError(f"LLM调用失败: {str(e)}")
    
    def extract_json(self, prompt: str) -> Dict:
        """
        发送请求并解析JSON响应
        """
        response = self.chat(prompt)
        
        try:
            json_str = response
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0]
            
            return json.loads(json_str.strip())
        except json.JSONDecodeError as e:
            raise LLMError(f"JSON解析失败: {str(e)}, 原始响应: {response}")
    
    def batch_chat(
        self, 
        prompts: List[str],
        temperature: Optional[float] = None
    ) -> List[str]:
        """
        批量发送聊天请求
        """
        results = []
        for prompt in prompts:
            result = self.chat(prompt, temperature=temperature)
            results.append(result)
        return results


llm_client = None

def get_llm_client() -> LLMClient:
    """
    获取LLM客户端单例
    """
    global llm_client
    if llm_client is None:
        llm_client = LLMClient()
    return llm_client
