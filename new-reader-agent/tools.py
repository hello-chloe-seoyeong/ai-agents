import time
from crewai_tools import tool, SerperDevTool
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup # beautifulsoup: HTML을 다루고 조작하는 거, 태그 찾고, 바꾸고 지우고 등

search_tool = SerperDevTool(
  n_results=5
)

search_tool.run(search_query="Cambodia Thai War")

@tool
def scrape_tool(url:str):
  """
    Use this when you need to read the content of a website.
    Returns the content of a website, in case the website is not available, it returns 'No content'.
    Input should be a `url` string. for example (https://www.reuters.com/world/asia-pacific/cambodia-thailand-begin-talks-malaysia-amid-fragile-ceasefire-2025-08-04/)
  """

  print(f"Scrapping URL: {url}")

  with sync_playwright as p:
    # 브라우저 키고, 페이지 이동, 그 페이지에서 html 추출하고, 정리(header, footer, nav 등 필요 하지 않는 거 정리)

    browser = p.chromium.launch(headless=True) # 브라우저 창 없이 백그라운드에서 실행하기

    page = browser.new_page()

    page.goto(url)

    time.sleep(5) # 모두 로드 될때까지 조금 기다리는거

    html = page.content()

    browser.close()

    soup = BeautifulSoup(html, "html.parser")

    unwated_tags = [
      "header",
      "footer",
      "nav",
      "aside",
      "script",
      "style",
      "noscript",
      "iframe",
      "form",
      "button",
      "input",
      "select",
      "textarea",
      "img",
      "svg",
      "canvas",
      "audio",
      "video",
      "embed",
      "object"
    ]

    for tag in soup.find_all(unwated_tags):
      tag.decompose() # decompose (통째로 삭제) 페이지 요소와 그 자식들까지 없애줌

    content = soup.get_text(separator=" ")

    return content if content != "" else "No content"