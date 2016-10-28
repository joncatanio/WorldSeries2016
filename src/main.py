from datetime import date
from request_engine import buildAppContent
from content_save import save_content

def main():
   curDate = date(2016, 6, 21)
   appContent = buildAppContent(curDate)
   print(appContent)

   save_content('../../WorldSeries2016_API/datastore/' + curDate.isoformat() + '.txt', appContent)

main()
