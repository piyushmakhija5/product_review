"""
Unified LLM client supporting both Claude and Gemini.
Provides a consistent interface for making LLM calls with thinking and tool use capabilities.
"""
from typing import Optional, List, Dict, Any, Union
import json
from config import Config


class LLMClient:
    """Unified client for Claude Sonnet 4.5 and Gemini 3."""

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize LLM client.

        Args:
            provider: 'claude' or 'gemini'. Defaults to Config.LLM_PROVIDER
            model: Model name. Defaults to Config.LLM_MODEL
        """
        self.provider = (provider or Config.LLM_PROVIDER).lower()
        self.model = model or Config.LLM_MODEL

        if self.provider == 'claude':
            self._init_claude()
        elif self.provider == 'gemini':
            self._init_gemini()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _init_claude(self):
        """Initialize Anthropic Claude client."""
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

    def _init_gemini(self):
        """Initialize Google Gemini client."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            self.client = genai.GenerativeModel(self.model)
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")

    def call(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        thinking: bool = False,
        json_mode: bool = False
    ) -> Union[str, Dict]:
        """
        Make a unified LLM call.

        Args:
            prompt: User prompt
            system: System prompt
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens in response
            thinking: Enable extended thinking mode
            json_mode: Expect JSON response

        Returns:
            String response or parsed JSON dict
        """
        if self.provider == 'claude':
            response = self._call_claude(
                prompt, system, temperature, max_tokens, thinking
            )
        else:
            response = self._call_gemini(
                prompt, system, temperature, max_tokens, thinking
            )

        # Parse JSON if requested
        if json_mode:
            return self._extract_json(response)

        return response

    def _call_claude(
        self,
        prompt: str,
        system: str,
        temperature: float,
        max_tokens: int,
        thinking: bool
    ) -> str:
        """Make a call to Claude API."""
        messages = [{"role": "user", "content": prompt}]

        params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }

        if system:
            params["system"] = system

        # Enable extended thinking for Claude
        if thinking:
            params["thinking"] = {
                "type": "enabled",
                "budget_tokens": 3000
            }

        try:
            response = self.client.messages.create(**params)
            return self._extract_claude_content(response)
        except Exception as e:
            raise RuntimeError(f"Claude API error: {str(e)}")

    def _call_gemini(
        self,
        prompt: str,
        system: str,
        temperature: float,
        max_tokens: int,
        thinking: bool
    ) -> str:
        """Make a call to Gemini API."""
        # Combine system and user prompt for Gemini
        full_prompt = f"{system}\n\n{prompt}" if system else prompt

        # Add thinking instruction if requested
        if thinking:
            full_prompt = f"{full_prompt}\n\nThink through this carefully step by step before responding."

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        try:
            response = self.client.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")

    def _extract_claude_content(self, response) -> str:
        """Extract text content from Claude response."""
        # Handle thinking blocks if present
        text_parts = []
        for block in response.content:
            # Skip thinking blocks - only get actual text responses
            if hasattr(block, 'type') and block.type == 'thinking':
                continue
            if hasattr(block, 'text'):
                text_parts.append(block.text)
        return "\n".join(text_parts)

    def _extract_json(self, response: str) -> Dict:
        """
        Extract and parse JSON from LLM response.
        Handles cases where JSON is wrapped in markdown code blocks or has preamble text.
        """
        text = response.strip()

        # Remove markdown code blocks if present
        if "```json" in text:
            # Extract content between ```json and ```
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end != -1:
                text = text[start:end].strip()
        elif text.startswith("```"):
            # Generic code block
            text = text[3:]
            if text.endswith("```"):
                text = text[:-3]

        text = text.strip()

        # Try to parse directly first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find JSON object in the text (in case of preamble)
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                json_str = text[start:end+1]
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # If all else fails, show what we got
        raise ValueError(
            f"Failed to parse JSON from LLM response.\n"
            f"Response preview: {text[:500]}\n"
            f"Full length: {len(text)} characters"
        )

    def structured_output(
        self,
        prompt: str,
        system: str = "",
        schema: Optional[Dict] = None,
        temperature: float = 0.7,
        thinking: bool = False
    ) -> Dict:
        """
        Get structured JSON output from LLM.

        Args:
            prompt: User prompt
            system: System prompt
            schema: Optional JSON schema to describe expected output
            temperature: Sampling temperature
            thinking: Enable extended thinking

        Returns:
            Parsed JSON dict
        """
        # Add JSON instruction to prompt
        json_instruction = "\n\nYou must respond with valid JSON only. Do not include any text outside the JSON object."

        if schema:
            json_instruction += f"\n\nExpected JSON schema:\n```json\n{json.dumps(schema, indent=2)}\n```"

        full_prompt = prompt + json_instruction

        return self.call(
            prompt=full_prompt,
            system=system,
            temperature=temperature,
            thinking=thinking,
            json_mode=True
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> str:
        """
        Multi-turn chat conversation.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: System prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Assistant's response
        """
        if self.provider == 'claude':
            return self._chat_claude(messages, system, temperature, max_tokens)
        else:
            return self._chat_gemini(messages, system, temperature, max_tokens)

    def _chat_claude(
        self,
        messages: List[Dict[str, str]],
        system: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Multi-turn chat with Claude."""
        params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }

        if system:
            params["system"] = system

        try:
            response = self.client.messages.create(**params)
            return self._extract_claude_content(response)
        except Exception as e:
            raise RuntimeError(f"Claude API error: {str(e)}")

    def _chat_gemini(
        self,
        messages: List[Dict[str, str]],
        system: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Multi-turn chat with Gemini."""
        # Convert messages to Gemini format
        history = []
        for msg in messages[:-1]:  # All but last
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [msg["content"]]})

        # Start chat with history
        chat = self.client.start_chat(history=history)

        # Add system prompt to first message if present
        last_message = messages[-1]["content"]
        if system and not history:
            last_message = f"{system}\n\n{last_message}"

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        try:
            response = chat.send_message(last_message, generation_config=generation_config)
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")


# Convenience function for quick calls
def quick_call(prompt: str, system: str = "", thinking: bool = False) -> str:
    """
    Quick LLM call using default configuration.

    Args:
        prompt: User prompt
        system: System prompt
        thinking: Enable extended thinking

    Returns:
        LLM response string
    """
    client = LLMClient()
    return client.call(prompt=prompt, system=system, thinking=thinking)
