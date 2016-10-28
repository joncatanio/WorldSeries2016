from thresholds_globals import *

rivalryFactor = {
   'ATL': ['NYM', 'WSH'],
   'ARI': ['LAD', 'CHC'],
   'BAL': ['NYY', 'WSH'],
   'BOS': ['NYY', 'TB'],
   'CHC': ['STL', 'CWS'],
   'CWS': ['CHC', 'MIN'],
   'CIN': ['STL', 'CLE'],
   'CLE': ['DET', 'NYY'],
   'COL': ['LAD', 'ARI'],
   'DET': ['CLE', 'CWS'],
   'HOU': ['TEX', 'OAK'],
   'KC' : ['STL', 'DET'],
   'LAA': ['LAD', 'OAK'],
   'LAD': ['SF', 'LAA'],
   'MIA': ['ATL', 'NYM'],
   'MIL': ['CHC', 'STL'],
   'MIN': ['NYY', 'CWS'],
   'NYM': ['NYY', 'PHI'],
   'NYY': ['BOS', 'NYM'],
   'OAK': ['SF', 'LAA'],
   'PHI': ['NYM', 'ATL'],
   'PIT': ['STL', 'PHI'],
   'STL': ['CHC', 'CIN'],
   'SD' : ['LAD', 'ARI'],
   'SF' : ['LAD', 'OAK'],
   'SEA': ['OAK', 'TEX'],
   'TB' : ['NYY', 'BOS'],
   'TEX': ['LAA', 'HOU'],
   'TOR': ['NYY', 'BOS'],
   'WSH': ['BAL', 'ATL'] 
}

def getRivalries(content):
   for game in content:
      homeTeam = game['home']
      homeName = game['home_name']
      awayTeam = game['away']
      awayName = game['away_name']

      getRivalryTagline(homeTeam, awayTeam, game)

      if awayTeam in rivalryFactor[homeTeam]:
         game['rank_factors']['home'].append({
            'title': 'Rivalry Game',
            'verbiage': 'The ' + homeName + ' are rivals with the ' + awayName,
            'rank' : '4'
         })
         if 'Top Rivalry' not in game['taglines'] and 'Rivales' not in game['taglines'] and len(game['taglines']) < 3:
            game['taglines'].append('Rivales')
      if homeTeam in rivalryFactor[awayTeam]:
         game['rank_factors']['away'].append({
            'title': 'Rivalry Game',
            'verbiage': 'The ' + awayName + ' are rivals with the ' + homeName,
            'rank' : '4'
         })
         if 'Top Rivalry' not in game['taglines'] and 'Rivales' not in game['taglines'] and len(game['taglines']) < 3:
            game['taglines'].append('Rivales')

def getRivalryTagline(homeTeam, awayTeam, game):
   if homeTeam == rivalryFactor[awayTeam][0] and awayTeam == rivalryFactor[homeTeam][0]:
      game['taglines'].append('Top Rivalry')  
   elif homeTeam in rivalryFactor[awayTeam] and awayTeam in rivalryFactor[homeTeam]:
      game['taglines'].append('Rivalry')

      
