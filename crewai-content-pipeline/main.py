from crewai.flow.flow import Flow, listen, start, router, and_, or_ # and_, or_ 모두 여러개의 function을 실행시킬수 있는데, and_는 모두 끝나야만, or_은 그중에 하나만 끝나고 코드 실행 가능 
from pydantic import BaseModel

class MyFirstFlowState(BaseModel):

  user_id: int = 1
  is_admin: bool = False

# FLOW: 여러 개의 method를 가진 class. <= method는 클래스 안에 있는 function
class MyFirstFlow(Flow[MyFirstFlowState]):

  @start()
  def first(self):
    print(self.state.user_id)
    print("Hello")

  @listen(first) # first가 끝나길 기다리는거
  def second(self):
    self.state.user_id = 2
    print("world")

  @listen(first)
  def third(self):
    print("!")

  @listen(and_(second, third))
  def final(self):
    print(":)")

  @router(final)
  def route(self):
    if self.state.is_admin:
      return "even"
    else:
      return "odd"

  @listen("even")
  def handle_even(self):
    print("even")

  @listen("odd")
  def handle_odd(self):
    print("odd")

flow = MyFirstFlow() # instance화

flow.plot() # flow를 시각화해서 저장해줘
flow.kickoff()