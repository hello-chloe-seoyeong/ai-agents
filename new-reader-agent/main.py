
import dotenv

dotenv.load_dotenv()

from crewai import Crew, Agent, Task
from crewai.project import CrewBase, crew, agent, task
from tools import search_tool, scrape_tool

@CrewBase
class NewsReaderAgent:

	@agent
	def news_hunter_agent(self):
		return Agent(
			config=self.agents_config["news_hunter_agent"],
			tools=[ search_tool, scrape_tool]
		)

	@agent
	def summarizer_agent(self):
		return Agent(
			config=self.agents_config["summarizer_agent"],
			tools=[scrape_tool]
		)

	@agent
	def curator_agent(self):
		return Agent(
			config=self.agents_config["curator_agent"]
	)

	@task
	def content_harvesting_task(self):
		return Task(
			config=self.tasks_config["content_harvesting_task"]
		)

	@task
	def summarization_task(self):
		return Task(
			config=self.tasks_config["summarization_task"]
		)

	@task
	def final_report_assembly_task(self):
		return Task(
			config=self.tasks_config["final_report_assembly_task"]
		)

	@crew
	def crew(self):
		return Crew(
			tasks=self.tasks,
			agents=self.agents,
			verbose=True
		)

NewsReaderAgent().crew().kickoff(inputs={ "topic": "Stable coin" }) # tasks.yaml 보면 topic 받아야하는 걸로 되어있어

# class 안에 있는 tasks들은 자동으로 1번째 task가 끝나면 그 output이 다음 task의 input으로 가고 가고 가고.. 
# 마지막 output으로 뭔가를 하고 싶으면 ? 

response = NewsReaderAgent().crew().kickoff(inputs={ "topic": "Stable coin" })

# for task_output in response.tasks_output: # tasks_output 접근 방법, type=list
# 	# for문으로 개별 결과물 확인 가능
# 	print(task_output)