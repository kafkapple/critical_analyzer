#!/usr/bin/env python3
"""
개선된 HTML 변환기 - 정확한 Markdown to HTML 변환
"""

import os
import re
from pathlib import Path
import argparse

def convert_markdown_to_html(markdown_content: str) -> str:
    """
    Markdown 내용을 HTML로 변환
    """
    lines = markdown_content.split('\n')
    html_lines = []
    in_list = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # 빈 줄 처리
        if not stripped:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append('<br>')
            continue
        
        # 제목 처리
        if line.startswith('### '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<h3>{line[4:].strip()}</h3>')
        elif line.startswith('## '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<h2>{line[3:].strip()}</h2>')
        elif line.startswith('# '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<h1>{line[2:].strip()}</h1>')
        
        # 4단계 제목 처리 (####)
        elif line.startswith('#### '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<h4>{line[5:].strip()}</h4>')
        
        # 리스트 처리
        elif line.startswith('- ') or line.startswith('• '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            content = line[2:].strip() if line.startswith('- ') else line[2:].strip()
            # 굵은 글씨 처리
            content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
            html_lines.append(f'<li>{content}</li>')
        
        # 들여쓰기 있는 리스트 처리
        elif line.startswith('  - ') or line.startswith('  • '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            content = line[4:].strip()
            content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
            html_lines.append(f'<li style="margin-left: 20px;">{content}</li>')
        
        # 체크박스 처리
        elif line.startswith('□ '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(f'<p>☐ {line[2:].strip()}</p>')
        
        # 일반 텍스트 처리
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            
            # 굵은 글씨 처리
            content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            # 기울임 처리
            content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
            html_lines.append(f'<p>{content}</p>')
    
    # 마지막에 열린 리스트 닫기
    if in_list:
        html_lines.append('</ul>')
    
    return '\n'.join(html_lines)

def create_full_html(title: str, content: str) -> str:
    """
    완전한 HTML 문서 생성
    """
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ 
            font-family: "Noto Sans CJK KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
            margin: 40px;
            line-height: 1.8;
            color: #333;
            background-color: #fafafa;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        h1 {{ 
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}
        
        h2 {{ 
            color: #27ae60;
            border-bottom: 2px solid #27ae60;
            padding-bottom: 10px;
            margin-top: 35px;
            margin-bottom: 20px;
        }}
        
        h3 {{ 
            color: #e74c3c;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        
        h4 {{
            color: #8e44ad;
            margin-top: 25px;
            margin-bottom: 10px;
        }}
        
        p {{ 
            margin: 10px 0;
            text-align: justify;
        }}
        
        ul {{
            margin: 15px 0;
            padding-left: 20px;
        }}
        
        li {{ 
            margin: 8px 0;
            line-height: 1.6;
        }}
        
        strong {{ 
            color: #2c3e50;
            font-weight: bold;
        }}
        
        em {{
            color: #7f8c8d;
            font-style: italic;
        }}
        
        br {{
            line-height: 1.5;
        }}
        
        /* 이모지 크기 조정 */
        .emoji {{
            font-size: 1.2em;
        }}
        
        /* 인쇄 스타일 */
        @media print {{
            body {{ 
                font-size: 12pt;
                background-color: white;
                margin: 0;
            }}
            .container {{
                box-shadow: none;
                margin: 0;
                padding: 20px;
            }}
            h1 {{ font-size: 18pt; }}
            h2 {{ font-size: 16pt; }}
            h3 {{ font-size: 14pt; }}
            h4 {{ font-size: 13pt; }}
            p {{ font-size: 12pt; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>"""

def convert_file(input_file: str, output_file: str = None) -> str:
    """
    Markdown 파일을 HTML로 변환
    """
    try:
        # 파일 읽기
        with open(input_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # 출력 파일명 생성
        if output_file is None:
            output_file = input_file.replace('.md', '.html')
        
        # 제목 생성
        title = os.path.basename(input_file).replace('.md', '')
        
        # HTML 변환
        html_content = convert_markdown_to_html(markdown_content)
        full_html = create_full_html(title, html_content)
        
        # 파일 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"✅ HTML 변환 완료: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"❌ 변환 실패: {e}")
        return None

def batch_convert(input_dir: str, output_dir: str = None):
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
    
    print(f"📄 {len(md_files)}개의 Markdown 파일을 변환합니다...")
    
    success_count = 0
    for md_file in md_files:
        output_file = output_path / (md_file.stem + '.html')
        result = convert_file(str(md_file), str(output_file))
        if result:
            success_count += 1
    
    print(f"✅ 완료: {success_count}/{len(md_files)} 파일 변환 성공")
    print("\n💡 PDF 저장 방법:")
    print("1. 브라우저에서 HTML 파일 열기")
    print("2. Ctrl+P (인쇄)")
    print("3. 대상을 'PDF로 저장'으로 선택")
    print("4. 저장 클릭")

def main():
    parser = argparse.ArgumentParser(description='개선된 Markdown to HTML 변환기')
    parser.add_argument('input', help='입력 파일 또는 디렉토리')
    parser.add_argument('-o', '--output', help='출력 파일 또는 디렉토리')
    parser.add_argument('--batch', action='store_true', help='디렉토리 내 모든 파일 변환')
    
    args = parser.parse_args()
    
    if args.batch:
        batch_convert(args.input, args.output)
    else:
        if os.path.isfile(args.input):
            convert_file(args.input, args.output)
        else:
            print(f"❌ 파일을 찾을 수 없습니다: {args.input}")

if __name__ == '__main__':
    main()