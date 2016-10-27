import requests, json, xml

mlbEndpoint = 'http://gd.mlb.com'

def getGames(content, date):
   scoreboard = requests.get(mlbEndpoint + '/components/game/mlb/year_' + date.strftime('%Y') + '/month_' + date.strftime('%m') + '/day_' + date.strftime('%d') + '/master_scoreboard.json')
   jsonSB = scoreboard.json()
   jsonGames = jsonSB['data']['games']

   for obj in jsonGames['game']:
      content.append({ 'home': obj['home_name_abbrev'], 'away': obj['away_name_abbrev'],
                     'home_id': obj['home_team_id'], 'away_id': obj['away_team_id'],
                     'game_data_dir': obj['game_data_directory'] })

def getPitchersOfGames():

   return

def buildAppContent(date):
   content = []
   buildGames(content, date)

   return content
