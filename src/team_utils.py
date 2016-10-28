def fillTaglines(content):
   for game in content:
      if not game['taglines']:
         maxFactor = None
         factorList = game['rank_factors']['home'] + game['rank_factors']['away']
         for factor in factorList:
            if maxFactor == None:
               maxFactor = factor
            else:
               if maxFactor['rank'] < factor['rank']:
                  maxFactor = factor

         if maxFactor != None:
            game['taglines'].append(maxFactor['title'])
