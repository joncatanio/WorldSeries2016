# WorldSeries2016
MLBAM Hackathon of Champions

This is the engine we created to call MLB's APIs and gather data for each game
every day. Since we aren't MLB insiders we are only allowed exposure to their
API and not their databases so we had to do a lot of XML/JSON parsing and data
calculations that could have been done much more efficiently using SQL or
something similar. Another option would have been to scrape as much data
as we could from MLB's APIs and load them into our own database but due to the
time constraints of a hackathon we decided we would take the performance hit
and simply have this run every day in the morning and save a pretty small
JSON array to a flat file and serve that up from our own REST endpoint.

See the WorldSeries2016_API repository for a bit more information on that.

By: Jon Catanio, Giancarlo Tarantino
