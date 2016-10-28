import requests, json
import xml.etree.ElementTree as ET
from decimal import *
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
                     'game_data_dir': obj['game_data_directory'],
                     'home_name': obj['home_team_name'], 'away_name': obj['away_team_name'],
                     'rank_factors': { 'home': [], 'away': []}, 'est_time': obj['time']})

# Called by getPitchAndAvgData to determine if a player is very good against a pitcher
def playerVsPitcher(content, game, team, player, pitcher):
   res = requests.get('http://mlb.mlb.com/lookup/json/named.stats_batter_vs_pitcher_composed.bam?sport_code=\'mlb\'&game_type=\'R\'&player_id=\'' + player.get('id') + '\'&pitcher_id=\'' + pitcher.get('id') + '\'')
   if res.status_code != requests.codes.ok:
      res.raise_for_status()

   obj = res.json()
   info = obj['stats_batter_vs_pitcher_composed']['stats_batter_vs_pitcher_total']['queryResults']['row']

   if info['ab'] == '' or int(info['ab']) < 5:
      return None

   getcontext().prec = 3
   if int(info['ab']) >= 20:
      if Decimal(info['avg']) > Decimal('.350'):
         if team.get('id') == game['home']:
            game['rank_factors']['home'].append({
               'title': 'You\'re My Favorite',
               'verbiage': info['player_first_last_html'] + ' is batting ' + info['avg'] + ' against today\'s pitcher.'
            })
         else:
            game['rank_factors']['away'].append({
               'title': 'You\'re My Favorite',
               'verbiage': info['player_first_last_html'] + ' is batting ' + info['avg'] + ' against today\'s pitcher.'
            })

   return Decimal(info['avg'])

def teamAvgThisYear(game, team, avg):
   teamAvg = Decimal(avg) / Decimal(9)
   if teamAvg > Decimal('0.300'):
      if team.get('id') == game['home']:
         game['rank_factors']['home'].append({
            'title': 'High Average!',
            'verbiage': 'The ' + game['home_name'] + ' have a batting average of ' + str(teamAvg)
         })
      else:
         game['rank_factors']['away'].append({
            'title': 'High Average!',
            'verbiage': 'The ' + game['away_name'] + ' have a batting average of ' + str(teamAvg)
         })

def teamAverageVsPitcher(game, team, faced, avgAgainstP, pitcher):
   if faced > 4:
      avgAgainstP = avgAgainstP / Decimal(faced)
      if avgAgainstP < Decimal('0.150'):
         if team.get('id') == game['home']:
            game['rank_factors']['home'].append({
               'title': 'Dominant Pitcher',
               'verbiage': pitcher.get('first') + ' ' + pitcher.get('last') + ' holds the ' + game['home_name'] + ' to a team batting average of ' + str(avgAgainstP)
            })
         else:
            game['rank_factors']['away'].append({
               'title': 'Dominant Pitcher',
               'verbiage': pitcher.get('first') + ' ' + pitcher.get('last') + ' holds the ' + game['away_name'] + ' to a team batting average of ' + str(avgAgainstP)
            })
      if avgAgainstP >= Decimal('0.325'):
         if team.get('id') == game['home']:
            game['rank_factors']['home'].append({
               'title': 'Our Favorite Pitcher',
               'verbiage': 'The ' + game['home_name'] + ' are hitting ' + str(avgAgainstP) + ' against ' + pitcher.get('first') + ' ' + pitcher.get('last')
            })
         else:
            game['rank_factors']['away'].append({
               'title': 'Our Favorite Pitcher',
               'verbiage': 'The ' + game['away_name'] + ' are hitting ' + str(avgAgainstP) + ' against ' + pitcher.get('first') + ' ' + pitcher.get('last')
            })

def getPitchAndAvgData(content):
   # For adding batting averages 
   getcontext().prec = 3
   matchup = []

   for game in content:
      res = requests.get(mlbEndpoint + game['game_data_dir'] + '/players.xml')
      if res.status_code != requests.codes.ok:
         res.raise_for_status()

      root = ET.fromstring(res.text)
      teams = root.findall('team')

      awayP = None
      homeP = None
      for team in teams:
         players = team.findall('player')
         for player in players:
            if player.get('game_position') == 'P':
               if team.get('type') == 'away':
                  awayP = player
               else:
                  homeP = player

      game['away_pitcher'] = awayP.get('first') + ' ' + awayP.get('last')
      game['home_pitcher'] = homeP.get('first') + ' ' + homeP.get('last')

      for team in teams:
         players = team.findall('player')
         avg = Decimal('0.0')
         avgAgainstP = Decimal('0.0')
         pitcherAvg = Decimal('0.0')
         starters = 0
         faced = 0

         # Find the pitcher for playerVsPitcher()
         pitcher = None
         if team.get('type') == 'away':
            pitcher = homeP
         else:
            pitcher = awayP

         for player in players:
            pos = player.get('game_position')
            starters += 1  

            if pos != None:
               if pos == 'P':
                  pitcherAvg = Decimal(player.get('avg'))
               else:
                  # The player is a starter (non-pitcher)
                  tempAvg = playerVsPitcher(content, game, team, player, pitcher)
                  if tempAvg != None:
                     avgAgainstP += tempAvg
                     faced += 1

                  avg += Decimal(player.get('avg'))

         # Team average overall (on the season)
         if starters == 9:
            avg += pitcherAvg
         teamAvgThisYear(game, team, avg)

         # Team average vs pitcher
         teamAverageVsPitcher(game, team, faced, avgAgainstP, pitcher)

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
               {'title': 'Winning Streak',
                'verbiage': 'The ' + game['home_name'] + ' have a winning streak of ' + homeStreakNum + ', will it continue?!'}
               )
      else:
         if int(homeStreakNum) >= LOSE_STREAK:
            game['rank_factors']['home'].append(
               {'title': 'Losing Streak',
                'verbiage': 'The ' + game['home_name'] + ' have a losing streak of ' + homeStreakNum + ', will they break it?'}
               )

      if awayStreakType == 'W':
         if int(awayStreakNum) >= WIN_STREAK:
            game['rank_factors']['away'].append(
               {'title': 'Winning Streak',
                'verbiage': 'The ' + game['away_name'] + ' have a winning streak of ' + awayStreakNum + ', will it continue?!'}
               )
      else: 
         if int(awayStreakNum) >= LOSE_STREAK:
            game['rank_factors']['away'].append(
               {'title': 'Losing Streak',
                'verbiage': 'The ' + game['away_name'] + ' have a losing streak of ' + awayStreakNum + ', will they break it?'}
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
