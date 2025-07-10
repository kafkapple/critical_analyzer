# src/main.py
import hydra
from omegaconf import DictConfig
import os
from tqdm import tqdm
from file_handler import FileHandler
from llm_adapter import LLMAdapter
import logging

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
    # Hydra's output directory is the current working directory
    output_dir = os.getcwd()
    final_report_path = os.path.join(output_dir, cfg.output_file)

    # Create a dedicated 'outputs/summaries' directory at the project root
    summaries_base_dir = get_full_path("outputs")
    individual_summaries_dir = os.path.join(summaries_base_dir, "summaries")
    os.makedirs(individual_summaries_dir, exist_ok=True)

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
    print("\n--- Generating Individual Summaries ---")
    for doc in tqdm(documents, desc="Summarizing documents"):
        tqdm.write(f"\nProcessing: {doc['filename']}")
        
        prompt = individual_prompt_template.format(document_content=doc['content'])
        summary_content = llm_adapter.generate(prompt)
        
        # Print a snippet of the summary
        summary_snippet = summary_content.strip().replace('\n', ' ')[0:200]
        tqdm.write(f"  └ Summary Snippet: {summary_snippet}...")

        # Save the individual summary to a file
        summary_filename = f"{os.path.splitext(doc['filename'])[0]}_summary.md"
        summary_filepath = os.path.join(individual_summaries_dir, summary_filename)
        
        with open(summary_filepath, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        summary_file_paths.append(summary_filepath)

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
