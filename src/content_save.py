import json

def save_content(filepath, content):
   with open(filepath, 'w') as outfile:
       json.dump(content, outfile)
