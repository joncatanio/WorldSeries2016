import requests
import xml.etree.ElementTree as ET
from thresholds_globals import *

WIN_STREAK = 2
LOSE_STREAK = 4

def getWinLoseStreak(content, date):  
   standingsNL = requests.get(mlbLookupEndpoint + '/named.standings_all.bam?sit_code=\'h0\'' + \
      '&league_id=\'104\'&season=\'' + date.strftime('%Y') + '\'')
   if standingsNL != requests.codes.ok:
      standingsNL.raise_for_status()
   
   standingsAL = requests.get(mlbLookupEndpoint + '/named.standings_all.bam?sit_code=\'h0\'' + \
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
