import dotenv

dotenv.load_dotenv()

from crewai import Crew, Agent, Task
from crewai.project import CrewBase, agent, task, crew # decorator
from tools import count_letters


# create crew
@CrewBase
class TranslatorCrew:

	@agent
	def translator_agent(self):
		return Agent(
			config=self.agents_config["translator_agent"]
		)
	# Agent Attributes: Role-agent가 crew안에서 어떤 역할을 하는지 알려주는 거 / Gola-의사결정할때 참고할 내용 / Backstory-agent의 성격이나 배경 같은 맥락

	@agent
	def counter_agent(self):
		return Agent(
			config=self.agents_config["counter_agent"],
			tools=[count_letters]
		)

	@task
	def translate_task(self):
		return Task(
			config=self.tasks_config["translate_task"]
		)

	@task
	def retranslate_task(self):
		return Task(
			config=self.tasks_config["retranslate_task"]
		)

	@task
	def count_task(self):
		return Task(
			config=self.tasks_config["count_task"]
		)

	@crew
	def assemble_crew(self):
		return Crew(
			# 여기서 self.agents, self.tasks 로 사용할 수 있는 건 위에 데코레이터로 @task, @agent를 붙여놔서 가능, 각 데코레이터가 붙은 각 해당 이름의 리스트(?)로 들어가
			agents=self.agents,
			tasks=self.tasks,
			verbose=True # log 볼수있음
		)

TranslatorCrew().assemble_crew().kickoff(
	inputs={
		"sentence": "I'm Chloe and I like to ride my bicicle in Napoli"
	}
)