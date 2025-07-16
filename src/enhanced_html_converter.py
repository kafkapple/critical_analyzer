#!/usr/bin/env python3
"""
Enhanced HTML Converter with LaTeX Math Support and PDF Generation
수식 지원 및 PDF 생성 기능이 포함된 HTML 변환기
"""

import os
import re
import markdown
import webbrowser
import tempfile
import subprocess
from pathlib import Path

class EnhancedHTMLConverter:
    def __init__(self):
        self.math_patterns = [
            # Inline math: $...$
            (r'\$([^$]+)\$', r'<span class="math-inline">\\(\1\\)</span>'),
            # Display math: $$...$$
            (r'\$\$([^$]+)\$\$', r'<div class="math-display">\\[\1\\]</div>'),
            # LaTeX commands
            (r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\\frac{\1}{\2}'),
            (r'\\sin', r'\\sin'),
            (r'\\cos', r'\\cos'),
            (r'\\tan', r'\\tan'),
            (r'\\log', r'\\log'),
            (r'\\theta', r'\\theta'),
        ]
        
    def convert_math_expressions(self, text):
        """수식 표현을 MathJax 형태로 변환"""
        # 먼저 $$ 형태의 display math 처리
        text = re.sub(r'\$\$([^$]+)\$\$', r'<div class="math-display">\\[\1\\]</div>', text, flags=re.DOTALL)
        
        # 그 다음 $ 형태의 inline math 처리
        text = re.sub(r'\$([^$\n]+)\$', r'<span class="math-inline">\\(\1\\)</span>', text)
        
        return text

    def convert_to_html(self, md_file_path, output_file_path):
        """마크다운을 수식 지원 HTML로 변환"""
        try:
            # 마크다운 파일 읽기
            with open(md_file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # 수식 변환
            md_content = self.convert_math_expressions(md_content)
            
            # 마크다운을 HTML로 변환
            html_content = markdown.markdown(md_content, extensions=['nl2br', 'tables'])
            
            # 파일명에서 제목 추출
            title = Path(md_file_path).stem
            
            # 완전한 HTML 문서 생성
            full_html = self.create_full_html(html_content, title)
            
            # HTML 파일 저장
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(full_html)
            
            print(f"✅ HTML 생성 완료: {output_file_path}")
            return True
            
        except Exception as e:
            print(f"❌ HTML 변환 오류: {e}")
            return False

    def create_full_html(self, content, title):
        """완전한 HTML 문서 생성"""
        return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    
    <!-- MathJax 설정 -->
    <script>
        window.MathJax = {{
            tex: {{
                inlineMath: [['\\\\(', '\\\\)']],
                displayMath: [['\\\\[', '\\\\]']],
                processEscapes: true,
                processEnvironments: true
            }},
            options: {{
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
                ignoreHtmlClass: 'tex2jax_ignore',
                processHtmlClass: 'tex2jax_process'
            }}
        }};
    </script>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    
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
            page-break-after: avoid;
        }}
        
        h2 {{ 
            color: #27ae60;
            border-bottom: 2px solid #27ae60;
            padding-bottom: 10px;
            margin-top: 35px;
            margin-bottom: 20px;
            page-break-after: avoid;
        }}
        
        h3 {{ 
            color: #e74c3c;
            margin-top: 30px;
            margin-bottom: 15px;
            page-break-after: avoid;
        }}
        
        h4 {{
            color: #8e44ad;
            margin-top: 25px;
            margin-bottom: 10px;
            page-break-after: avoid;
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
        
        /* 수식 스타일 */
        .math-inline {{
            display: inline-block;
            margin: 0 2px;
        }}
        
        .math-display {{
            display: block;
            margin: 20px 0;
            text-align: center;
        }}
        
        /* 테이블 스타일 */
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
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
            
            h1 {{ 
                font-size: 18pt;
                page-break-after: avoid;
            }}
            
            h2 {{ 
                font-size: 16pt;
                page-break-after: avoid;
            }}
            
            h3 {{ 
                font-size: 14pt;
                page-break-after: avoid;
            }}
            
            h4 {{ 
                font-size: 13pt;
                page-break-after: avoid;
            }}
            
            p {{ 
                font-size: 12pt;
                orphans: 3;
                widows: 3;
            }}
            
            /* 페이지 나누기 방지 */
            .math-display {{
                page-break-inside: avoid;
            }}
            
            ul, ol {{
                page-break-inside: avoid;
            }}
        }}
        
        /* PDF 생성 가이드 */
        .pdf-guide {{
            background-color: #e8f5e8;
            border: 1px solid #4caf50;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        
        .pdf-guide h3 {{
            color: #4caf50;
            margin-top: 0;
        }}
        
        @media print {{
            .pdf-guide {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="pdf-guide">
            <h3>📄 PDF 생성 방법</h3>
            <p><strong>1단계:</strong> 브라우저에서 Ctrl+P (또는 Cmd+P) 누르기</p>
            <p><strong>2단계:</strong> 대상을 "PDF로 저장" 선택</p>
            <p><strong>3단계:</strong> 여백을 "최소"로 설정</p>
            <p><strong>4단계:</strong> "저장" 클릭</p>
        </div>
        
        {content}
    </div>
</body>
</html>"""

    def generate_pdf_via_browser(self, html_file_path):
        """브라우저를 통한 PDF 생성 가이드"""
        print(f"🌐 브라우저에서 PDF 생성하기: {html_file_path}")
        
        # 브라우저에서 파일 열기
        webbrowser.open(f'file://{os.path.abspath(html_file_path)}')
        
        print("📄 PDF 생성 방법:")
        print("1. 브라우저에서 Ctrl+P (또는 Cmd+P) 누르기")
        print("2. 대상을 'PDF로 저장' 선택")
        print("3. 여백을 '최소'로 설정")
        print("4. 배경 그래픽 인쇄 활성화")
        print("5. 저장 클릭")

def main():
    """메인 함수 - 모든 마크다운 파일을 HTML로 변환"""
    converter = EnhancedHTMLConverter()
    
    # 보고서 디렉토리 경로
    reports_dir = Path("outputs/reports")
    
    # 각 카테고리별 처리
    for category in ['student', 'teacher']:
        category_dir = reports_dir / category
        if not category_dir.exists():
            continue
            
        # 마크다운 파일 찾기
        md_files = list(category_dir.glob("*.md"))
        print(f"\n📁 {category} 카테고리: {len(md_files)}개 파일 처리")
        
        for md_file in md_files:
            # HTML 파일 경로 생성
            html_file = md_file.with_suffix('.html')
            
            # 변환 실행
            if converter.convert_to_html(str(md_file), str(html_file)):
                print(f"  ✅ {md_file.name} -> {html_file.name}")
            else:
                print(f"  ❌ {md_file.name} 변환 실패")
    
    print("\n🎉 모든 변환 완료!")
    print("\n📄 PDF 생성 방법:")
    print("1. HTML 파일을 브라우저에서 열기")
    print("2. Ctrl+P (또는 Cmd+P) 누르기")
    print("3. 'PDF로 저장' 선택")
    print("4. 여백을 '최소'로 설정")
    print("5. 저장 클릭")

if __name__ == "__main__":
    main()