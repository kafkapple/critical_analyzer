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
    # Initialize LLM adapter once
    llm_adapter = LLMAdapter(
        model_name=cfg.llm.model_name,
        temperature=cfg.llm.temperature,
        max_tokens=cfg.llm.max_tokens
    )

    # Load prompts
    individual_prompt_template = open(get_full_path(cfg.mode.individual_summary_prompt), 'r', encoding='utf-8').read()
    
    final_analysis_prompt_template = ""
    integration_analysis_prompt_template = ""
    integration_report_prompt_template = ""

    if cfg.mode.analysis_mode == "integration" and hasattr(cfg.mode, 'two_step_integration') and cfg.mode.two_step_integration:
        integration_analysis_prompt_template = open(get_full_path(cfg.mode.integration_analysis_prompt_path), 'r', encoding='utf-8').read()
        integration_report_prompt_template = open(get_full_path(cfg.mode.integration_report_prompt_path), 'r', encoding='utf-8').read()
    if cfg.mode.analysis_mode == "summary":
        report_type_suffix = "_summary"
        final_analysis_prompt_template = open(get_full_path(cfg.prompt.comprehensive_analysis_prompt), 'r', encoding='utf-8').read()
    elif cfg.mode.analysis_mode == "integration":
        report_type_suffix = "_integrated"
        final_analysis_prompt_template = open(get_full_path(cfg.mode.final_prompt_path), 'r', encoding='utf-8').read()
    else:
        raise ValueError("Invalid analysis_mode specified in config. Must be 'summary' or 'integration'.")

    # Process each input directory
    for input_dir_path in cfg.mode.input_dirs:
        input_dir = get_full_path(input_dir_path)
        print(f"\n--- Processing directory: {input_dir} ---")

        # Use the absolute path for the base output directory for this input_dir
        summaries_base_dir = os.path.join(input_dir, "outputs")
        os.makedirs(summaries_base_dir, exist_ok=True)

        individual_summaries_dir = os.path.join(summaries_base_dir, "summaries")
        os.makedirs(individual_summaries_dir, exist_ok=True)

        # Initialize file_handler for the current input_dir
        file_handler = FileHandler(input_dir)

        # Determine the final report path, adding a number if the file already exists
        today_str = datetime.now().strftime("%y%m%d")
        llm_name = cfg.llm.model_name.replace('/', '_')
        
        # Include input directory name in the report filename
        input_dir_name = os.path.basename(input_dir_path)
        base_report_filename = f"{today_str}_{llm_name}_{input_dir_name}{report_type_suffix}"
        report_counter = 1
        final_report_path = os.path.join(summaries_base_dir, f"{base_report_filename}_{report_counter}.md")
        while os.path.exists(final_report_path):
            report_counter += 1
            final_report_path = os.path.join(summaries_base_dir, f"{base_report_filename}_{report_counter}.md")

        # --- 2. Read Documents ---
        documents = file_handler.read_markdown_files()
        if not documents:
            print(f"No markdown files found in {input_dir}. Skipping.")
            continue

        print(f"Found {len(documents)} documents to analyze in {input_dir_name}.")

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

        # --- 4. Generate Final Analysis Report based on mode ---
        if cfg.mode.analysis_mode == "summary":
            print("\n--- Generating Comprehensive Summary Report ---")
            # Concatenate all individual summaries
            concatenated_input = ""
            for filepath in summary_file_paths:
                filename = os.path.basename(filepath).replace('_summary.md', '.md')
                with open(filepath, 'r', encoding='utf-8') as f:
                    summary_text = f.read()
                concatenated_input += f"--- DOCUMENT: {filename} ---\n\n{summary_text}\n\n"
            
            final_prompt = final_analysis_prompt_template.format(documents_concatenated=concatenated_input)
            final_report_content = ""
            with tqdm(total=1, desc="Creating final report") as pbar:
                final_report_content = llm_adapter.generate(final_prompt)
                pbar.update(1)

        elif cfg.mode.analysis_mode == "integration":
            print("\n--- Integrating and Optimizing Documents ---")
            # Concatenate all original documents for integration
            concatenated_original_documents = ""
            for doc in documents: # Use original documents, not summaries
                filename = os.path.basename(doc['filename'])
                concatenated_original_documents += f"--- DOCUMENT: {filename} ---\n\n{doc['content']}\n\n"

            # Smart token strategy analysis
            print("\n🔍 Analyzing content and determining optimal strategy...")
            strategy_info = llm_adapter.analyze_token_strategy(concatenated_original_documents)
            
            # Display strategy information
            print(f"📊 Token Analysis:")
            print(f"  ├─ Content tokens: {strategy_info['token_count']:,}")
            print(f"  ├─ Model context limit: {strategy_info['model_context_limit']:,}")
            print(f"  ├─ Direct integration threshold: {strategy_info['direct_threshold']:,}")
            print(f"  ├─ Two-step threshold: {strategy_info['two_step_threshold']:,}")
            print(f"  ├─ Recommended strategy: {strategy_info['strategy'].upper()}")
            print(f"  ├─ Risk level: {strategy_info['risk_level'].upper()}")
            print(f"  └─ Reason: {strategy_info['reason']}")
            
            # Log strategy information
            logging.info(f"Token strategy analysis: {strategy_info}")

            # Execute based on strategy
            if strategy_info['strategy'] == 'direct':
                print(f"\n⚡ Executing DIRECT integration (single-step)...")
                final_prompt = integration_analysis_prompt_template.format(documents_concatenated=concatenated_original_documents)
                final_report_content = ""
                with tqdm(total=1, desc="Direct integration") as pbar:
                    final_report_content = llm_adapter.generate(final_prompt)
                    pbar.update(1)
            
            elif strategy_info['strategy'] == 'two_step':
                print(f"\n🔄 Executing TWO-STEP integration...")
                
                if hasattr(cfg.mode, 'two_step_integration') and cfg.mode.two_step_integration:
                    print("--- Step 1: Generating Integration Analysis Summary ---")
                    analysis_prompt = integration_analysis_prompt_template.format(documents_concatenated=concatenated_original_documents)
                    integration_analysis_summary = ""
                    with tqdm(total=1, desc="Generating analysis summary") as pbar:
                        integration_analysis_summary = llm_adapter.generate(analysis_prompt)
                        pbar.update(1)
                    
                    print("--- Step 2: Generating Final Integration Report ---")
                    report_prompt = integration_report_prompt_template.format(integration_analysis_summary=integration_analysis_summary)
                    final_report_content = ""
                    with tqdm(total=1, desc="Creating final report") as pbar:
                        final_report_content = llm_adapter.generate(report_prompt)
                        pbar.update(1)
                else:
                    # Fallback to single-step if two_step_integration not configured
                    print("⚠️  Two-step integration not configured, falling back to single-step")
                    final_prompt = final_analysis_prompt_template.format(documents_concatenated=concatenated_original_documents)
                    final_report_content = ""
                    with tqdm(total=1, desc="Single-step fallback") as pbar:
                        final_report_content = llm_adapter.generate(final_prompt)
                        pbar.update(1)
            
            elif strategy_info['strategy'] == 'chunk':
                print(f"\n⚠️  CHUNKING strategy detected - content exceeds safe limits")
                print("📋 Consider:")
                print("  ├─ Breaking documents into smaller sections")
                print("  ├─ Using document summary mode instead")
                print("  └─ Processing documents in batches")
                
                # For now, attempt two-step with warning
                print("🔄 Attempting two-step integration with risk warning...")
                logging.warning("Content exceeds safe limits - attempting two-step integration")
                
                if hasattr(cfg.mode, 'two_step_integration') and cfg.mode.two_step_integration:
                    analysis_prompt = integration_analysis_prompt_template.format(documents_concatenated=concatenated_original_documents)
                    integration_analysis_summary = ""
                    with tqdm(total=1, desc="High-risk analysis") as pbar:
                        integration_analysis_summary = llm_adapter.generate(analysis_prompt)
                        pbar.update(1)
                    
                    report_prompt = integration_report_prompt_template.format(integration_analysis_summary=integration_analysis_summary)
                    final_report_content = ""
                    with tqdm(total=1, desc="High-risk integration") as pbar:
                        final_report_content = llm_adapter.generate(report_prompt)
                        pbar.update(1)
                else:
                    final_prompt = final_analysis_prompt_template.format(documents_concatenated=concatenated_original_documents)
                    final_report_content = ""
                    with tqdm(total=1, desc="High-risk single-step") as pbar:
                        final_report_content = llm_adapter.generate(final_prompt)
                        pbar.update(1)
            
            else:
                print(f"❌ Unknown strategy: {strategy_info['strategy']} - using fallback")
                final_prompt = final_analysis_prompt_template.format(documents_concatenated=concatenated_original_documents)
                final_report_content = ""
                with tqdm(total=1, desc="Fallback integration") as pbar:
                    final_report_content = llm_adapter.generate(final_prompt)
                    pbar.update(1)

        # --- 5. Write Final Report ---
        with open(final_report_path, 'w', encoding='utf-8') as f:
            f.write(final_report_content)

        print(f"\nAnalysis complete. Report saved to: {final_report_path}")

        # --- 6. Generate Feedback if path is provided ---
        if hasattr(cfg.mode, 'feedback_prompt_path') and cfg.mode.feedback_prompt_path:
            print(f"\n--- Generating Feedback for {os.path.basename(final_report_path)} ---")
            feedback_output_path = final_report_path.replace(".md", "_feedback.md")
            feedback_command = (
                f"python3 src/feedback_generator.py "
                f"--report_file \"{final_report_path}\" "
                f"--pi_info_file \"{get_full_path('data/target/lab.md')}\" "
                f"--feedback_prompt_file \"{get_full_path(cfg.mode.feedback_prompt_path)}\" "
                f"--output_file \"{feedback_output_path}\""
            )
            os.system(feedback_command)
            print(f"Feedback saved to: {feedback_output_path}")

if __name__ == "__main__":
    main()