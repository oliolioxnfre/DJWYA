To do:
Finish classifer table of genres
    Add like 40 more genres
    Tweak each one
    Make each ones vibe more extreme to skew graph
Add multiple users to Database
    Add playlist logic and playlist removal logic to the app and DB
Add compare.py logic ultimate score 
    Add the "Master Tally" Algorithm

Find a way to automate festival playlists
    Idea 1: Manually Scrape playlists 💩
    Idea 2: Use EDMTRAIN api to give moltbot instructions of which playlists to scrape
    Idea 3: Use EDMTRAIN api to find festivals and then use moltbot to scrape each poster

Website:
    Make Landing page ✅
    Make signin ✅
    Make upload csv ✅
    Dashboard
        Add SonicDNA: radar chart/starchart
    Festivals page:
        Festival Card:
            Analytics:
                Add SonicDNA: chart/starchart sync visual
                Add Visual on expansion
                Add Multi day festival intelligence
                Add Star power
                Show Genres better
            Buttons:
                Add to list button
                Add buy ticket button
        General:
            Add randomizer button
            Add festival search bar
            Add Region Filter On region click
            Node Color = Festival Type
                green = outdoor
                blue = indoor
                
    Settings:
        Username Changing
        PFP Changing
        Special Settings
            Cursor Tracers
            Font changes
            Radar - Star chart toggle
            Click Fireworks
            Idle animations
    Graph page
        General:
            Fix the relationships
            Adjust arrows
            Redo Descriptions over an LLM
            MAYBE remove weights from influences
            Fix legend spacings
        Visual:
            Add some background jfx effects (glow, blur, sand, ripple?)
            Slected node vibrates lines around it.
            Make all root genres bigger
            Redo root genre coloring
            Make all text lighter hue
            change node border color
            Change root colors
            Make Root nodes have the stronger weights
        Special Feature:
            Add Sonic DNA reccomendation feature: User Selects points on the star
            Add genre reccomendation function: User selects A 2 existing vibes and searches for a genre with inbetween
            This will take any two or 3 genres that you like and find you a new genre to get into It will highlight the closest path from the selected genres to the selected genre
            Size the nodes by Popularity
            Size the nodes by a user's intrest
    Artist Page:
        Make a page for each artist
        Democratize the genres of the artist
        Add artist DNA and analytics
        Display events the artist is going to play at
    About Page:
        Rationale of the project
        Opensource tools used in the project
        Future plans
        Contact information
        Buy me a glowstick ⚡️
            BTC, ETH, ADA, SOL, USDC, USDCx, Paypal


Backend:
    Fix genre aliases
    Fix genre classifier
    Festival Genres should not be in festival table
        Relate festival genres to artist genres (democracy)


Mobile:
    Redesign EVERYTHING for mobile.





SQLStuff
    SQLtools extension for vscode
    pgcron: schedule sql jobs
    pgai 
    pgvectors: Store DNA in vectors
        Query nearest vectors based on l2 distance
    tsvectors:
        searching for shit

    electricsql sync layer for supabase
    pg_graphql
    pg_crypto
    pgjwt (pg json web token)
