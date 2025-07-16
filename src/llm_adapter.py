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
        
        # Model context limits mapping
        self.model_context_limits = {
            'gpt-4': 8192,
            'gpt-4-0125-preview': 128000,
            'gpt-4-turbo-preview': 128000,
            'gpt-4o': 128000,
            'gpt-4o-mini': 128000,
            'gpt-3.5-turbo': 4096,
            'gpt-3.5-turbo-16k': 16384,
            'claude-3-opus-20240229': 200000,
            'claude-3-sonnet-20240229': 200000,
            'claude-3-haiku-20240307': 200000,
            'claude-3-5-sonnet-20241022': 200000,
            'gemini-pro': 32768,
            'gemini-1.5-pro': 1048576,
            'gemini-1.5-flash': 1048576,
        }
        
        # Calculate dynamic thresholds
        self.model_context_limit = self._get_model_context_limit()
        self.direct_integration_threshold = int(self.model_context_limit * 0.6)  # 60% for direct
        self.two_step_threshold = int(self.model_context_limit * 0.85)  # 85% for two-step

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

    def _get_model_context_limit(self) -> int:
        """Get context limit for current model"""
        for model_key in self.model_context_limits:
            if model_key in self.model_name:
                return self.model_context_limits[model_key]
        
        # Default fallback for unknown models
        logging.warning(f"Unknown model {self.model_name}, using default context limit of 8192")
        return 8192

    def count_tokens(self, text: str) -> int:
        try:
            return litellm.token_counter(model=self.model_name, messages=[{"role": "user", "content": text}])
        except Exception as e:
            logging.warning(f"Could not count tokens for model {self.model_name}: {e}")
            return -1 # Return -1 to indicate an error or inability to count
    
    def analyze_token_strategy(self, text: str) -> dict:
        """Analyze input and determine optimal processing strategy"""
        token_count = self.count_tokens(text)
        
        strategy_info = {
            'token_count': token_count,
            'model_context_limit': self.model_context_limit,
            'direct_threshold': self.direct_integration_threshold,
            'two_step_threshold': self.two_step_threshold,
            'strategy': 'unknown',
            'reason': '',
            'risk_level': 'low'
        }
        
        if token_count == -1:
            strategy_info.update({
                'strategy': 'two_step',
                'reason': 'Cannot count tokens - using safe two-step approach',
                'risk_level': 'high'
            })
        elif token_count <= self.direct_integration_threshold:
            strategy_info.update({
                'strategy': 'direct',
                'reason': f'Token count ({token_count}) is within direct integration threshold ({self.direct_integration_threshold})',
                'risk_level': 'low'
            })
        elif token_count <= self.two_step_threshold:
            strategy_info.update({
                'strategy': 'two_step',
                'reason': f'Token count ({token_count}) requires two-step processing (threshold: {self.two_step_threshold})',
                'risk_level': 'medium'
            })
        else:
            strategy_info.update({
                'strategy': 'chunk',
                'reason': f'Token count ({token_count}) exceeds two-step threshold - requires chunking',
                'risk_level': 'high'
            })
        
        return strategy_info
