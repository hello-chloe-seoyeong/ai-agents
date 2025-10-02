import requests
import os, re

from crewai.tools import tool

@tool
def web_search_tool(query: str):
  """
  Search the jobs information
  """

  url = "https://api.firecrawl.dev/v2/search"

  payload = {
    "query": query,
    "sources": ["web"],
    "categories": [],
    "limit": 5,
    "scrapeOptions": {
      "onlyMainContent": True,
      "maxAge": 172800000,
      "parsers": ["pdf"],
      "formats": ["markdown"]
    }
  }

  headers = {
      "Authorization": f"Bearer {os.getenv('FIRECRAWL_API_KEY')}",
      "Content-Type": "application/json"
  }

  response = requests.post(url, json=payload, headers=headers)
  response = response.json()

  if not response["success"]:
    return "Error using tool."

  cleaned_chunks = []

  for result in response["data"]["web"]:

    title = result["title"]
    url = result["url"]
    markdown = result["markdonw"]

    cleaned = re.sub(r'\\+|\n', '', markdown).strip() # \랑 \n줄바꿈을 ''으로 바꿀꺼고, 그걸 markdown에서 바꿔줄거야, 그리고 뒤(?) 공백 자르기
    cleaned = re.sub(r'\[[^\]]+\]\([^\]+\) |https?://[^\s]+', "", cleaned)

    cleaned_result = {
      "title": title,
      "url": url,
      "markdown": cleaned
    }

    cleaned_chunks.append(cleaned_result)

  return cleaned_chunks
