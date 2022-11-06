import os
import time
import json

from google.cloud import language_v1
from flask import Flask, request


app = Flask(__name__)
client = language_v1.LanguageServiceClient()

def get_tags_from_text(text) -> dict:
  document = language_v1.Document(
    content=text, 
    type_=language_v1.Document.Type.PLAIN_TEXT,
    language = "ja"
  )

  request = language_v1.AnalyzeSyntaxRequest(
    document=document,
  )
  
  # Detects the sentiment of the text
  response = client.analyze_syntax(
    request=request
  )

  result = []
  for token in response.tokens:
    print("tag: {}".format(token.lemma))
    print("text: {}".format(token.text))
    print("part_of_speech: {}".format(token.part_of_speech))
    print("dependency_edge: {}".format(token.dependency_edge))
    result.append({
      "tag": token.lemma,
      "part_of_spech_tag": token.part_of_speech.tag.name,
      "dependency_edge_label": token.dependency_edge.label.name
      })
  return {'tokens': result}


@app.route("/", methods=['POST'])
def get_syntaxes():
  return_value = []
  request_json = request.get_json()
  calls = request_json['calls']
  
  
  for call in calls:
    for text in call:
      try:
        tags = get_tags_from_text(text)
      except Exception as e:
        if(e.code==429):
          print(f"{'sleeping':*^20}")
          time.sleep(3600)
          tags = get_tags_from_text(text)
        else:
          print("ERROR")
          print(e)
          tags = {'tokens': ""}
      finally:
        return_value.append(tags)
      
  replies = [str(x) for x in return_value]
  return json.dumps(({ "replies" :  replies}))
  

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))