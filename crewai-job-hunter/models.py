# for schema: AI가 따라야 할 모든 데이터의 형태를 정의 (structured outputs)

# pydantic: 특정 형태를 만들 수 있게 해주는 패키지

from datetime import date
from pydantic import BaseModel

class Job():
  job_title: str
  company_name: str
  job_location: str
  is_remote_friendly: bool | None = None # None is 기본적으로 필수가 아니고, 기본이 None 값이라는거
  employment_type: str | None = None
  compensation: str | None = None
  job_posting_url: str
  job_summary: str

  key_qualifications: list[str] | None = None
  job_responsibilities: list[str] | None = None
  date_listed: date | None = None
  required_technologies: list[str] | None = None
  core_keywords: list[str] | None = None

  role_seniority_level: str | None = None
  years_of_experience_required: str | None = None
  minimum_education: str | None = None
  job_benefits: list[str] | None = None
  includes_equity: bool | None = None
  offers_visa_sponsorship: bool | None = None
  hiring_company_size: str | None = None
  hiring_industry: str | None = None
  source_listing_url: str | None = None
  full_raw_job_description: str | None = None

# {
#   'jobs': [{position: 'xxx', location: 'xxx', is_remote: false}, {...}]
# }

class JobList(BaseModel):
  jobs: list[Job]

class RankedJob(BaseModel):
  job: Job
  match_score: int
  reason: str

class RankedJobList(BaseModel):
  ranked_jobs: list[RankedJob]

class ChosenJob(BaseModel):
  job: Job
  selected: bool
  reason: str