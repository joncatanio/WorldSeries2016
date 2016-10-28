import requests, json, xml
from xml.dom.minidom import parseString as xmlParseString

mlbEndpoint = 'http://gd.mlb.com'

def getGames(content, date):
   scoreboard = requests.get(mlbEndpoint + '/components/game/mlb/year_' + date.strftime('%Y') + '/month_' + date.strftime('%m') + '/day_' + date.strftime('%d') + '/master_scoreboard.json')
   jsonSB = scoreboard.json()
   jsonGames = jsonSB['data']['games']

   for obj in jsonGames['game']:
      content.append({ 'home': obj['home_name_abbrev'], 'away': obj['away_name_abbrev'],
                     'home_id': obj['home_team_id'], 'away_id': obj['away_team_id'],
                     'game_data_dir': obj['game_data_directory'] ,
                     'rank_factors': { 'home': [], 'away': []}})

def getPitchingMatchup(content):
   matchup = []
   players = requests.get(mlbEndpoint + content['game_data_dir'])


def getWinLoseStreak(content, date):  
   standingsNL = requests.get('http://mlb.mlb.com/lookup/named.standings_all.bam?sit_code=\'h0\'' + \
      '&league_id=\'104\'&season=\'' + date.strftime('%Y') + '\'')
   standingsAL = requests.get('http://mlb.mlb.com/lookup/named.standings_all.bam?sit_code=\'h0\'' + \
      '&league_id=\'103\'&season=\'' + date.strftime('%Y') + '\'')

   print(standingsNL)
   standingsNL = xmlParseString(standingsNL.text)
   standingsAL = xmlParseString(standingsAL.text)
   test = [node for node in standingsAL.getElementsByTagName("team_id") if node.nodeValue == '147']
   print(test)
   for team in standingsAL.getElementsByTagName("row"):
      print(team.children)
   
   #for game in content:
    #  if game['home_id'] 

   return content
 
def buildAppContent(date):
   content = []
   getGames(content, date)
   getWinLoseStreak(content, date)

   return content
