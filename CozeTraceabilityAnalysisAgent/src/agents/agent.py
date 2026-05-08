"""
无境深蓝海洋垃圾溯源侦探 Agent
专业的海洋垃圾图片分析与溯源分析专家
"""

import os
import json
from typing import Optional, Union, Dict, Any, List
from langchain.agents import create_agent
from langgraph.graph import MessagesState
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from coze_coding_dev_sdk import LLMClient
from coze_coding_utils.runtime_ctx.context import new_context, Context, default_headers
from storage.memory.memory_saver import get_memory_saver

LLM_CONFIG = "config/agent_llm_config.json"


class AgentState(MessagesState):
    """Agent 状态定义"""
    pass


# 全局 LLM 客户端和配置（延迟初始化）
_llm_client: Optional[LLMClient] = None
_llm_config: Optional[Dict[str, Any]] = None


def _get_llm_client(ctx: Optional[Context] = None) -> LLMClient:
    """获取或初始化 LLM 客户端"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient(ctx=ctx)
    return _llm_client


def _get_llm_config() -> Dict[str, Any]:
    """获取 LLM 配置"""
    global _llm_config
    if _llm_config is None:
        workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        config_path = os.path.join(workspace_path, LLM_CONFIG)
        with open(config_path, 'r', encoding='utf-8') as f:
            _llm_config = json.load(f)
    return _llm_config


def _extract_text_content(content: Union[str, List]) -> str:
    """安全提取文本内容，并清理 markdown 代码块"""
    text = ""
    if isinstance(content, str):
        text = content.strip()
    elif isinstance(content, list):
        if content and isinstance(content[0], str):
            text = " ".join(content).strip()
        else:
            text_parts = [
                item.get("text", "") 
                for item in content 
                if isinstance(item, dict) and item.get("type") == "text"
            ]
            text = " ".join(text_parts).strip()
    
    # 清理 markdown 代码块标记
    text = _clean_json_response(text)
    return text


def _clean_json_response(text: str) -> str:
    """
    清理模型返回的 JSON 响应，移除 markdown 代码块标记
    处理以下情况：
    - ```json\n{...}\n```
    - ```\n{...}\n```
    - 纯文本描述 + JSON 块
    """
    import re
    
    # 情况1: 完整的 markdown 代码块 ```json ... ```
    if '```' in text:
        # 匹配 ```json\n...\n``` 或 ```\n...\n```
        patterns = [
            r'```json\s*\n?(.*?)\n?```',
            r'```\s*\n?(.*?)\n?```',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()
    
    # 情况2: 文本描述 + JSON（取最后一个 { 到最后一个 } 之间的内容）
    json_start = text.rfind('{')
    json_end = text.rfind('}')
    if json_start != -1 and json_end != -1 and json_end > json_start:
        potential_json = text[json_start:json_end+1]
        # 验证是否是有效 JSON
        try:
            json.loads(potential_json)
            return potential_json
        except json.JSONDecodeError:
            pass
    
    return text


def analyze_marine_debris(
    image_url: str,
    additional_context: Optional[str] = None,
    ctx: Optional[Context] = None
) -> str:
    """
    分析海洋垃圾图片并返回溯源分析结果
    
    Args:
        image_url: 图片的公开访问链接
        additional_context: 额外的上下文信息（如拍摄地点、时间等）
        ctx: 请求上下文
    
    Returns:
        JSON 格式的分析结果字符串
    """
    if ctx is None:
        ctx = new_context(method="analyze_marine_debris")
    
    client = _get_llm_client(ctx)
    config = _get_llm_config()
    
    # 构建提示词
    prompt_text = "请分析这张海洋垃圾图片，按照系统提示词的要求输出JSON格式的分析结果。"
    if additional_context:
        prompt_text += f"\n\n额外信息：{additional_context}"
    
    # 构建多模态消息
    messages = [
        HumanMessage(content=[
            {
                "type": "text",
                "text": prompt_text
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            }
        ])
    ]
    
    # 调用模型
    response = client.invoke(
        messages=messages,
        model=config['config'].get("model", "doubao-seed-1-6-vision-250815"),
        temperature=config['config'].get("temperature", 0.3),
        top_p=config['config'].get("top_p", 0.9),
        max_completion_tokens=config['config'].get("max_completion_tokens", 10000),
    )
    
    return _extract_text_content(response.content)


def chat(
    user_message: str,
    image_url: Optional[str] = None,
    ctx: Optional[Context] = None
) -> str:
    """
    与 Agent 对话，支持图片输入
    
    Args:
        user_message: 用户消息
        image_url: 可选的图片URL
        ctx: 请求上下文
    
    Returns:
        Agent 回复
    """
    if ctx is None:
        ctx = new_context(method="chat")
    
    client = _get_llm_client(ctx)
    config = _get_llm_config()
    
    # 构建消息内容
    if image_url:
        content = [
            {
                "type": "text",
                "text": user_message
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            }
        ]
    else:
        content = user_message
    
    messages = [HumanMessage(content=content)]
    
    # 调用模型
    response = client.invoke(
        messages=messages,
        model=config['config'].get("model", "doubao-seed-1-6-vision-250815"),
        temperature=config['config'].get("temperature", 0.3),
        top_p=config['config'].get("top_p", 0.9),
        max_completion_tokens=config['config'].get("max_completion_tokens", 10000),
    )
    
    return _extract_text_content(response.content)


def build_agent(ctx: Optional[Context] = None):
    """
    构建 LangGraph Agent（用于复杂对话场景）
    
    Returns:
        配置好的 Agent 实例
    """
    config = _get_llm_config()
    
    # 创建一个简单的 ChatOpenAI 包装用于 create_agent
    # 注意：由于使用 coze-coding-dev-sdk，我们直接使用 chat 函数
    # 这里提供一个简化的 agent 构建方式
    
    from langchain_openai import ChatOpenAI
    from coze_coding_utils.runtime_ctx.context import default_headers
    
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
    
    llm = ChatOpenAI(
        model=config['config'].get("model", "doubao-seed-1-6-vision-250815"),
        api_key=api_key,
        base_url=base_url,
        temperature=config['config'].get('temperature', 0.3),
        streaming=True,
        timeout=config['config'].get('timeout', 600),
        extra_body={
            "thinking": {
                "type": config['config'].get('thinking', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}
    )
    
    return create_agent(
        model=llm,
        system_prompt=config.get("sp", ""),
        tools=[],
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )


def get_system_prompt() -> str:
    """获取系统提示词"""
    config = _get_llm_config()
    return config.get("sp", "")


def get_model_name() -> str:
    """获取当前使用的模型名称"""
    config = _get_llm_config()
    return config['config'].get("model", "doubao-seed-1-6-vision-250815")
