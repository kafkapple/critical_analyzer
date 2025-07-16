#!/usr/bin/env python3
"""
PDF 생성 도구 - 다양한 방법으로 HTML을 PDF로 변환
"""

import os
import subprocess
import webbrowser
from pathlib import Path
import time

class PDFGenerator:
    def __init__(self):
        self.available_tools = self.check_available_tools()
        
    def check_available_tools(self):
        """사용 가능한 PDF 변환 도구 확인"""
        tools = {}
        
        # wkhtmltopdf 확인
        try:
            subprocess.run(['wkhtmltopdf', '--version'], 
                         capture_output=True, check=True)
            tools['wkhtmltopdf'] = True
        except:
            tools['wkhtmltopdf'] = False
            
        # pandoc 확인
        try:
            subprocess.run(['pandoc', '--version'], 
                         capture_output=True, check=True)
            tools['pandoc'] = True
        except:
            tools['pandoc'] = False
            
        # chromium/chrome 확인
        chrome_paths = [
            '/usr/bin/chromium-browser',
            '/usr/bin/google-chrome',
            '/usr/bin/chromium',
            '/snap/bin/chromium'
        ]
        
        tools['chrome'] = False
        for path in chrome_paths:
            if os.path.exists(path):
                tools['chrome'] = path
                break
                
        return tools
    
    def generate_pdf_wkhtmltopdf(self, html_file, pdf_file):
        """wkhtmltopdf를 사용한 PDF 생성"""
        if not self.available_tools.get('wkhtmltopdf'):
            return False
            
        try:
            cmd = [
                'wkhtmltopdf',
                '--page-size', 'A4',
                '--margin-top', '0.75in',
                '--margin-right', '0.75in',
                '--margin-bottom', '0.75in',
                '--margin-left', '0.75in',
                '--encoding', 'UTF-8',
                '--no-stop-slow-scripts',
                '--javascript-delay', '2000',
                str(html_file),
                str(pdf_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ wkhtmltopdf로 PDF 생성 완료: {pdf_file}")
                return True
            else:
                print(f"❌ wkhtmltopdf 오류: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ wkhtmltopdf 실행 오류: {e}")
            return False
    
    def generate_pdf_chrome(self, html_file, pdf_file):
        """Chrome/Chromium을 사용한 PDF 생성"""
        chrome_path = self.available_tools.get('chrome')
        if not chrome_path:
            return False
            
        try:
            cmd = [
                chrome_path,
                '--headless',
                '--disable-gpu',
                '--no-sandbox',
                '--print-to-pdf=' + str(pdf_file),
                '--print-to-pdf-no-header',
                '--run-all-compositor-stages-before-draw',
                '--virtual-time-budget=2000',
                f'file://{os.path.abspath(html_file)}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(pdf_file):
                print(f"✅ Chrome으로 PDF 생성 완료: {pdf_file}")
                return True
            else:
                print(f"❌ Chrome PDF 생성 실패: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Chrome 실행 오류: {e}")
            return False
    
    def generate_pdf_browser_guide(self, html_file):
        """브라우저 수동 PDF 생성 가이드"""
        print(f"\n🌐 브라우저에서 PDF 생성하기: {html_file}")
        print("=" * 60)
        
        # 브라우저에서 파일 열기
        file_url = f'file://{os.path.abspath(html_file)}'
        webbrowser.open(file_url)
        
        print("📄 PDF 생성 단계:")
        print("1. 브라우저에서 Ctrl+P (또는 Cmd+P) 누르기")
        print("2. 대상을 'PDF로 저장' 선택")
        print("3. 여백을 '최소' 또는 '사용자 지정'으로 설정")
        print("4. 배경 그래픽 인쇄 활성화")
        print("5. 저장 위치 지정 후 저장 클릭")
        print("6. 저장된 PDF 파일을 적절한 위치로 이동")
        print("=" * 60)
    
    def generate_pdf_auto(self, html_file, pdf_file):
        """자동 PDF 생성 (사용 가능한 도구 순서대로 시도)"""
        print(f"\n🔄 PDF 자동 생성 시도: {html_file} -> {pdf_file}")
        
        # 1. wkhtmltopdf 시도
        if self.available_tools.get('wkhtmltopdf'):
            print("🔧 wkhtmltopdf로 시도...")
            if self.generate_pdf_wkhtmltopdf(html_file, pdf_file):
                return True
        
        # 2. Chrome 시도
        if self.available_tools.get('chrome'):
            print("🔧 Chrome으로 시도...")
            if self.generate_pdf_chrome(html_file, pdf_file):
                return True
        
        # 3. 수동 방법 안내
        print("❌ 자동 PDF 생성 실패. 수동 방법 안내:")
        self.generate_pdf_browser_guide(html_file)
        return False
    
    def process_all_html_files(self):
        """모든 HTML 파일을 PDF로 변환"""
        print("🎯 전체 HTML 파일 PDF 변환 시작")
        print("=" * 60)
        
        # 사용 가능한 도구 출력
        print("🔍 사용 가능한 도구:")
        for tool, available in self.available_tools.items():
            status = "✅" if available else "❌"
            print(f"  {status} {tool}: {available}")
        print()
        
        # 각 카테고리별 처리
        reports_dir = Path("outputs/reports")
        
        for category in ['student', 'teacher']:
            category_dir = reports_dir / category
            if not category_dir.exists():
                continue
                
            html_files = list(category_dir.glob("*.html"))
            print(f"📁 {category} 카테고리: {len(html_files)}개 파일")
            
            success_count = 0
            for html_file in html_files:
                pdf_file = html_file.with_suffix('.pdf')
                
                if self.generate_pdf_auto(str(html_file), str(pdf_file)):
                    success_count += 1
                    
            print(f"✅ {category} 카테고리 완료: {success_count}/{len(html_files)}")
            print()
        
        print("🎉 PDF 변환 프로세스 완료!")

def main():
    """메인 함수"""
    generator = PDFGenerator()
    generator.process_all_html_files()

if __name__ == "__main__":
    main()