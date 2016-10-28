import requests, json
import xml.etree.ElementTree as ET
from xml.dom.minidom import parse, parseString

mlbEndpoint = 'http://gd.mlb.com'
WIN_STREAK = 2
LOSE_STREAK = 4

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

def getWinLoseStreak(content, date):  
   standingsNL = requests.get('http://mlb.mlb.com/lookup/named.standings_all.bam?sit_code=\'h0\'' + \
      '&league_id=\'104\'&season=\'' + date.strftime('%Y') + '\'')
   if standingsNL != requests.codes.ok:
      standingsNL.raise_for_status()
   
   standingsAL = requests.get('http://mlb.mlb.com/lookup/named.standings_all.bam?sit_code=\'h0\'' + \
      '&league_id=\'103\'&season=\'' + date.strftime('%Y') + '\'')
   if standingsAL != requests.codes.ok:
      standingsAL.raise_for_status()

   for game in content:
      homeID = game['home_id']
      awayID = game['away_id']
      
      streaks = getStreak(homeID, awayID, standingsNL, standingsAL, content)
     
      homeStreakType = streaks[0][0]
      awayStreakType = streaks[1][0]
      homeStreakNum = streaks[0][-1]
      awayStreakNum = streaks[1][-1]
      
      isStreak(homeStreakType, homeStreakNum, awayStreakType, awayStreakNum, game)
 
   return content

def isStreak(homeStreakType, homeStreakNum, awayStreakType, awayStreakNum, game):
      if homeStreakType == 'W':
         if int(homeStreakNum) >= WIN_STREAK:
            game['rank_factors']['home'].append(
               {'title': 'streak',
                'verbiage': game['home'] + ' has a winning streak of ' + homeStreakNum + ', will it continue?!'}
               )
      else:
         if int(homeStreakNum) >= LOSE_STREAK:
            game['rank_factors']['home'].append(
               {'title': 'streak',
                'verbiage': game['home'] + ' has a losing streak of ' + homeStreakNum + ', will they break it?'}
               )

      if awayStreakType == 'W':
         if int(awayStreakNum) >= WIN_STREAK:
            game['rank_factors']['away'].append(
               {'title': 'streak',
                'verbiage': game['away'] + ' has a winning streak of ' + awayStreakNum + ', will it continue?!'}
               )
      else: 
         if int(awayStreakNum) >= LOSE_STREAK:
            game['rank_factors']['away'].append(
               {'title': 'streak',
                'verbiage': game['away'] + ' has a losing streak of ' + awayStreakNum + ', will they break it?'}
               )
 
def getStreak(homeID, awayID, standingsNL, standingsAL, content):
   rootNL = ET.fromstring(standingsNL.text)
   rootAL = ET.fromstring(standingsAL.text)
   resultsNL = rootNL.find('queryResults')
   resultsAL = rootAL.find('queryResults')
   teamsNL = resultsNL.findall('row')
   teamsAL = resultsAL.findall('row')
   streakHome = '';
   streakAway = '';

   if isTeamInLeague(homeID, teamsNL):
      for team in teamsNL:
         if homeID == team.get('team_id'):
            streakHome = team.get('streak')
   else:
      for team in teamsAL:
         if homeID == team.get('team_id'):
            streakHome = team.get('streak')

   if isTeamInLeague(awayID, teamsAL):
      for team in teamsAL:
         if awayID == team.get('team_id'):
            streakAway = team.get('streak')

   else:
      for team in teamsNL:
         if awayID == team.get('team_id'):
            streakAway = team.get('streak')

   return (streakHome, streakAway)

def isTeamInLeague(teamID, league):
   for team in league:
      if teamID == team.get('team_id'):
         return True
   return False

def buildAppContent(date):
   content = []
   getGames(content, date)
   getWinLoseStreak(content, date)
   getPitchAndAvgData(content)

   return content
