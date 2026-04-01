Aggregating Festivals for the database
    1. Perform a monthly aggregation of festivals from EDMTRAIN
        Festivals are posted to EDM Train in the format:
            Name: Coachella Weekend 1 | Date: 2026-04-10 | Location: Indio, CA
            Name: Coachella Weekend 1 | Date: 2026-04-11 | Location: Indio, CA
            Name: Coachella Weekend 1 | Date: 2026-04-12 | Location: Indio, CA
            So in order to track multi-day festivals, we must execute the following logic:
                First Check if the Name String is in the database
                If it isn't, add it to the database and initialize the starting date and ending date as the date provided
                If the new date is later than the current end date, update the ending date, but if its earlier, set it to the new date
                On a second pass, some artists may be duplicated so only add new artists into the jsonb artists collumn.
                Use the the EDMTRAIN API key values to fill in the festivals database, but check if NULL before doing so: 
                    name(text): name
                    start_date(date): date
                    end_date(date): date
                    lat(float8): venue['latitude'] 
                    lng(float8): venue['longitude']
                    location(text): "venue['city'], venue['state'], venue['country']"
                    state(text): venue['state']
                    city(text): venue['city']
                    country(text): venue['country']
                IF the festival has a non null lineup, we must process all of the artists in the lineup
                Once all the artists in the lineup have been processed, we add their uuids to the artist_id column of the event_artists table and the uuid of the festival to the event_id column of the event_artists table.
                After a lineup has been processed, we recalculate the festival's genre_id column by taking the mode of all the genres of the artists in the lineup the same way as in festival_aggregator.py. Then we also recalcualte the festival's sonic_dna the same way as in festival_aggregator.py. After all this has been done we can move onto the next festival.

Unprocessible names:
    If a name is not found in Last.fm then dont add it.
    If a name has the format: "NAME1 (NAME2 & NAME3)" then we must only process NAME2 & NAME3.
        For example the name "SUBJOHNICS (Subtronics & John Summit)" could not be resolved on Last.fm, but "Subtronics & John Summit" could be.
    


                    
CURRENT PLAN:
    MUST REFACTOR FESTIVALS TABLE ID(int8) to UUID
                
        Festivals are aggregated for the next 12 months
    2. While innactive, allow moltbot to scan:
        1. X.com accounts
        2. EDM blogs (unsure how to do this)
Finding the Data (Location, Size, Dates, Lineup)
    1. EDM Train festivals
        EDM Train Festivals have (Names, Dates, Location)
        EDM Train Festivals DONT have (Lineup, ticket_links, coordinates)
        EDM Train festivals 

Problems: 
    1. Festivals may be announced on different platforms.
    2. Festivals may be announced with a partial lineup
    3. Festivals may be canceled all together
    4. Festivals may be rescheduled
    5. Artists may be announced after the initial lineup
    6. EDM Train may not have all festivals

