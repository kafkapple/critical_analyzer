# src/main.py
import hydra
from omegaconf import DictConfig
import os
from tqdm import tqdm
from file_handler import FileHandler
from llm_adapter import LLMAdapter
import logging
from datetime import datetime

def get_full_path(path: str) -> str:
    """Helper to get absolute path from hydra's original cwd."""
    return os.path.join(hydra.utils.get_original_cwd(), path)

@hydra.main(config_path="../configs", config_name="config", version_base=None)
def main(cfg: DictConfig) -> None:
    # Suppress verbose logging from httpx and litellm
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)

    print("Starting the analysis process...")
    
    # --- 1. Setup ---
    input_dir = get_full_path(cfg.input_dir)
    # Use the absolute path for the base output directory
    summaries_base_dir = cfg.base_output_dir
    os.makedirs(summaries_base_dir, exist_ok=True)

    individual_summaries_dir = os.path.join(summaries_base_dir, cfg.summaries_sub_dir)
    os.makedirs(individual_summaries_dir, exist_ok=True)

    # Hydra's output directory is the current working directory
    output_dir = os.getcwd()
    # Determine the final report path, adding a number if the file already exists
    today_str = datetime.now().strftime("%y%m%d")
    llm_name = cfg.llm.model_name.replace('/', '_')
    prompt_name = os.path.splitext(os.path.basename(cfg.prompt.comprehensive_analysis_prompt))[0]
    
    base_report_filename = f"{today_str}_{llm_name}_{prompt_name}"
    report_counter = 1
    final_report_path = os.path.join(summaries_base_dir, f"{base_report_filename}_{report_counter}.md")
    while os.path.exists(final_report_path):
        report_counter += 1
        final_report_path = os.path.join(summaries_base_dir, f"{base_report_filename}_{report_counter}.md")

    # Load prompts
    individual_prompt_template = open(get_full_path(cfg.prompt.individual_summary_prompt), 'r', encoding='utf-8').read()
    comprehensive_prompt_template = open(get_full_path(cfg.prompt.comprehensive_analysis_prompt), 'r', encoding='utf-8').read()

    # Initialize components
    file_handler = FileHandler(input_dir)
    llm_adapter = LLMAdapter(
        model_name=cfg.llm.model_name,
        temperature=cfg.llm.temperature,
        max_tokens=cfg.llm.max_tokens
    )

    # --- 2. Read Documents ---
    documents = file_handler.read_markdown_files()
    if not documents:
        print(f"No markdown files found in {input_dir}. Exiting.")
        return

    print(f"Found {len(documents)} documents to analyze.")

    # --- 3. Generate and Save Individual Summaries ---
    summary_file_paths = []
    documents_to_summarize = []

    print("\n--- Checking for Existing Summaries ---")
    for doc in documents:
        base_filename = os.path.basename(doc['filename'])
        summary_filename = f"{os.path.splitext(base_filename)[0]}_summary.md"
        summary_filepath = os.path.join(individual_summaries_dir, summary_filename)

        if os.path.exists(summary_filepath):
            print(f"  └ Existing summary found for {doc['filename']}. Reusing it.")
            summary_file_paths.append(summary_filepath)
        else:
            documents_to_summarize.append(doc)

    if documents_to_summarize:
        print("\n--- Generating New Individual Summaries ---")
        for doc in tqdm(documents_to_summarize, desc="Summarizing new documents"):
            tqdm.write(f"\nProcessing: {doc['filename']}")
            
            base_filename = os.path.basename(doc['filename'])
            summary_filename = f"{os.path.splitext(base_filename)[0]}_summary.md"
            summary_filepath = os.path.join(individual_summaries_dir, summary_filename)

            prompt = individual_prompt_template.format(document_content=doc['content'])
            summary_content = llm_adapter.generate(prompt)
            
            with open(summary_filepath, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            
            summary_snippet = summary_content.strip().replace('\n', ' ')[0:200]
            tqdm.write(f"  └ Summary Snippet: {summary_snippet}...")

            summary_file_paths.append(summary_filepath)
    else:
        print("\n--- No new documents to summarize. ---")

    # --- 4. Generate Comprehensive Analysis from Summaries ---
    print("\n--- Generating Comprehensive Analysis Report ---")
    
    # Concatenate all individual summaries
    concatenated_summaries = ""
    for filepath in summary_file_paths:
        filename = os.path.basename(filepath).replace('_summary.md', '.md')
        with open(filepath, 'r', encoding='utf-8') as f:
            summary_text = f.read()
        concatenated_summaries += f"--- DOCUMENT: {filename} ---\n\n{summary_text}\n\n"

    comprehensive_prompt = comprehensive_prompt_template.format(documents_concatenated=concatenated_summaries)
    
    final_report_content = ""
    with tqdm(total=1, desc="Creating final report") as pbar:
        final_report_content = llm_adapter.generate(comprehensive_prompt)
        pbar.update(1)

    # --- 5. Write Final Report ---
    with open(final_report_path, 'w', encoding='utf-8') as f:
        f.write(final_report_content)

    print(f"\nAnalysis complete. Report saved to: {final_report_path}")

if __name__ == "__main__":
    main()
