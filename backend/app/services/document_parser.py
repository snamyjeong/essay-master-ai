# 다양한 형식의 문서를 파싱하여 텍스트 내용을 추출하는 서비스 파일입니다.
# 현재는 PDF 파일과 일반 텍스트 파일을 지원합니다.

from pypdf import PdfReader # PDF 파일 읽기를 위한 pypdf 라이브러리 임포트
import io # 인메모리 바이너리 스트림 처리를 위한 io 모듈 임포트

# 문서 파서 클래스 정의
class DocumentParser:
    def __init__(self):
        """
        DocumentParser를 초기화합니다.
        현재는 특별한 초기화 설정은 필요 없습니다.
        """
        pass

    async def parse_pdf(self, file_content: bytes) -> str:
        """
        PDF 파일의 바이너리 내용을 파싱하여 모든 페이지의 텍스트를 추출합니다.
        :param file_content: PDF 파일의 바이너리 데이터
        :return: PDF에서 추출된 모든 텍스트를 담은 문자열
        """
        try:
            # io.BytesIO를 사용하여 바이너리 데이터를 파일처럼 처리합니다.
            pdf_file = io.BytesIO(file_content)
            # PdfReader를 사용하여 PDF 파일을 읽습니다.
            reader = PdfReader(pdf_file)
            text_content = ""
            # PDF의 각 페이지를 순회하며 텍스트를 추출합니다.
            for page in reader.pages:
                text_content += page.extract_text() + "\n" # 각 페이지의 텍스트를 추출하고 줄바꿈 추가
            return text_content.strip() # 추출된 텍스트의 앞뒤 공백 제거 후 반환
        except Exception as e:
            print(f"PDF 파싱 중 오류 발생: {e}") # 오류 발생 시 콘솔에 출력
            raise ValueError(f"PDF 파일을 파싱할 수 없습니다: {e}") # ValueError 발생

    async def parse_text(self, file_content: bytes) -> str:
        """
        일반 텍스트 파일의 바이너리 내용을 파싱하여 문자열로 디코딩합니다.
        :param file_content: 텍스트 파일의 바이너리 데이터
        :return: 디코딩된 텍스트 문자열
        """
        try:
            # UTF-8로 디코딩을 시도하고, 실패하면 다른 일반적인 인코딩으로 시도합니다.
            # `errors='ignore'`를 사용하여 디코딩 불가능한 문자를 무시합니다.
            return file_content.decode('utf-8').strip()
        except UnicodeDecodeError:
            # UTF-8이 아닌 경우 cp949(EUC-KR)로 재시도 (한국어 환경 고려)
            return file_content.decode('cp949', errors='ignore').strip()
        except Exception as e:
            print(f"텍스트 파일 파싱 중 오류 발생: {e}") # 오류 발생 시 콘솔에 출력
            raise ValueError(f"텍스트 파일을 파싱할 수 없습니다: {e}") # ValueError 발생

# DocumentParser 인스턴스를 전역으로 생성하여 애플리케이션 전반에서 재사용합니다.
document_parser = DocumentParser()
