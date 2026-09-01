from mcp.server.fastmcp import FastMCP  # FastMCP: MCP 서버를 빠르게 구성하는 클래스 임포트
import os  # 파일 시스템 경로 및 디렉토리 접근용 표준 라이브러리
import stat  # 파일 모드(권한) 문자열 변환용 표준 라이브러리
import time  # 타임스탬프를 사람이 읽는 문자열로 변환하는 표준 라이브러리
from typing import List  # 반환 타입 힌트 List 임포트


mcp = FastMCP(  # [ 1 ] FastMCP 서버 인스턴스 생성
    "FileSearch",  # 서버 이름 지정
    instructions="로컬 파일 검색을 도와주는 어시스턴트입니다."  # 서버 동작 안내 문구 설정
)


# 파일 목록 호출
@mcp.tool()  # [ 2 ] 이 함수를 MCP 도구로 등록
async def file_listup(directory: str) -> List[str]:  # directory 경로를 받아 문자열 리스트 반환
    """지정된 디렉토리 경로의 파일 이름 목록을 반환합니다."""  # 도구 설명(스키마에 노출)
    try:
        return os.listdir(directory)  # 해당 디렉토리 내 항목 이름 리스트 반환
    except Exception as e:  # 접근 실패 등 예외 발생 시
        return [f"오류: {str(e)}"]  # 오류 메시지를 담은 리스트 반환


# 파일 검색 요약 및 정리 담당
@mcp.tool()  # [ 3 ] 이 함수를 MCP 도구로 등록
async def file_info(path: str) -> dict:  # path를 받아 상세 정보 딕셔너리 반환
    """
    지정된 경로의 파일 또는 디렉토리에 대한 상세 정보를 반환합니다.
    """  # 도구 설명(스키마에 노출)
    if not os.path.exists(path):  # 경로가 존재하지 않으면
        return {"error": f"경로 '{path}' 가 존재하지 않습니다."}  # 오류 딕셔너리 반환

    try:
        stat_info = os.stat(path)  # 파일 상태 정보(크기, 시간, 모드 등) 조회

        permissions = stat.filemode(stat_info.st_mode)  # 모드 값을 권한 문자열로 변환

        with open(path, "r", encoding="utf-8") as f:  # 파일을 UTF-8 텍스트 모드로 열기
            content = f.read()  # 파일 전체 내용을 문자열로 읽기

        return {
            "path": os.path.abspath(path),  # 절대 경로
            "content": content,  # 읽어들인 파일 내용
            "type": "file",  # 타입을 "file" 문자열로 지정
            "size": stat_info.st_size,  # bytes  # 파일 크기(바이트)
            "created_time": time.ctime(stat_info.st_birthtime),  # 생성 시각 문자열
            "modified_time": time.ctime(stat_info.st_mtime),  # 수정 시각 문자열
            "access_time": time.ctime(stat_info.st_atime),  # 접근 시각 문자열
            "permissions": permissions,  # 권한 문자열
        }
    except Exception as e:  # 파일 열기/조회 중 예외 발생 시
        return {"error": str(e)}  # 오류 딕셔너리 반환


# 파일 쓰기 저장 담당
@mcp.tool()  # [ 4 ] 이 함수를 MCP 도구로 등록
async def save_file(content: str, output_path="file_info.md") -> str:  # content를 output_path에 저장, 경로 반환
    """제공된 내용을 지정된 output_path의 텍스트 파일에 작성합니다."""  # 도구 설명(스키마에 노출)
    with open(output_path, "w", encoding="utf-8") as f:  # 파일을 UTF-8 쓰기 모드로 열기
        f.write(content)  # content를 파일에 기록

    return output_path  # 저장한 파일 경로 반환


if __name__ == "__main__":  # [ 5 ] 스크립트가 직접 실행될 때만 아래 코드 실행
    # 서버 시작 안내 메시지를 콘솔에 출력
    print("MCP server started and waiting for clients...")
    # streamable-http 전송 방식으로 MCP 서버를 실행 (기본적으로 http://localhost:8000/mcp 에서 대기)
    mcp.run(transport="streamable-http")