import os
import re
import json
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger


class ReActAgent:
    """
    A ReAct-style Agent that follows the Thought-Action-Observation loop.
    """

    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        """
        Returns the system prompt instructing the agent to follow the ReAct format.
        Includes available tools and format instructions.
        """
        tool_descriptions = "\n".join(
            [f"- {t['name']}: {t['description']}" for t in self.tools]
        )
        return f"""You are an intelligent assistant that solves problems step by step.
You have access to the following tools:
{tool_descriptions}

Always use this exact format:
Thought: <your reasoning about what to do next>
Action: <tool_name>(<arguments>)
Observation: <result of the tool call>
... (repeat Thought/Action/Observation as many times as needed)
Final Answer: <your final response to the user>

Rules:
- Only call ONE tool per Action step.
- Wait for the Observation before continuing.
- When you have enough information, write "Final Answer:" followed by your response.
- Do not fabricate Observations; they will be filled in for you.
"""

    def run(self, user_input: str) -> str:
        """
        Executes the ReAct loop:
        1. Generate Thought + Action via LLM.
        2. Parse the Action and execute the corresponding tool.
        3. Append the Observation to the conversation and repeat.
        4. Stop when a Final Answer is found or max_steps is reached.
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})

        # Build up a running transcript that grows with each step
        transcript = f"User: {user_input}\n"
        steps = 0
        final_answer = None

        while steps < self.max_steps:
            # --- 1. Generate the next LLM response ---
            result = self.llm.generate(transcript, system_prompt=self.get_system_prompt())

            response_content = result.get("content", "")
            logger.log_event("LLM_RESPONSE", {"step": steps, "response": result})

            # Append the model's output to the running transcript
            transcript += response_content

            # --- 2. Check for Final Answer first ---
            final_match = re.search(r"Final Answer:\s*(.+)", response_content, re.DOTALL)
            if final_match:
                final_answer = final_match.group(1).strip()
                logger.log_event("FINAL_ANSWER", {"answer": final_answer, "steps": steps})
                break

            # --- 3. Parse Action ---
            action_match = re.search(r"Action:\s*(\w+)\((.*?)\)", response_content, re.DOTALL)
            if action_match:
                tool_name = action_match.group(1).strip()
                tool_args = action_match.group(2).strip()

                logger.log_event("TOOL_CALL", {"tool": tool_name, "args": tool_args})

                # --- 4. Execute the tool ---
                observation = self._execute_tool(tool_name, tool_args)

                logger.log_event("TOOL_RESULT", {"tool": tool_name, "result": observation})

                # Append the Observation so the LLM sees it in the next iteration
                transcript += f"\nObservation: {observation}\n"
            else:
                # Model produced neither an Action nor a Final Answer — nudge it
                transcript += "\nObservation: (No action taken. Please continue with Thought/Action or provide a Final Answer.)\n"

            steps += 1

        logger.log_event("AGENT_END", {"steps": steps})

        if final_answer:
            return final_answer

        # Fallback: ask the LLM to summarise with what it has so far
        fallback_prompt = transcript + "\nFinal Answer:"
        fallback = self.llm.generate(fallback_prompt, system_prompt=self.get_system_prompt())
        return fallback.get("content", "").strip()

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Looks up a tool by name, parses JSON arguments, and calls its 'func'.

        Each tool dict is expected to have at least:
            {
                "name": str,
                "description": str,
                "func": Callable[[Dict[str, Any]], str]
            }
        """
        for tool in self.tools:
            if tool["name"] == tool_name:
                func = tool.get("func")
                if callable(func):
                    # --- CRITICAL UPGRADE: Parse the argument string as JSON ---
                    try:
                        # The LLM should provide a JSON string, e.g., '{"item_name": "iphone"}'
                        # Clean up common formatting issues from LLMs (quotes, markdown backticks)
                        clean_args = args.strip(" \n'\"`")
                        if clean_args.lower().startswith("json"):
                            clean_args = clean_args[4:].strip(" \n")
                            
                        tool_args_dict = json.loads(clean_args)
                        return str(func(tool_args_dict))
                    except json.JSONDecodeError:
                        error_msg = f"Error: Invalid JSON arguments provided for {tool_name}. Expected a valid JSON string. Received: {args}"
                        logger.log_event("TOOL_ERROR", {"tool": tool_name, "error": error_msg})
                        return error_msg
                    except Exception as exc:
                        logger.log_event(
                            "TOOL_ERROR", {"tool": tool_name, "args": args, "error": str(exc)}
                        )
                        return f"Error executing {tool_name}: {exc}"
                else:
                    return f"Tool '{tool_name}' has no callable 'func' defined."

        return f"Tool '{tool_name}' not found. Available tools: {[t['name'] for t in self.tools]}"