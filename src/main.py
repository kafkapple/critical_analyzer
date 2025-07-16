# src/main.py
import hydra
from omegaconf import DictConfig
import os
import subprocess
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

    # Load prompts (only for summary and integration modes)
    individual_prompt_template = ""
    if cfg.mode.analysis_mode in ["summary", "integration"] and hasattr(cfg.mode, 'individual_summary_prompt'):
        individual_prompt_template = open(get_full_path(cfg.mode.individual_summary_prompt), 'r', encoding='utf-8').read()
    
    final_analysis_prompt_template = ""
    integration_analysis_prompt_template = ""
    integration_report_prompt_template = ""

    if cfg.mode.analysis_mode == "integration" and hasattr(cfg.mode, 'two_step_integration') and cfg.mode.two_step_integration:
        integration_analysis_prompt_template = open(get_full_path(cfg.mode.integration_analysis_prompt_path), 'r', encoding='utf-8').read()
        integration_report_prompt_template = open(get_full_path(cfg.mode.integration_report_prompt_path), 'r', encoding='utf-8').read()
    if cfg.mode.analysis_mode == "summary":
        report_type_suffix = "_summary"
        final_analysis_prompt_template = open(get_full_path(cfg.mode.final_prompt_path), 'r', encoding='utf-8').read()
    elif cfg.mode.analysis_mode == "integration":
        report_type_suffix = "_integrated"
        final_analysis_prompt_template = open(get_full_path(cfg.mode.final_prompt_path), 'r', encoding='utf-8').read()
    elif cfg.mode.analysis_mode == "report":
        report_type_suffix = "_report"
        # Report 모드는 개별 프롬프트 템플릿을 사용
        student_prompt_template = open(get_full_path(cfg.mode.student_prompt_path), 'r', encoding='utf-8').read()
        teacher_prompt_template = open(get_full_path(cfg.mode.teacher_prompt_path), 'r', encoding='utf-8').read()
    else:
        raise ValueError("Invalid analysis_mode specified in config. Must be 'summary', 'integration', or 'report'.")

    # --- Report 모드 처리 ---
    if cfg.mode.analysis_mode == "report":
        print("\n--- Processing Report Mode ---")
        
        # Report 모드 전용 처리 로직
        import re
        import glob
        
        # 각 입력 디렉토리 처리
        for input_dir_path in cfg.mode.input_dirs:
            input_dir = get_full_path(input_dir_path)
            print(f"\n--- Processing directory: {input_dir} ---")
            
            # 폴더 패턴에 맞는 하위 폴더 찾기
            folder_pattern = re.compile(cfg.mode.file_patterns.folder_pattern)
            
            for folder_name in os.listdir(input_dir):
                folder_path = os.path.join(input_dir, folder_name)
                if not os.path.isdir(folder_path):
                    continue
                    
                # 폴더명 패턴 매칭
                match = folder_pattern.match(folder_name)
                if not match:
                    continue
                    
                student_name = match.group(1)  # 이름 부분
                student_id = match.group(2)    # 8자리 ID
                
                print(f"Processing: {student_name} (ID: {student_id})")
                
                # chats_*.txt 파일 찾기
                chat_files = glob.glob(os.path.join(folder_path, cfg.mode.file_patterns.chat_file_pattern))
                
                if not chat_files:
                    print(f"  No chat files found in {folder_path}")
                    continue
                
                # 모든 chat 파일 내용 연결
                concatenated_content = ""
                for chat_file in sorted(chat_files):
                    with open(chat_file, 'r', encoding='utf-8') as f:
                        concatenated_content += f.read() + "\n\n"
                
                # 학생용 및 교사용 리포트 생성
                for report_type in cfg.mode.report_types:
                    print(f"  Generating {report_type} report...")
                    
                    # 프롬프트 선택
                    if report_type == "student":
                        prompt_template = student_prompt_template
                    elif report_type == "teacher":
                        prompt_template = teacher_prompt_template
                    else:
                        continue
                    
                    # 프롬프트에 대화 내용 삽입
                    final_prompt = prompt_template.format(query=concatenated_content)
                    
                    # LLM 호출
                    with tqdm(total=1, desc=f"Generating {report_type} report") as pbar:
                        report_content = llm_adapter.generate(final_prompt)
                        pbar.update(1)
                    
                    # 출력 디렉토리 생성
                    output_dir = os.path.join(get_full_path(cfg.mode.output_base_dir), report_type)
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # 파일 저장 (MD)
                    output_filename = f"{student_name}.md"
                    output_path = os.path.join(output_dir, output_filename)
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(report_content)
                    
                    print(f"  {report_type.title()} report saved to: {output_path}")
                    
                    # PDF 출력 (설정에서 활성화된 경우)
                    if hasattr(cfg.mode, 'output_formats') and 'pdf' in cfg.mode.output_formats:
                        try:
                            from pdf_generator import markdown_to_pdf
                            pdf_output_path = output_path.replace('.md', '.pdf')
                            pdf_result = markdown_to_pdf(output_path, pdf_output_path)
                            if pdf_result:
                                print(f"  {report_type.title()} PDF saved to: {pdf_output_path}")
                        except Exception as e:
                            print(f"  ⚠️ PDF 생성 실패: {e}")
                
                print(f"  Completed processing: {student_name}")

        print("\n--- Report Mode Processing Complete ---")
        return  # Exit early for report mode

    # Process each input directory (for summary and integration modes)
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
            
            try:
                result = subprocess.run(feedback_command, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"Feedback generated successfully: {feedback_output_path}")
                else:
                    print(f"Error generating feedback: {result.stderr}")
            except Exception as e:
                print(f"Error running feedback generator: {e}")


if __name__ == "__main__":
    main()