import requests
import xml.etree.ElementTree as ET
from thresholds_globals import *

MONTH_THRESHOLD = 7
GB_THRESHOLD = 2.0
WILDCARD_GB_THRESHOLD = 2.0

def getStandingsComparison(content):
   for game in content:
      if int(game['month']) > MONTH_THRESHOLD:
         homeName = game['home_name']
         awayName = game['away_name']

         homeGB = convertToFloat(game['home_games_back'])
         awayGB = convertToFloat(game['away_games_back'])         
         homeGB_wildcard = convertToFloat(game['home_games_back_wildcard'])
         awayGB_wildcard = convertToFloat(game['away_games_back_wildcard'])
         back = ''

         if homeGB != '-' and homeGB != '' and homeGB < GB_THRESHOLD:
            if homeGB == 1.0:
               back = ' game back'
            else:
               back = ' games back'
            game['rank_factors']['home'].append({
               'title': 'Closing In',
               'verbiage': 'The ' + homeName + ' are currently ' + str(homeGB) + back
            })
         
         if awayGB != '-' and awayGB != '' and awayGB < GB_THRESHOLD:
            if awayGB == 1.0:
               back = ' game back'
            else:
               back = ' games back'
            game['rank_factors']['away'].append({
               'title': 'Closing In',
               'verbiage': 'The ' + homeName + ' are currently ' + str(awayGB) +back
            })
         if homeGB_wildcard != '-' and homeGB_wildcard != '' and homeGB_wildcard < GB_THRESHOLD:
            if homeGB_wildcard == 1.0:
               back = ' game back'
            else:
               back = ' games back'
            game['rank_factors']['home'].append({
               'title': 'Postseason Potential',
               'verbiage': 'The ' + homeName + ' are ' + str(homeGB_wildcard) + back + ' from a wildcard spot'
            })
         if awayGB_wildcard != '-' and awayGB_wildcard != '' and awayGB_wildcard < GB_THRESHOLD:
            if awayGB_wildcard == 1.0:
               back = ' game back'
            else:
               back = ' games back'
            game['rank_factors']['away'].append({
               'title': 'Postseason Potential',
               'verbiage': 'The ' + homeName + ' are ' + str(awayGB_wildcard) + back + ' from a wildcard spot'
            })


def convertToFloat(data):
   if data != '-' and data != '':
      if data[0] == '+':
         return '-'
      else:
         return float(data)
   else:
      return data
