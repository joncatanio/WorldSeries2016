from datetime import date
import request_engine

def main():
   curDate = date(2016, 6, 16)
   games = request_engine.getGames(curDate)
   teamBatAvgs = request_engine.getTeamBatAvg(games)
main()
