from datetime import date
import request_engine

def main():
   curDate = date(2016, 6, 16)
   request_engine.getGames(curDate)

main()
