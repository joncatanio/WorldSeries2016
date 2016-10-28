import requests, json
import xml.etree.ElementTree as ET
from xml.dom.minidom import parse, parseString

mlbEndpoint = 'http://gd.mlb.com'

def getGames(content, date):
   res = requests.get(mlbEndpoint + '/components/game/mlb/year_' + date.strftime('%Y') + '/month_' + date.strftime('%m') + '/day_' + date.strftime('%d') + '/master_scoreboard.json')
   if res.status_code != requests.codes.ok:
      res.raise_for_status()

   jsonRes = res.json()
   jsonGames = jsonRes['data']['games']

   for obj in jsonGames['game']:
      content.append({ 'home': obj['home_name_abbrev'], 'away': obj['away_name_abbrev'],
                     'home_id': obj['home_team_id'], 'away_id': obj['away_team_id'],
                     'game_data_dir': obj['game_data_directory'] ,
                     'rank_factors': { 'home': [], 'away': []}})

def getPitchAndAvgData(content):
   matchup = []

   for game in content:
      res = requests.get(mlbEndpoint + game['game_data_dir'] + '/players.xml')
      if res.status_code != requests.codes.ok:
         res.raise_for_status()

      root = ET.fromstring(res.text)
      teams = root.findall('team')
      for team in teams:
         for player in team.findall('player'):
            player.get('boxname')

def buildAppContent(date):
   content = []
   getGames(content, date)
   getPitchAndAvgData(content)

   return content
