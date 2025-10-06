from crewai.flow.flow import Flow, start, listen, router, and_, or_
from crewai.agent import Agent
from crewai import LLM # agent 없이 AI와 직접 대화 할 수 있게 해주는 class
from pydantic import BaseModel
from tools import web_search_tool
from seo_crew import SeoCrew
from virality_crew import ViralityCrew

class BlogPost(BaseModel):
  title: str
  subtitle: str
  sections: list[str]

class Tweet(BaseModel):
  content: str
  hashtags: str

class LinkedInPost(BaseModel):
  hook: str
  content: str
  call_to_action: str

class ContentScore(BaseModel):
  score: int = 0
  reason: str = ""

class ContentPipelineState(BaseModel):

  # Inputs
  content_type: str = ""
  topic: str = ""

  # Internal
  max_length: int = 0
  score: ContentScore | None = None
  research: str = "" # researcher가 실행되고 결과물이 저장될 곳

  # Content
  blog_post: BlogPost | None = None
  tweet: Tweet | None = None
  linkedin_post: LinkedInPost | None = None

class ContentPipelineFlow(Flow[ContentPipelineState]):

  @start()
  def init_content_pipeline(self):

    if self.state.content_type not in ["tweet", "blog", "linkedin"]:
      raise ValueError("The content type is wrong")

    if self.state.topic == "":
      raise ValueError("The topic can't be blank")

    if self.state.content_type == "tweet":
      self.state.max_length = 150
    elif self.state.content_type == "blog":
      self.state.max_length = 800
    elif self.state.content_type == "linkedin":
      self.state.max_length = 500

  @listen(init_content_pipeline)
  def conduct_research(self):

    researcher = Agent(
      role="Head Researcher",
      goal=f"Find the most interesing and useful info about {self.state.topic}",
      backstory="You're like a digital detective who loves digging up fascinating facts and insights. You have a knack for finding the good stuff that others miss.",
      tools=[web_search_tool]
    )

    self.state.research = researcher.kickoff(f"Find the most interesting and useful info about {self.state.topic}")

  @router(conduct_research)
  def conduct_research_router(self):
    content_type = self.state.content_type

    if content_type == "blog":
      return "make_blog"
    elif content_type == "tweet":
      return "make_tweet"
    else:
      return "make_linkedin_post"

  @listen(or_("make_blog", "remake_blog"))
  def handle_make_blog(self):
    # agent를 쓰지 않고 위 BaseModel 형태로 output을 강제하면서 AI와 직접 대화하는 방법!
    blog_post = self.state.blog_post

    llm = LLM(model="openai/o4-mini", response_format=BlogPost) # output을 BlogPost 이 형태로 해줘!

    if blog_post is None:
      # self.state.blog_post = llm.call( ... ) 원래 이렇게만 해도 되는데 json으로 바꾸는 부분에서 버그있어서 result 넣은 뒤에 바꿔주기
      result = llm.call(
        f"""
        Make a blog post on the topic {self.state.topic} using the following research:

        <research>
        ================
        {self.state.research}
        ================
        </research>
        """
      )
    else:
      result = llm.call(
        f"""
        You wrote this blog post on {self.state.topic}, but it does not have a good SEO score because of {self.state.score.reason}
        Improve it.

        <blog post>
        {self.state.blog_post.model_dump_json()}
        </blog post>

        Use the following research.

        <research>
        ================
        {self.state.research}
        ================
        </research>
        """
      )

    self.state.blog_post = BlogPost.model_validate_json(result)

  @listen(or_("make_tweet", "remake_tweet"))
  def handle_make_tweet(self):

    tweet = self.state.tweet

    llm = LLM(model="openai/o4-mini", response_format=Tweet) # output을 BlogPost 이 형태로 해줘!

    if tweet is None:
      result = llm.call(
        f"""
        Make a tweet on the topic {self.state.topic} using the following research:

        <research>
        ================
        {self.state.research}
        ================
        </research>
        """
      )
    else:
      result = llm.call(
        f"""
        You wrote this tweet on {self.state.topic}, but it does not have a good virality score because of {self.state.score.reason}
        Improve it.

        <tweet>
        {self.state.tweet.model_dump_json()}
        </tweet>

        Use the following research.

        <research>
        ================
        {self.state.research}
        ================
        </research>
        """
      )

    self.state.tweet = Tweet.model_validate_json(result)

  @listen(or_("make_linkedin_post", "remake_linkedin_post"))
  def handle_make_linkedin_post(self):

    linkedin_post = self.state.linkedin_post

    llm = LLM(model="openai/o4-mini", response_format=LinkedInPost) # output을 BlogPost 이 형태로 해줘!

    if linkedin_post is None:
      result = llm.call(
        f"""
        Make a linkedin post on the topic {self.state.topic} using the following research:

        <research>
        ================
        {self.state.research}
        ================
        </research>
        """
      )
    else:
      result = llm.call(
        f"""
        You wrote this blog post on {self.state.topic}, but it does not have a good virality score because of {self.state.score.reason}
        Improve it.

        <linkedin post>
        {self.state.linkedin_post.model_dump_json()}
        </linkedin post>

        Use the following research.

        <research>
        ================
        {self.state.research}
        ================
        </research>
        """
      )
    self.state.linkedin_post = LinkedInPost.model_validate_json(result)

  @listen(handle_make_blog)
  def check_seo(self):
    result = SeoCrew().crew().kickoff(inputs={
      "topic": self.state.topic,
      "blog_post": self.state.blog_post.model_dump_json() # pydantic -> json
    }) # 여러개의 input에 대해 crew를 kickoff 할 수 있음

    self.state.score = result.pydantic

    print(self.state.score)

  @listen(or_(handle_make_tweet, handle_make_linkedin_post))
  def check_virality(self):
    result = ViralityCrew().crew().kickoff(inputs={
      "topic": self.state.topic,
      "content_type": self.state.content_type,
      "content": self.state.tweet.model_dump_json() if self.state.content_type == "tweet" else self.state.linkedin_post.model_dump_json()
    }) # 여러개의 input에 대해 crew를 kickoff 할 수 있음

    self.state.score = result.pydantic

  @router(or_(check_seo, check_virality))
  def score_router(self):

    content_type = self.state.content_type
    score = self.state.score

    if score.score >= 8: # score가 ContentScore 형태자나 score, reason 가지고 있는, 그래서 한번더 선택해줘야함
      return "check_passed"
    else:
      if content_type == "blog":
        return "remake_blog"
      elif content_type == "tweet":
        return "remake_tweet"
      else:
        return "remake_linkedin_post"

  @listen("check_passed")
  def finalize_content(self):
    print("Finalizing content")

flow = ContentPipelineFlow()

# flow.plot()
flow.kickoff(inputs={ # flowState 값을 kickoff할때 inputs로 넣을 수 있어
  "content_type": "tweet",
  "topic": "AI dog training",
})