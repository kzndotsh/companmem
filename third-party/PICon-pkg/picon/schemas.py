from pydantic import BaseModel
from typing import Literal, Dict, Any, List

class ToolCall(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    details: List | Dict | Any | None = None # LLM 응답 전체

class Action(BaseModel):
    agent: str | None = None                # action을 수행한 agent 이름
    action_type: Literal["respond", "next_agent", "tool_call", "finish"]
    content: Any | None = None              # 'respond'일 경우 응답 내용
    target_agent: str | None = None         # 'next_agent'일 경우 다음 act할 에이전트 이름
    tool_call: ToolCall | None = None       # 'tool_call'일 경우 사용할 툴 정보

class IntervieweeResponse(BaseModel):
    question: str
    content: str

class ToolOutput(BaseModel):
    tool_call_id: str
    tool_name: str
    arguments: Dict[str, Any] | None = None  # Optional for backward compatibility with saved data
    output: str |List | List[Dict] | Any # 웹 검색 결과 등

class Observation(BaseModel):
    observation_type: Literal["interviewee_response", "tool_output"]
    response: IntervieweeResponse | None = None # interviewee의 답변
    tool_output: List[ToolOutput] | None = None # if we did the tool call

class Turn(BaseModel):
    type: Literal['get_to_know', 'main_interrogation', 'repeat']
    agent_action: List[Action] | None = None # 여러 action이 있을 수 있음
    environment_observation: List[Observation] = [] # 여러 observation이 있을 수 있음

class State(BaseModel):
    current_turn: int
    current_observation: Observation | None = None
    history: List[Turn] = [] # Action과 Observation의 순차적 기록