import argparse
import os
from llm_adapter import LLMAdapter
import logging

def get_full_path(path: str) -> str:
    """Helper to get absolute path from the current working directory."""
    return os.path.abspath(path)

def main():
    parser = argparse.ArgumentParser(description="Generate PI feedback for a research report.")
    parser.add_argument("--report_file", type=str, required=True,
                        help="Absolute path to the comprehensive report file.")
    parser.add_argument("--pi_info_file", type=str, required=True,
                        help="Absolute path to the PI information file.")
    parser.add_argument("--feedback_prompt_file", type=str, required=True,
                        help="Absolute path to the feedback prompt file.")
    parser.add_argument("--output_file", type=str, required=True,
                        help="Absolute path to save the generated feedback report.")
    parser.add_argument("--model_name", type=str, default="perplexity/sonar-reasoning",
                        help="LLM model name to use for generation.")
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="Temperature for LLM generation.")
    parser.add_argument("--max_tokens", type=int, default=4000,
                        help="Maximum tokens for LLM generation.")

    args = parser.parse_args()

    # Suppress verbose logging from httpx and litellm
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)

    print(f"Generating PI feedback for: {args.report_file}")

    try:
        # Read contents
        with open(get_full_path(args.report_file), 'r', encoding='utf-8') as f:
            report_content = f.read()
        with open(get_full_path(args.pi_info_file), 'r', encoding='utf-8') as f:
            pi_info_content = f.read()
        with open(get_full_path(args.feedback_prompt_file), 'r', encoding='utf-8') as f:
            feedback_prompt_template = f.read()

        # Initialize LLM adapter
        llm_adapter = LLMAdapter(
            model_name=args.model_name,
            temperature=args.temperature,
            max_tokens=args.max_tokens
        )

        # Format the prompt
        # Assuming feedback_prompt_template has placeholders like:
        # **입력 1: 연구 계획서**
        # [여기에 검토할 연구 계획서 내용을 입력하세요]
        #
        # **입력 2: 연구실 정보**
        # [연구실명, PI 정보, 주요 연구 분야, 보유 장비/자원, 연구 철학 등을 입력하세요]
        formatted_prompt = feedback_prompt_template.replace(
            "[여기에 검토할 연구 계획서 내용을 입력하세요]", report_content
        ).replace(
            "[연구실명, PI 정보, 주요 연구 분야, 보유 장비/자원, 연구 철학 등을 입력하세요]", pi_info_content
        )

        # Generate feedback
        feedback_content = llm_adapter.generate(formatted_prompt)

        # Save feedback
        os.makedirs(os.path.dirname(get_full_path(args.output_file)), exist_ok=True)
        with open(get_full_path(args.output_file), 'w', encoding='utf-8') as f:
            f.write(feedback_content)

        print(f"PI feedback saved to: {args.output_file}")

    except FileNotFoundError as e:
        print(f"Error: One of the input files was not found. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
