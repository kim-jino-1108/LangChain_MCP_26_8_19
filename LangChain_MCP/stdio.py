# stdio 연결을 위한 서버 파라미터 생성
import asyncio  # 비동기 함수를 실행하기 위한 이벤트 루프 실행 모듈

from mcp import ClientSession, StdioServerParameters  # MCP 세션과 stdio 서버 파라미터 클래스
from mcp.client.stdio import stdio_client  # stdio 전송(transport) 방식의 클라이언트

from langchain_mcp_adapters.tools import load_mcp_tools  # MCP 도구를 LangChain 도구로 변환
from langchain.agents import create_agent  # LangChain 에이전트 생성 함수
import os
from dotenv import load_dotenv

load_dotenv()

server_params = StdioServerParameters(
    command="python",  # 서버 스크립트를 실행할 명령어
    # math_server.py 파일의 전체 절대 경로로 수정해서 사용
    args=["math_server2.py"],  # command에 전달할 인자, 여기서는 실행할 서버 스크립트 파일명
)


# 비동기 로직을 담는 메인 함수 정의
async def main():
    # stdio_client로 서버 프로세스를 실행하고 읽기/쓰기 스트림을 확보
    async with stdio_client(server_params) as (read, write):
        # 읽기/쓰기 스트림으로 MCP 클라이언트 세션 생성
        async with ClientSession(read, write) as session:
            # 세션 초기화(핸드셰이크 수행)
            await session.initialize()

            # 서버가 제공하는 도구 목록을 가져와 LangChain 도구로 변환
            tools = await load_mcp_tools(session)

            # 모델과 도구를 사용해 에이전트 생성
            agent = create_agent("openai:gpt-5-mini", tools)
            # 사용자 메시지를 전달해 에이전트 실행 후 응답 반환
            agent_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})

            # 에이전트 응답을 화면에 출력
            print(agent_response)
            # 마지막 메시지 내용만 따로 출력
            print(agent_response["messages"][-1].content)


# 스크립트가 직접 실행될 때만 main 코루틴을 이벤트 루프에서 실행
if __name__ == "__main__":
    asyncio.run(main())