import itertools
import json
import logging

from openai import AsyncAzureOpenAI
from openai.types.chat.chat_completion import ChatCompletion

from .config import config
from .data_mcp_client import MCPClient
from .sys_prompt import SYSTEM_PROMPT
from .vector_retriever import VectorRetriever

logger = logging.getLogger(__name__)


class Bot:
    def __init__(
        self,
        mcp_client: MCPClient,
        gpt_client: AsyncAzureOpenAI,
        vector_retriever: VectorRetriever,
    ):
        self.mcp_client: MCPClient = mcp_client
        self.gpt_client: AsyncAzureOpenAI = gpt_client
        self.model_name: str = config.AZURE_OPENAI_API_DEPLOYMENT_NAME
        self.log_function_calling: bool = False
        self.tools: dict = {}
        self.msg_list: list = []
        self.session_memory: dict = {}
        self.vector_retriever: VectorRetriever = vector_retriever

    def load_conversations(self) -> None:
        for conv_file in config.CONV_DIR.glob("*.json"):
            try:
                with conv_file.open(encoding="utf-8") as f:
                    history = json.load(f)
                session_id = conv_file.stem
                self.session_memory[session_id] = [
                    {"role": msg["role"], "content": msg["content"].strip()}
                    for msg in history
                ]
            except Exception:
                logger.exception("Failed to load %s", conv_file.name)

    async def initialize(self) -> None:
        try:
            self.tools = await self.get_available_tools()
            self.msg_list = await self.prep_messages_with_system_prompt(self.tools)
        except Exception:
            logger.exception("couldnt load the tools")
            self.tools = {}
            self.msg_list = [{
                "role": "system",
                "content": SYSTEM_PROMPT.format(tools="there are no tools")
            }]

    async def chat_loop(self, query: str, tools: dict, messages: list[dict]) -> tuple[str, list]:
        messages.append({"role": "user", "content": query})
        first_response = await self.gpt_client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=([t["schema"] for t in tools.values()] if len(tools) > 0 else None),
        )
        if first_response.choices[0].message.tool_calls is not None:
            messages = await self.append_tool_call(first_response, messages)
            new_response = await self.gpt_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
            )
        elif first_response.choices[0].finish_reason == "stop":
            new_response = first_response
        else:
            msg = f"Unknown stop reason: {first_response.choices[0].finish_reason}"
            raise ValueError(msg)

        messages.append(
            {"role": "assistant", "content": new_response.choices[0].message.content},
        )

        return new_response.choices[0].message.content, messages

    async def append_tool_call(self, first_response: ChatCompletion, messages: list) -> list:
        for tool_call in first_response.choices[0].message.tool_calls:
            arguments = json.loads(tool_call.function.arguments) if isinstance(tool_call.function.arguments, str) else tool_call.function.arguments
            messages.append(
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": json.dumps(arguments),
                            },
                        },
                    ],
                },
            )
            tool_result = await self.mcp_client.call_tool(tool_call.function.name, **arguments)
            if self.log_function_calling:
                logger.info("------------------------------------------")
                logger.info("Calling Function: %s with args: %s", tool_call.function.name, arguments)
                logger.info("Function Result: %s", tool_result)
                logger.info("------------------------------------------")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": json.dumps(tool_result),
                },
            )
        return messages

    async def prep_messages_with_system_prompt(self, tools_dict: dict) -> list:
        return [
            {
                "role": "system",
                "content": SYSTEM_PROMPT.format(
                    tools="\n- ".join(
                        [f"{t['name']}: {t['schema']['function']['description']}" for t in tools_dict.values()],
                    ),
                ),
            },
        ]

    async def get_available_tools(self) -> dict:
        tools = await self.mcp_client.get_available_tools()
        return {
            tool.name: {
                "name": tool.name,
                "schema": {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                },
            }
            for tool in tools
        }

    async def run_query(self, query: str, session_id: str = "default") -> str:
        if session_id not in self.session_memory:
            self.session_memory[session_id] = []
        history = list(itertools.chain.from_iterable(self.session_memory.values()))
        context = await self.vector_retriever.get_combined_context(query, k=3, max_distance=0.4)
        prompt_with_context = f"{context}\n\n{query}"
        msg_list = [{"role": "system", "content": SYSTEM_PROMPT}, *history]
        msg_list.append({"role": "user", "content": prompt_with_context})
        response, updated_messages = await self.chat_loop(query, self.tools, msg_list)
        self.session_memory[session_id].append({"role": "user", "content": query})
        self.session_memory[session_id].append({"role": "assistant", "content": response})

        return response
