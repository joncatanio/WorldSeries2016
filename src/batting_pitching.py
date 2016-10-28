import requests, json
import xml.etree.ElementTree as ET
from decimal import *
from thresholds_globals import *

MONTH_BAT_AVG_THRESHOLD = .300
MONTH_HR_THRESHOLD = 5

# Called by getPitchAndAvgData to determine if a player is very good against a pitcher
def playerVsPitcher(content, game, team, player, pitcher):
   res = requests.get(mlbLookupEndpoint + '/json/named.stats_batter_vs_pitcher_composed.bam?sport_code=\'mlb\'&game_type=\'R\'&player_id=\'' + player.get('id') + '\'&pitcher_id=\'' + pitcher.get('id') + '\'')
   if res.status_code != requests.codes.ok:
      res.raise_for_status()

   obj = res.json()
   info = obj['stats_batter_vs_pitcher_composed']['stats_batter_vs_pitcher_total']['queryResults']['row']

   if info['ab'] == '' or int(info['ab']) < 5:
      return None

   getcontext().prec = 3
   if int(info['ab']) >= 20:
      if Decimal(info['avg']) > Decimal('.290'):
         if team.get('id') == game['home']:
            game['rank_factors']['home'].append({
               'title': 'You\'re My Favorite',
               'verbiage': info['player_first_last_html'] + ' is batting ' + info['avg'] + ', in ' + info['ab'] + ' at bats, against ' + info['pitcher_first_last_html'] + '.'
            })
         else:
            game['rank_factors']['away'].append({
               'title': 'You\'re My Favorite',
               'verbiage': info['player_first_last_html'] + ' is batting ' + info['avg'] + ', in ' + info['ab'] + ' at bats, against ' + info['pitcher_first_last_html'] + '.'
            })
   elif int(info['ab']) >= 10:
      if Decimal(info['avg']) > Decimal('.300'):
         if team.get('id') == game['home']:
            game['rank_factors']['home'].append({
               'title': 'You\'re My Favorite',
               'verbiage': info['player_first_last_html'] + ' is batting ' + info['avg'] + ', in ' + info['ab'] + ' at bats, against ' + info['pitcher_first_last_html'] + '.'
            })
         else:
            game['rank_factors']['away'].append({
               'title': 'You\'re My Favorite',
               'verbiage': info['player_first_last_html'] + ' is batting ' + info['avg'] + ', in ' + info['ab'] + ' at bats, against ' + info['pitcher_first_last_html'] + '.'
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

def pitcherHeadToHead(game, homeP, awayP):
   getcontext().prec = 2
   homeEra = Decimal(homeP.get('era'))
   awayEra = Decimal(awayP.get('era'))
   homeWL = int(homeP.get('wins')) + int(homeP.get('losses'))
   awayWL = int(awayP.get('wins')) + int(awayP.get('losses'))
   duel = False

   if homeWL >= 2:
      if homeEra < Decimal('2.20'):
         duel = True
         game['rank_factors']['home'].append({
            'title': 'Low ERA Pitcher',
            'verbiage': homeP.get('first') + ' ' + homeP.get('last') + ' has a ' + str(homeEra) + ' ERA'
         })
   if awayWL >= 2:
      if awayEra < Decimal('2.20'):
         game['rank_factors']['away'].append({
            'title': 'Low ERA Pitcher',
            'verbiage': awayP.get('first') + ' ' + awayP.get('last') + ' has a ' + str(awayEra) + ' ERA'
         })
         if duel:
            game['taglines'].append('Pitcher\'s Duel')

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

      pitcherHeadToHead(game, homeP, awayP)
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
                  # Find Past 5 Game Stats
                  getPastFiveGamesData(player.get('id'), team.get('type'), game)
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

def getPastFiveGamesData (playerID, playerTeam, game):
   playerStats = requests.get(mlbEndpoint + game['game_data_dir'] + '/batters/' + playerID + '.xml')

   if playerStats.status_code != requests.codes.ok:
      playerStats.raise_for_status()

   root = ET.fromstring(playerStats.text)
   month = root.find('month')

   firstName = root.get('first_name')
   lastName = root.get('last_name')
   monthBatAVG = month.get('avg')
   monthHRs = month.get('hr')

   if float(monthBatAVG) >= MONTH_BAT_AVG_THRESHOLD and int(monthHRs) >= MONTH_HR_THRESHOLD:
      game['rank_factors'][playerTeam].append({
         'title': 'Good Month',
         'verbiage' : firstName + ' ' + lastName + ' batted ' + monthBatAVG + ' and has hit '
            + monthHRs + ' homeruns in the last month'
      })
   elif float(monthBatAVG) >= MONTH_BAT_AVG_THRESHOLD:
      game['rank_factors'][playerTeam].append({
         'title': 'Good Month',
         'verbiage' : firstName + ' '  + lastName + ' batted ' + monthBatAVG + ' in the last month' 
      }) 
   elif int(monthHRs) >= MONTH_HR_THRESHOLD:
      game['rank_factors'][playerTeam].append({
         'title': 'Good Month',
         'verbiage' : firstName + ' '  + lastName + ' has hit ' + monthHRs + ' homeruns in the last month' 
      }) 
