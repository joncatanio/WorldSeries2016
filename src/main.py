from datetime import date
import request_engine

def main():
   curDate = date(2016, 6, 17)
   appContent = request_engine.buildAppContent(curDate)
   print(appContent)

main()
