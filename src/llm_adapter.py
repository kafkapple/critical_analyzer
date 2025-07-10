# src/llm_adapter.py
import litellm
from dotenv import load_dotenv
import os
import logging

class LLMAdapter:
    def __init__(self, model_name, temperature, max_tokens):
        load_dotenv()
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        # litellm automatically handles API keys from .env
        # (e.g., OPENAI_API_KEY, GEMINI_API_KEY)

    def generate(self, prompt: str) -> str:
        try:
            messages = [{"role": "user", "content": prompt}]
            response = litellm.completion(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            # Add robust checking for the response content
            if response and response.choices and response.choices[0].message and response.choices[0].message.content:
                return response.choices[0].message.content
            else:
                logging.error("LLM response was empty or invalid.")
                logging.error(f"Full response object: {response}")
                return "Error: LLM returned an empty or invalid response."

        except Exception as e:
            logging.error(f"An error occurred while calling the LLM: {e}", exc_info=True)
            return f"Error: Could not get a response from the model. Details: {e}"
