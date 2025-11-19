import os
import json
import requests
from typing import Dict, Any, Optional, List, Union

class BaseModel:
    """基础模型类，定义通用接口"""
    def __init__(self, model_name: str):
        self.model_name = model_name
    
    def chat(self, prompt: str) -> str:
        """聊天接口，返回模型回复"""
        raise NotImplementedError("子类必须实现此方法")

class OpenAIModel(BaseModel):
    """OpenAI API模型"""
    def __init__(self, model_name: str, api_key: str, api_base: Optional[str] = None):
        super().__init__(model_name)
        self.api_key = api_key
        self.api_base = api_base
        
        try:
            from openai import OpenAI
            if api_base:
                self.client = OpenAI(api_key=api_key, base_url=api_base)
            else:
                self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("请安装OpenAI Python包: pip install openai")
    
    def chat(self, prompt: str) -> str:
        """使用OpenAI API进行对话"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            return f"错误: {str(e)}"

class QwenModel(BaseModel):
    """阿里云通义千问API模型"""
    def __init__(self, model_name: str, api_key: str):
        super().__init__(model_name)
        self.api_key = api_key
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key, base_url=self.base_url)
        except ImportError:
            raise ImportError("请安装OpenAI Python包: pip install openai")
    
    def chat(self, prompt: str) -> str:
        """使用通义千问API进行对话"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"通义千问API调用失败: {e}")
            return f"错误: {str(e)}"

class BaiduModel(BaseModel):
    """百度文心一言API模型"""
    def __init__(self, model_name: str, api_key: str, secret_key: str):
        super().__init__(model_name)
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = self._get_access_token()
    
    def _get_access_token(self) -> str:
        """获取百度API访问令牌"""
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        response = requests.post(url, params=params)
        result = response.json()
        return result.get("access_token")
    
    def chat(self, prompt: str) -> str:
        """使用百度文心一言API进行对话"""
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{self.model_name}?access_token={self.access_token}"
        payload = json.dumps({
            "messages": [{"role": "user", "content": prompt}]
        })
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, headers=headers, data=payload)
            result = response.json()
            return result.get("result", "")
        except Exception as e:
            print(f"百度API调用失败: {e}")
            return f"错误: {str(e)}"

class LocalModel(BaseModel):
    """本地部署模型"""
    def __init__(self, model_name: str, api_url: str):
        super().__init__(model_name)
        self.api_url = api_url
    
    def chat(self, prompt: str) -> str:
        """调用本地API进行对话"""
        headers = {'Content-Type': 'application/json'}
        payload = json.dumps({
            "prompt": prompt,
            "max_tokens": 2048,
            "temperature": 0.7
        })
        
        try:
            response = requests.post(self.api_url, headers=headers, data=payload)
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            print(f"本地API调用失败: {e}")
            return f"错误: {str(e)}"

# 工厂函数，根据配置创建相应的模型实例
def create_model(config: Dict[str, Any]) -> BaseModel:
    """根据配置创建模型实例"""
    model_type = config.get("type", "").lower()
    
    if model_type == "openai":
        return OpenAIModel(
            model_name=config.get("model_name", "gpt-3.5-turbo"),
            api_key=config.get("api_key", ""),
            api_base=config.get("api_base")
        )
    elif model_type == "qwen":
        return QwenModel(
            model_name=config.get("model_name", "qwen-max"),
            api_key=config.get("api_key", "")
        )
    elif model_type == "baidu":
        return BaiduModel(
            model_name=config.get("model_name", "ernie-bot-4"),
            api_key=config.get("api_key", ""),
            secret_key=config.get("secret_key", "")
        )
    elif model_type == "local":
        return LocalModel(
            model_name=config.get("model_name", "local-model"),
            api_url=config.get("api_url", "http://localhost:8000/v1/chat/completions")
        )
    else:
        raise ValueError(f"不支持的模型类型: {model_type}")