from crewai.tools import tool

@tool
def count_letters(sentence: str):
  """
  This function is to count the amount of letters in a sentence.
  The input is a `sentence` string.
  The output is a number.
  """
  # 위에 """ doc string """: 이 안에 부분이 함수를 설명하는 내용, crew ai가 이 doc string을 사용해서 function schema를 만들어
  print("tool called with input:", sentence)
  return len(sentence)