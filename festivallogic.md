Aggregating Festivals for the database
    1. Perform a monthly aggregation of festivals from EDMTRAIN
        Festivals are posted to EDM Train in the format:
            Name: Coachella Weekend 1 | Date: 2026-04-10 | Location: Indio, CA
            Name: Coachella Weekend 1 | Date: 2026-04-11 | Location: Indio, CA
            Name: Coachella Weekend 1 | Date: 2026-04-12 | Location: Indio, CA
            So in order to track multi-day festivals, we must execute the following logic:
                First Check if the Name String is in the database
                If it isn't, add it to the database and initialize the starting date and ending date as the date provided
                If it is, update the ending date to the date provided by the second listing
                
                
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

