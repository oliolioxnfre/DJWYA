# DJWYA
Small Spotify based web app designed to scour the inet for festivals featuring your favorite DJs.

Install the dependencies
supabase pylast spotipy python-dotenv

Notes to self: source bin/activate, ./bin/pip install -r requirements.txt

To add:
Context (complextro.csv) (Mewnlight Rose)
1) For starters gotta fix the my main CSV filing loop. Theres a massive technical bug that is causing failures in artist lookups to LAST.FM causing a default fallback to the genres in the playlist CSV. For example, Mewnlight Rose is auto fallbacking to the csv file's genre "happy hardcore" 
2) Even though artists like Mewnlight Rose are categorized as "happy hardcore" in the csv" the database filing loop specfically the DNA mapping is mapping the incorrect DNA rankings for HAPPY HARDCORE.

Exemplified) Mewnlight Rose is (electro house, happy hardcore, uk hardcore, dubstep, colour bass) on LAST.FM -> Database Mewnlight Rose is (happy hardcore)
happy hardcore is listed in the classifier as 
{'intensity': 8, 'euphoria': 10,'space': 5, 'pulse': 9, 'chaos': 4, 'swing': 3},
but in the DB is mapped as 
{"chaos": 4.8, "pulse": 8.2, "space": 4.5, "swing": 4.8, "euphoria": 5.5, "intensity": 6.8}