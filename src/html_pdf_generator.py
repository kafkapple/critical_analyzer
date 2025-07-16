#!/usr/bin/env python3
"""
HTML 기반 PDF 생성 도구 - Markdown을 HTML로 변환 후 PDF 생성
"""

import os
from pathlib import Path
import argparse

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

try:
    import pdfkit
    PDFKIT_AVAILABLE = True
except ImportError:
    PDFKIT_AVAILABLE = False

def markdown_to_html_pdf(markdown_file: str, output_file: str = None) -> str:
    """
    Markdown 파일을 HTML을 거쳐 PDF로 변환
    
    Args:
        markdown_file: 입력 Markdown 파일 경로
        output_file: 출력 PDF 파일 경로 (생략시 자동 생성)
    
    Returns:
        생성된 PDF 파일 경로
    """
    if not MARKDOWN_AVAILABLE or not PDFKIT_AVAILABLE:
        print("❌ 필요한 패키지가 설치되지 않았습니다.")
        print("설치 방법: pip install markdown pdfkit")
        print("wkhtmltopdf도 설치해야 합니다: sudo apt-get install wkhtmltopdf")
        return None
    
    try:
        # 출력 파일명 생성
        if output_file is None:
            output_file = markdown_file.replace('.md', '.pdf')
        
        # Markdown 파일 읽기
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Markdown을 HTML로 변환
        html_content = markdown.markdown(
            markdown_content,
            extensions=['extra', 'codehilite', 'toc']
        )
        
        # HTML 템플릿 적용
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Report</title>
            <style>
                body {{
                    font-family: "Noto Sans", Arial, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1, h2, h3 {{ color: #333; }}
                h1 {{ border-bottom: 2px solid #333; }}
                h2 {{ border-bottom: 1px solid #ccc; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
                pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 3px; overflow-x: auto; }}
                .emoji {{ font-size: 1.2em; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # HTML을 PDF로 변환
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }
        
        pdfkit.from_string(html_template, output_file, options=options)
        print(f"✅ PDF 생성 완료: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"❌ PDF 생성 실패: {e}")
        return None

def simple_markdown_to_html(markdown_file: str, output_file: str = None) -> str:
    """
    간단한 Markdown to HTML 변환 (PDF 생성 패키지 없이)
    """
    try:
        if output_file is None:
            output_file = markdown_file.replace('.md', '.html')
        
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 개선된 마크다운 변환
        lines = content.split('\n')
        html_lines = []
        
        for line in lines:
            # 제목 변환
            if line.startswith('### '):
                html_lines.append(f'<h3>{line[4:]}</h3>')
            elif line.startswith('## '):
                html_lines.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('# '):
                html_lines.append(f'<h1>{line[2:]}</h1>')
            # 리스트 변환
            elif line.startswith('- '):
                html_lines.append(f'<li>{line[2:]}</li>')
            elif line.startswith('  - '):
                html_lines.append(f'<ul><li>{line[4:]}</li></ul>')
            # 굵은 글씨 변환
            elif '**' in line:
                line = line.replace('**', '<strong>').replace('**', '</strong>')
                html_lines.append(f'<p>{line}</p>')
            # 빈 줄
            elif line.strip() == '':
                html_lines.append('<br>')
            # 일반 텍스트
            else:
                html_lines.append(f'<p>{line}</p>')
        
        html_content = '\n'.join(html_lines)
        
        # 잘못된 태그 수정
        html_content = html_content.replace('<strong><strong>', '<strong>').replace('</strong></strong>', '</strong>')
        
        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>학습 분석 리포트</title>
    <style>
        body {{ 
            font-family: "Noto Sans", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
            margin: 30px;
            line-height: 1.8;
            color: #333;
        }}
        h1 {{ 
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{ 
            color: #27ae60;
            border-bottom: 2px solid #27ae60;
            padding-bottom: 5px;
        }}
        h3 {{ 
            color: #e74c3c;
            margin-top: 25px;
        }}
        p {{ 
            margin: 8px 0;
            text-align: justify;
        }}
        li {{ 
            margin: 5px 0;
            list-style-type: disc;
            margin-left: 20px;
        }}
        ul {{ 
            margin: 10px 0;
        }}
        strong {{ 
            color: #2c3e50;
            font-weight: bold;
        }}
        .print-friendly {{ 
            max-width: 800px;
            margin: 0 auto;
        }}
        @media print {{
            body {{ font-size: 12pt; }}
            h1 {{ font-size: 18pt; }}
            h2 {{ font-size: 16pt; }}
            h3 {{ font-size: 14pt; }}
        }}
    </style>
</head>
<body>
    <div class="print-friendly">
        {html_content}
    </div>
</body>
</html>"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        print(f"✅ HTML 생성 완료: {output_file}")
        print("브라우저에서 열어 인쇄 → PDF로 저장하세요.")
        return output_file
        
    except Exception as e:
        print(f"❌ HTML 생성 실패: {e}")
        return None

def batch_convert_to_html(input_dir: str, output_dir: str = None):
    """
    디렉토리 내 모든 Markdown 파일을 HTML로 변환
    """
    input_path = Path(input_dir)
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = input_path
    
    md_files = list(input_path.glob('*.md'))
    
    if not md_files:
        print(f"❌ {input_dir}에 Markdown 파일이 없습니다.")
        return
    
    print(f"📄 {len(md_files)}개의 Markdown 파일을 HTML로 변환합니다...")
    
    success_count = 0
    for md_file in md_files:
        output_file = output_path / (md_file.stem + '.html')
        result = simple_markdown_to_html(str(md_file), str(output_file))
        if result:
            success_count += 1
    
    print(f"✅ 완료: {success_count}/{len(md_files)} 파일 변환 성공")

def main():
    parser = argparse.ArgumentParser(description='Markdown to HTML/PDF converter')
    parser.add_argument('input', help='Input markdown file or directory')
    parser.add_argument('-o', '--output', help='Output file or directory')
    parser.add_argument('--batch', action='store_true', help='Batch convert all MD files in directory')
    parser.add_argument('--html-only', action='store_true', help='Convert to HTML only (no PDF)')
    
    args = parser.parse_args()
    
    if args.batch:
        batch_convert_to_html(args.input, args.output)
    else:
        if os.path.isfile(args.input):
            if args.html_only:
                simple_markdown_to_html(args.input, args.output)
            else:
                markdown_to_html_pdf(args.input, args.output)
        else:
            print(f"❌ 파일을 찾을 수 없습니다: {args.input}")

if __name__ == '__main__':
    main()