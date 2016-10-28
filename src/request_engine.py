import requests, json
import xml.etree.ElementTree as ET
from team_streaks import getWinLoseStreak
from batting_pitching import getPitchAndAvgData
from thresholds_globals import *

def getGames(content, date):
   res = requests.get(mlbEndpoint + '/components/game/mlb/year_' + date.strftime('%Y') + '/month_' + date.strftime('%m') + '/day_' + date.strftime('%d') + '/master_scoreboard.json')
   if res.status_code != requests.codes.ok:
      res.raise_for_status()

   jsonRes = res.json()
   jsonGames = jsonRes['data']['games']

   for obj in jsonGames['game']:
      content.append({ 'home': obj['home_name_abbrev'], 'away': obj['away_name_abbrev'],
                     'home_id': obj['home_team_id'], 'away_id': obj['away_team_id'],
                     'game_data_dir': obj['game_data_directory'],
                     'home_name': obj['home_team_name'], 'away_name': obj['away_team_name'],
                     'rank_factors': { 'home': [], 'away': []}, 'est_time': obj['time'],
                     'home_win': obj['home_win'], 'home_loss': obj['home_loss'],
                     'away_win': obj['away_win'], 'away_loss': obj['away_loss'],
                     'taglines': []})


def buildAppContent(date):
   content = []
   getGames(content, date)
   getWinLoseStreak(content, date)
   getPitchAndAvgData(content)

   return content
