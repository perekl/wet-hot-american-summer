"""Master cue list for Wet Hot American Summer table read. Source: screenplay PDF."""

def cue(cid, page, scene, trigger, name, category, priority="Medium",
        duration="", loop="No", fade="None", volume="75", notes=""):
    return {
        "Cue ID": cid, "Script Page": page, "Scene": scene,
        "Trigger Dialogue": trigger, "Cue Name": name, "Category": category,
        "Priority": priority, "Duration": duration, "Loop": loop,
        "Fade": fade, "Volume": volume, "Notes": notes,
    }

CUES = [
    # PAGE 1
    cue("CUE-001", 1, "TITLE CARD", "Screenplay opens", "Pre-show Silence / House Lights", "Silence", "Critical", "5s", "No", "In", "0", "Hold black before titles."),
    # PAGE 2
    cue("CUE-002", 2, "OPENING TITLES", '"Jane" by Jefferson Starship begins with opening TITLES over black', "Jane (Jefferson Starship) - Opening Titles", "Music", "Critical", "Full song excerpt", "No", "In", "85", "Licensed. Fade under first scene."),
    cue("CUE-003", 2, "EXT. CAMPFIRE SITE - NIGHT", "CUT TO: EXT. CAMPFIRE SITE - NIGHT", "Scene Transition Stinger", "Transition", "High", "2s", "No", "None", "70", "Cut from black to campfire."),
    cue("CUE-004", 2, "EXT. CAMPFIRE SITE - NIGHT", "Music KICKS IN.", "Campfire Night Ambience", "Ambience", "High", "Loop", "Yes", "In", "60", "Crackling fire, distant crickets, counselors murmuring."),
    cue("CUE-005", 2, "EXT. CAMPFIRE SITE - NIGHT", "counselors dance and play guitar", "Acoustic Guitar Strumming (Diegetic)", "Ambience", "Medium", "Loop", "Yes", "In", "45", "Under Jane or post-title music."),
    cue("CUE-006", 2, "EXT. CAMPFIRE SITE - NIGHT", "TITLE: AUGUST 18, 1981", "Title Card Whoosh (Optional)", "Transition", "Optional", "1s", "No", "None", "55", "Comedy enhancement for date stamp."),
    cue("CUE-007", 2, "EXT. CAMPFIRE SITE - NIGHT", "MUSIC / TITLES CONTINUE", "Jane / Title Music Continue", "Music", "Critical", "Loop", "Yes", "None", "80", "Maintain through dawn montage."),
    cue("CUE-008", 2, "EXT. VARIOUS - DAWN", "The sun rises on a serene lake", "Dawn Lake Ambience", "Ambience", "High", "Loop", "Yes", "Crossfade", "55", "Birds, gentle water, rural New England morning."),
    cue("CUE-009", 2, "EXT. VARIOUS - DAWN", "GROUNDSKEEPER peels and eats a banana", "Banana Peel / Eating SFX", "SFX", "High", "3s", "No", "None", "70", "Comedy sound dissolves into next scene."),
    cue("CUE-010", 2, "INT. KATIE'S BUNK - DAWN", "banana-like sound of MAKING OUT", "Smooching / Making Out SFX", "SFX", "High", "Loop", "Yes", "In", "50", "Exaggerated comedy smooch layer."),
    cue("CUE-011", 2, "INT. KATIE'S BUNK - DAWN", "BUNK BOY emerges from under blanket", "Bunk Rustle / Blanket Movement", "SFX", "Medium", "2s", "No", "None", "55", ""),
    cue("CUE-012", 2, "INT. KATIE'S BUNK - DAWN", "They flip up their goods and DASH out", "Running Footsteps - Bunk Exit", "SFX", "Medium", "4s", "No", "Out", "65", ""),
    cue("CUE-013", 2, "EXT. KATIE'S BUNK - DAWN", "Music and credits continue.", "Title Music Continue", "Music", "High", "Loop", "Yes", "None", "75", ""),
    # PAGE 3
    cue("CUE-014", 3, "EXT. MAIN FIELD - DAWN", "Hundreds of sweat suited campers scurry about", "Camp Morning Bustle Ambience", "Ambience", "High", "Loop", "Yes", "In", "60", "Footsteps, whispers, hurried movement."),
    cue("CUE-015", 3, "INT. COOP'S BUNK - DAWN", 'CAMPERS singing "Standing in the rain"', "Campers Acapella Rock Snippet", "Music", "Medium", "15s", "No", "In", "50", "Diegetic camper singing, not full track."),
    cue("CUE-016", 3, "INT. COOP'S BUNK - DAWN", "campers SCREAM, jump on top of Coop", "Kids Scream / Pile-On SFX", "SFX", "High", "5s", "No", "None", "75", "Badminton rackets and whiffle bats."),
    cue("CUE-017", 3, "INT. COOP'S BUNK - DAWN", "banging their feet and air-guitaring", "Racket / Bat Air-Guitar Bangs", "SFX", "Medium", "4s", "No", "None", "60", ""),
    # PAGE 4
    cue("CUE-018", 4, "EXT. COOP'S BUNK - DAWN", "we hear the voice-over of ARTY", "Camp Radio Static / Bed", "Ambience", "High", "Loop", "Yes", "In", "40", "Under Arty V.O. - WCFW radio."),
    cue("CUE-019", 4, "EXT. COOP'S BUNK - DAWN", "Good morning everybody", "Radio VO Filter (Optional)", "SFX", "Optional", "Loop", "Yes", "None", "35", "Light AM radio EQ on table read if desired."),
    # PAGE 5
    cue("CUE-020", 5, "EXT. FLAGPOLE - DAWN", "Moose silently raises the flag", "Flagpole Rope / Fabric SFX", "SFX", "Low", "3s", "No", "None", "45", ""),
    cue("CUE-021", 5, "EXT. FLAGPOLE - DAWN", "French kiss grossly", "Comedy Smooch Stinger", "Comedy", "Optional", "2s", "No", "None", "50", ""),
    # PAGE 6-7 - dialogue heavy, light ambience
    cue("CUE-022", 6, "EXT. FLAGPOLE - DAWN", "Coop and Katie banter continues", "Flagpole Crowd Ambience", "Ambience", "Low", "Loop", "Yes", "None", "35", "Distant camp assembly murmur."),
    cue("CUE-023", 7, "EXT. PROFESSOR'S COTTAGE - MORNING", "Beth approaches Professor", "Garden Morning Ambience", "Ambience", "Low", "Loop", "Yes", "In", "40", "Birds, light breeze."),
    cue("CUE-024", 7, "EXT. PROFESSOR'S COTTAGE - MORNING", "trowel flies off leaving handle", "Tool Clatter SFX", "SFX", "Medium", "2s", "No", "None", "65", ""),
    # PAGE 8-9
    cue("CUE-025", 8, "EXT. PROFESSOR'S COTTAGE - MORNING", "Henry leans on flower pot, fist sinks", "Mud / Pot Squish SFX", "SFX", "Medium", "2s", "No", "None", "55", ""),
    cue("CUE-026", 9, "INT. MESS HALL - SERVING AREA - MORNING", "noisy cacophony of a hundred hungry kids", "Mess Hall Breakfast Crowd", "Ambience", "High", "Loop", "Yes", "In", "65", ""),
    cue("CUE-027", 9, "INT. MESS HALL - SERVING AREA - MORNING", "I SAID NO!!!", "Awkward Silence Beat", "Silence", "Medium", "3s", "No", "Out", "0", "Drop crowd bed after Professor snaps."),
    # PAGE 10-11
    cue("CUE-028", 10, "INT. MESS HALL - MORNING", "GARY! BRING OUT THE TATERS!", "Kitchen Call-Out Echo", "SFX", "Low", "2s", "No", "None", "60", ""),
    cue("CUE-029", 11, "INT. MESS HALL - MORNING", "Caped Boy addresses girls", "Mess Hall Ambience Continue", "Ambience", "Medium", "Loop", "Yes", "None", "50", ""),
    cue("CUE-030", 11, "INT. MESS HALL - MORNING", "He gets no response", "Comedy Crickets (Optional)", "Comedy", "Optional", "3s", "No", "None", "40", ""),
    # PAGE 12-13
    cue("CUE-031", 12, "INT. MESS HALL - MORNING", "Gene drops fried eggs platter with thud", "Metal Tray Thud SFX", "SFX", "Medium", "1s", "No", "None", "70", ""),
    cue("CUE-032", 13, "INT. MESS HALL (KITCHEN) - MORNING", "Gene and Gary argue", "Kitchen Backroom Ambience", "Ambience", "Low", "Loop", "Yes", "None", "45", "Pots, distant dining noise."),
    # PAGE 14-15
    cue("CUE-033", 14, "INT. MESS HALL - MORNING", "musical number from Godspell for talent show", "Godspell Announcement Sting (Ref)", "Music", "Low", "5s", "No", "In", "40", "Tease only; full cue at talent show."),
    cue("CUE-034", 15, "EXT. MESS HALL - MORNING", "Andy yells Hey JJ - save me a waffle", "Mess Hall Door / Exterior Ambience", "Ambience", "Low", "Loop", "Yes", "None", "40", ""),
  cue("CUE-035", 15, "EXT. MESS HALL / PARKING LOT - DAY", "Everyone leaves the mess hall", "Camp Exterior Day Ambience", "Ambience", "Medium", "Loop", "Yes", "Crossfade", "50", ""),
    # PAGE 16
    cue("CUE-036", 16, "EXT. MESS HALL / PARKING LOT - DAY", "ARTY V.O. morning activity time", "Camp Radio Bed Under VO", "Ambience", "Medium", "Loop", "Yes", "None", "40", ""),
    cue("CUE-037", 16, "EXT. MESS HALL / PARKING LOT - DAY", "Beth escorting Silas into car", "Car Door / Departure SFX", "SFX", "Medium", "4s", "No", "None", "55", ""),
    cue("CUE-038", 16, "EXT. MESS HALL / PARKING LOT - DAY", "counselors wrestle each other to ground", "Wrestling / Grunts SFX", "SFX", "Medium", "5s", "No", "None", "60", ""),
    # PAGE 17-18
    cue("CUE-039", 17, "INT. ARTS AND CRAFTS BUNK - DAY", "Gail rummaging for materials", "Arts & Crafts Room Ambience", "Ambience", "Medium", "Loop", "Yes", "In", "45", ""),
    cue("CUE-040", 17, "INT. ARTS AND CRAFTS BUNK - DAY", "Another camper screams - Where's the crayons?", "Kid Shout SFX", "SFX", "Medium", "2s", "No", "None", "65", ""),
    cue("CUE-041", 17, "INT. ARTS AND CRAFTS BUNK - DAY", "Gail BURSTS INTO TEARS", "Emotional Silence Beat", "Silence", "High", "2s", "No", "Out", "0", "Drop ambience for Gail breakdown."),
    # PAGE 18-19
    cue("CUE-042", 18, "EXT. PARKING LOT (WATERFRONT) - DAY", "long moment of silent tension. Beat.", "Tension Silence - Victor/Abby", "Silence", "High", "4s", "No", "None", "0", ""),
    cue("CUE-043", 19, "INT. RADIO STATION - MORNING", "breakfast time Rock Block", "Radio Station Room Tone", "Ambience", "Medium", "Loop", "Yes", "In", "40", "Tiny closet, fan hum."),
    cue("CUE-044", 19, "INT. RADIO STATION - MORNING", "Arty puts on headphones and turns on mic", "Mic On Click / Headphone SFX", "SFX", "Low", "1s", "No", "None", "50", ""),
    # PAGE 20-21
    cue("CUE-045", 20, "EXT. BETH'S OFFICE - DAY", "counselors on the hill", "Hill / Office Exterior Ambience", "Ambience", "Medium", "Loop", "Yes", "In", "45", ""),
    cue("CUE-046", 21, "EXT. BETH'S OFFICE - DAY", "ALL Agreed.", "Group Agreement Beat", "Silence", "Low", "2s", "No", "None", "0", "Brief pause before science scene."),
    # PAGE 22
    cue("CUE-047", 22, "INT. MESS HALL - DAY", "Andy pushes plate off table -- falls to floor", "Plate Crash SFX", "SFX", "High", "2s", "No", "None", "75", ""),
    cue("CUE-048", 22, "INT. ARTS AND CRAFTS BUNK - DAY", "Complete silence. Campers astonished.", "Arts & Crafts Dead Silence", "Silence", "Critical", "5s", "No", "Out", "0", "Hold for Aaron's line."),
    # PAGE 23-24
    cue("CUE-049", 23, "EXT. BETH'S OFFICE - DAY", "counselors applaud Beth", "Light Applause SFX", "SFX", "Medium", "3s", "No", "None", "55", ""),
    cue("CUE-050", 23, "EXT. BETH'S OFFICE - DAY", "BetaMax / China Syndrome mention", "VCR Hum (Optional Comedy)", "Comedy", "Optional", "Loop", "Yes", "None", "30", ""),
    # PAGE 25-26
    cue("CUE-051", 25, "EXT. BETH'S OFFICE - DAY", "Beth and Katie mousse conversation", "Office Porch Ambience", "Ambience", "Low", "Loop", "Yes", "None", "35", ""),
    cue("CUE-052", 26, "EXT. WATERFRONT - DAY", "floating dock, campers swim", "Lake / Waterfront Ambience", "Ambience", "High", "Loop", "Yes", "In", "55", "Splashing, distant motor."),
    # PAGE 27-29
    cue("CUE-053", 27, "EXT. WATERFRONT - DAY", "Erica zooms by in the ski boat", "Motorboat Pass-By SFX", "SFX", "High", "5s", "No", "None", "70", ""),
    cue("CUE-054", 29, "EXT. WATERFRONT - DAY", "campers whistle them on", "Wolf Whistles SFX", "SFX", "Medium", "3s", "No", "None", "55", ""),
    cue("CUE-055", 29, "EXT. WATERFRONT - DAY", "Erica falls into lake, choking", "Splash / Choking SFX", "SFX", "High", "4s", "No", "None", "70", ""),
    cue("CUE-056", 29, "EXT. WATERFRONT - DAY", "Erica DISAPPEARS under the lake", "Underwater Bubble Silence", "Silence", "High", "3s", "No", "Out", "0", "Tense beat before science scene."),
    # PAGE 30-31
    cue("CUE-057", 30, "EXT. SCIENCE CLEARING - DAY", "Beth approaches Professor", "Science Clearing Ambience", "Ambience", "Medium", "Loop", "Yes", "In", "45", ""),
    cue("CUE-058", 31, "EXT. WATERFRONT - DAY", "just sees a few bubbles, then no bubbles", "Ominous Bubble SFX", "SFX", "Medium", "3s", "No", "Out", "40", ""),
    cue("CUE-059", 31, "EXT. RURAL HIGHWAY - DAY", "VAN drives down at high speed", "Van Highway Drive Ambience", "Ambience", "High", "Loop", "Yes", "In", "60", ""),
    cue("CUE-060", 31, "EXT. RURAL HIGHWAY - DAY", "Felicia is THROWN out of the van", "Body Tumble / Road Roll SFX", "SFX", "High", "3s", "No", "None", "75", "Comedy beat."),
    # PAGE 32-33
    cue("CUE-061", 32, "EXT. PARKING AREA - DAY", "Beth drives pickup truck", "Truck Engine / Gravel SFX", "SFX", "Medium", "Loop", "Yes", "In", "55", ""),
    cue("CUE-062", 33, "EXT. WATERVILLE - VARIOUS - DAY", "TRIP TO TOWN MONTAGE: Love is Alright Tonight plays", "Love Is Alright Tonight (Rick Springfield)", "Music", "Critical", "Montage length", "No", "In/Out", "85", "Licensed. Town trip montage."),
    cue("CUE-063", 33, "EXT. WATERVILLE - VARIOUS - DAY", "library, ice cream, McDonald's", "Small Town Street Ambience", "Ambience", "Medium", "Loop", "Yes", "Under", "45", "Under montage music."),
    # PAGE 34
    cue("CUE-064", 34, "EXT. WATERVILLE - VARIOUS - DAY", "others cheer excitedly - beer", "Crowd Cheer SFX", "SFX", "Medium", "2s", "No", "None", "60", ""),
    cue("CUE-065", 34, "EXT. WATERVILLE - VARIOUS - DAY", "FADE OUT MUSIC", "Montage Music Fade Out", "Transition", "Critical", "3s", "No", "Out", "0", "End Rick Springfield montage."),
    cue("CUE-066", 34, "EXT. PARKING AREA - DAY", "pull back into parking lot", "Camp Parking Lot Return", "Ambience", "Medium", "Loop", "Yes", "In", "50", "Normal camp day resumes."),
    # PAGE 35
    cue("CUE-067", 35, "EXT. HIGHWAY 95 - DAY", "camper farts, everyone laughs", "Fart SFX + Laughter", "SFX", "High", "3s", "No", "None", "65", "Comedy."),
    cue("CUE-068", 35, "EXT. HIGHWAY 95 - DAY", "Victor floors it", "Van Engine Acceleration", "SFX", "Medium", "4s", "No", "None", "70", ""),
    # PAGE 36-37
    cue("CUE-069", 36, "EXT. BARBECUE PIT - DAY", "Gene and Gary at barbecue", "BBQ Pit Sizzle Ambience", "Ambience", "Medium", "Loop", "Yes", "In", "50", ""),
    cue("CUE-070", 37, "INT. RADIO STATION - DAY", "coitus interruptus", "Radio Booth Ambience", "Ambience", "Low", "Loop", "Yes", "None", "40", ""),
    # PAGE 38-39
    cue("CUE-071", 38, "INT. ARTS AND CRAFTS BUNK - DAY", "Gail Bursts into tears again", "Soft Crying Ambience", "Ambience", "Low", "Loop", "Yes", "In", "35", ""),
    cue("CUE-072", 39, "EXT. MOOSE RIVER CAMPSITE - DAY", "Victor screams - get out of van", "Victor Yelling / Van Doors SFX", "SFX", "High", "5s", "No", "None", "75", ""),
    cue("CUE-073", 39, "EXT. COUNTRY ROAD - DAY", "sings Danny's Song by Loggins & Messina", "Danny's Song (Loggins & Messina)", "Music", "Critical", "Verse+", "No", "In", "80", "Licensed. Victor driving."),
    cue("CUE-074", 39, "EXT. COUNTRY ROAD - DAY", "van CRASHES into a tree", "Van Crash Impact SFX", "SFX", "Critical", "4s", "No", "None", "90", "Hard cut music."),
    # PAGE 40
    cue("CUE-075", 40, "INT. ABBY'S BUNK - DAY", "Danny's Song hums from tape player", "Danny's Song (Tape Player Underscore)", "Music", "High", "Loop", "Yes", "In", "50", "Licensed, lo-fi bedroom."),
    cue("CUE-076", 40, "EXT. COUNTRY ROAD - DAY", "Victor walks barren road", "Lonely Road Wind Ambience", "Ambience", "Medium", "Loop", "Yes", "In", "45", ""),
    cue("CUE-077", 40, "INT. ABBY'S BUNK - DAY", "Abby and Gary making out", "Makeout Rustle (Low)", "SFX", "Low", "Loop", "Yes", "None", "30", ""),
    # PAGE 41-42
    cue("CUE-078", 41, "EXT. MOOSE RIVER - DAY", "campers in raft on river", "River / Raft Ambience", "Ambience", "High", "Loop", "Yes", "In", "55", "Gentle current."),
    cue("CUE-079", 41, "EXT. MOOSE RIVERBANK - DAY", "Neil jumps onto motorcycle and skids away", "Motorcycle Start / Skid SFX", "SFX", "High", "4s", "No", "None", "75", ""),
    cue("CUE-080", 42, "EXT. SMALL RURAL HIGHWAY - DAY", "Neil's motorcycle approaching", "Motorcycle Approach Loop", "SFX", "High", "Loop", "Yes", "In", "65", ""),
    cue("CUE-081", 42, "EXT. SMALL RURAL HIGHWAY - DAY", "RUNNER VS. MOTORCYCLE CHASE", "Chase Sequence Underscore", "Music", "High", "Loop", "Yes", "In", "70", "Royalty-free action/comedy."),
    cue("CUE-082", 42, "EXT. SMALL RURAL HIGHWAY - DAY", "Neil screeches to halt at hay bale", "Motorcycle Screech / Stop SFX", "SFX", "High", "2s", "No", "None", "80", ""),
    # PAGE 43-44
    cue("CUE-083", 43, "EXT. SWIMMING HOLE - DAY", "counselors skinny-dipping sneak", "Woods / Swimming Hole Ambience", "Ambience", "Medium", "Loop", "Yes", "In", "45", ""),
    cue("CUE-084", 44, "INT. EQUIPMENT SHACK - DAY", "Ben and McKinley in silence, kissing", "Shack Interior Silence", "Silence", "Medium", "3s", "No", "In", "0", "Sun through cracks."),
    cue("CUE-085", 44, "EXT. BASEBALL FIELD - DAY", "large group assembled for softball", "Ball Field Crowd Ambience", "Ambience", "High", "Loop", "Yes", "In", "55", ""),
    cue("CUE-086", 45, "EXT. BASEBALL FIELD - DAY", "Awkward silence. One camper speaks up", "Awkward Team Silence", "Silence", "High", "4s", "No", "Out", "0", ""),
    cue("CUE-087", 45, "EXT. BASEBALL FIELD - DAY", "huge bus drives in - CAMP TIGER CLAW", "Bus Arrival / Diesel SFX", "SFX", "High", "6s", "No", "None", "70", ""),
    cue("CUE-088", 45, "EXT. BASEBALL FIELD - DAY", "coach gets back on bus and drives away", "Bus Departure SFX", "SFX", "Medium", "5s", "No", "Out", "60", ""),
    # PAGE 46-47
    cue("CUE-089", 46, "EXT. FOREST LAKE - DAY", "Susie playing wooden flute", "Ceremony Flute Music", "Music", "High", "Loop", "Yes", "In", "60", "Original or royalty-free flute."),
    cue("CUE-090", 47, "EXT. FOREST LAKE - DAY", "Ben and McKinley wedding ceremony", "Wedding Ceremony Ambience", "Ambience", "Medium", "Loop", "Yes", "Under", "45", "Under flute."),
    cue("CUE-091", 47, "EXT. FOREST LAKE - DAY", "flute music continues as Ben and McKinley kiss", "Flute Music Continue", "Music", "Medium", "Loop", "Yes", "None", "55", ""),
    cue("CUE-092", 47, "EXT. BUNK AREA - DAY", "Moose belts CAPTURE THE FLAAAAAAG!", "Capture The Flag Call (Vocal)", "SFX", "High", "3s", "No", "None", "80", "Live read or recorded shout."),
    cue("CUE-093", 47, "EXT. BUNK AREA - DAY", "Someone blows whistle, game kicks off", "Whistle Blast + Game Start", "SFX", "Critical", "2s", "No", "None", "85", ""),
    cue("CUE-094", 47, "EXT. BUNK AREA - DAY", "staff chase and tagging", "Capture The Flag Game Ambience", "Ambience", "High", "Loop", "Yes", "In", "60", "Running, yelling."),
    # PAGE 48-52
    cue("CUE-095", 48, "EXT. BUNK AREA - DAY", "Steve throws peas at tree", "Pea Throw / Tree Tap SFX", "SFX", "Low", "Loop", "Yes", "None", "35", ""),
    cue("CUE-096", 49, "EXT. CAPTURE THE FLAG SIDELINES - DAY", "smells like the ribs are ready", "BBQ / Ribs Ready Ambience", "Ambience", "Medium", "Loop", "Yes", "None", "50", "Sizzling, crowd."),
    cue("CUE-097", 50, "EXT. SCIENCE CLEARING - DAY", "science group emotional huddle", "Emotional Group Ambience", "Ambience", "Low", "Loop", "Yes", "None", "40", ""),
    cue("CUE-098", 51, "EXT. BARBECUE PIT - DAY", "Lindsay face SLATHERED in barbecue sauce", "BBQ Pit Crowd Ambience", "Ambience", "Medium", "Loop", "Yes", "None", "50", ""),
    cue("CUE-099", 54, "EXT. BUNK AREA - CAPTURE THE FLAG - DAY", "slo-mo chase sequence", "Slo-Mo Sports Underscore", "Music", "Medium", "30s", "No", "In/Out", "65", "Royalty-free inspirational."),
    cue("CUE-100", 54, "EXT. WATERFRONT - DAY", "Lars dragged at top speed behind boat", "Water Ski Drag / Splash SFX", "SFX", "Critical", "6s", "No", "None", "80", ""),
    cue("CUE-101", 55, "EXT. RURAL HIGHWAY - DAY", "Freddy thrown out of van", "Body Tumble SFX (Repeat)", "SFX", "Medium", "3s", "No", "None", "70", ""),
    cue("CUE-102", 55, "EXT. CAMPFIRE SITE - DAY", "Coop and Katie in woods", "Woods Day Ambience", "Ambience", "Medium", "Loop", "Yes", "In", "45", "Birds, light wind."),
    cue("CUE-103", 56, "EXT. CAMPFIRE SITE - DAY", "They kiss", "Romantic Kiss Stinger (Optional)", "Comedy", "Optional", "2s", "No", "None", "45", ""),
    # PAGE 57-58
    cue("CUE-104", 57, "EXT. WOODS (LAKE AREA) - DAY", "STEVE walks with antenna on head", "Wind Through Trees Ambience", "Ambience", "Medium", "Loop", "Yes", "In", "50", ""),
    cue("CUE-105", 57, "INT. ARTS AND CRAFTS BUNK - DAY", "Ring Ring! Gail pretends phone", "Phone Ring SFX", "SFX", "High", "3s", "No", "None", "70", ""),
    cue("CUE-106", 57, "INT. ARTS AND CRAFTS BUNK - DAY", "campers applaud and cheer", "Kids Applause / Cheer", "SFX", "Medium", "4s", "No", "None", "60", ""),
    cue("CUE-107", 58, "INT. BETH'S OFFICE - DAY", "Coop on phone with parents", "Office Phone Room Tone", "Ambience", "Low", "Loop", "Yes", "None", "35", ""),
    cue("CUE-108", 58, "INT. REC HALL - DAY", "Susie rehearses talent show number", "Rehearsal Piano / Movement Room", "Ambience", "Medium", "Loop", "Yes", "In", "45", ""),
    # PAGE 59-60
    cue("CUE-109", 59, "EXT. MESS HALL - DAY", "Paul plays guitar on hill", "Paul's Guitar (Diegetic)", "Ambience", "Medium", "Loop", "Yes", "In", "50", ""),
    cue("CUE-110", 59, "EXT. MESS HALL - DAY", "Moose yells DINNER!!!!", "Dinner Call Shout", "SFX", "High", "2s", "No", "None", "85", ""),
    cue("CUE-111", 60, "INT. MESS HALL - DAY", "Everyone eating dinner", "Mess Hall Dinner Crowd", "Ambience", "High", "Loop", "Yes", "In", "60", ""),
    cue("CUE-112", 60, "INT. MESS HALL - DAY", "JJ rolls Crate and Barrel box in", "Large Box Roll / Door SFX", "SFX", "Medium", "4s", "No", "None", "60", ""),
    cue("CUE-113", 60, "INT. MESS HALL - DAY", "Everyone applauds McKinley and Ben", "Mess Hall Applause", "SFX", "Medium", "5s", "No", "None", "65", ""),
    cue("CUE-114", 60, "INT. KITCHEN - DAY", "Gene addresses Can of Vegetables", "Kitchen Backroom Quiet", "Ambience", "Low", "Loop", "Yes", "None", "40", ""),
    # PAGE 61-62
    cue("CUE-115", 61, "INT. RADIO STATION - DAY", "Arty cruising towards happy hour", "Radio Booth Ambience", "Ambience", "Medium", "Loop", "Yes", "None", "40", ""),
    cue("CUE-116", 62, "INT. RADIO STATION - DAY", "Summer in the City starts", "Summer in the City (Lovin' Spoonful)", "Music", "Critical", "Full/skip", "No", "In", "85", "Licensed. Under mess hall scene."),
    cue("CUE-117", 62, "EXT. MESS HALL - DAY", "Coop sees Andy and Katie walking", "Exterior Lawn Under Music", "Ambience", "Low", "Loop", "Yes", "Under", "35", ""),
    # PAGE 63-65
    cue("CUE-118", 63, "EXT. MESS HALL - DAY", "Coop love speech to Katie", "Music Duck / Focus Dialogue", "Transition", "High", "Fade", "No", "Out", "20", "Pull Summer in the City down."),
    cue("CUE-119", 64, "INT. MESS HALL - DAY", "Gene swings doors, plates go flying", "Plates Crash SFX", "SFX", "High", "3s", "No", "None", "80", ""),
    cue("CUE-120", 65, "INT. MESS HALL - DAY", "whole mess hall cheers and applauds Gene", "Big Mess Hall Cheer / Applause", "SFX", "Critical", "8s", "No", "None", "80", ""),
    cue("CUE-121", 65, "INT. MESS HALL - DAY", "Gene humps the fridge, crowd cheers", "Comedy Cheer Continue", "SFX", "High", "6s", "No", "None", "75", ""),
    cue("CUE-122", 65, "INT. MESS HALL - DAY", "they drag Arty to showers", "Struggle / Crowd Movement SFX", "SFX", "High", "Loop", "Yes", "In", "65", ""),
    cue("CUE-123", 65, "INT. SHOWERS - DAY", "push Arty into showers, water full force", "Shower Spray / Arty Yelling", "SFX", "High", "8s", "No", "None", "75", ""),
    cue("CUE-124", 65, "INT. SHOWERS - DAY", "crowd cheers them on", "Victory Cheer SFX", "SFX", "Medium", "5s", "No", "Out", "70", ""),
    # PAGE 66-68
    cue("CUE-125", 66, "EXT. PATH TO PICNIC TABLE - DAY", "Beth and Professor walk by lake", "Lakeside Evening Ambience", "Ambience", "Medium", "Loop", "Yes", "In", "50", ""),
    cue("CUE-126", 67, "EXT. PICNIC TABLE - DAY", "Skylab headed right for camp", "Ominous Drone Underscore", "Music", "High", "Loop", "Yes", "In", "55", "Tension bed."),
    cue("CUE-127", 68, "INT. ANDY'S BUNK - DAY", "Coop confronts Andy", "Bunk Interior Ambience", "Ambience", "Low", "Loop", "Yes", "None", "35", ""),
    # PAGE 69
    cue("CUE-128", 69, "EXT. ANDY'S BUNK - DAY", "steps on RAKE which hits head", "Slapstick Rake Bonk SFX", "SFX", "High", "1s", "No", "None", "80", ""),
    cue("CUE-129", 69, "EXT. ANDY'S BUNK - DAY", "steps on BANANA PEEL, falls in pool", "Banana Peel Slip / Splash SFX", "SFX", "High", "3s", "No", "None", "85", ""),
    cue("CUE-130", 69, "EXT. ANDY'S BUNK - DAY", "bucket lands on his head", "Bucket Clunk SFX", "SFX", "Medium", "1s", "No", "None", "70", "Optional sad trombone."),
    # PAGE 70
    cue("CUE-131", 70, "EXT. FIELD, ETC. - MONTAGE, DUSK", "Coop's TRAINING MONTAGE", "80s Training Montage Music", "Music", "Critical", "Montage", "No", "In/Out", "80", "Royalty-free synth rock."),
    cue("CUE-132", 70, "EXT. FIELD, ETC. - MONTAGE, DUSK", "SLO-MO race through field", "Running / Wind SFX", "SFX", "Medium", "Loop", "Yes", "Under", "45", ""),
    cue("CUE-133", 70, "EXT. FIELD, ETC. - MONTAGE, DUSK", "Coop breaks into tears in therapy", "Montage Music Dip", "Transition", "Medium", "3s", "No", "Out", "40", "Brief emotional beat."),
    cue("CUE-134", 70, "EXT. FIELD, ETC. - MONTAGE, DUSK", "Coop finally NAILS the dance move", "Montage Music Swell", "Music", "High", "5s", "No", "In", "85", ""),
    # PAGE 71
    cue("CUE-135", 71, "EXT. CAMP FIREWOOD SIGN - NIGHT", "Victor runs up path, bloodied", "Night Forest Running / Panting", "SFX", "High", "Loop", "Yes", "In", "60", ""),
    cue("CUE-136", 71, "EXT. BETH'S OFFICE - NIGHT", "Neil rides motorcycle up", "Motorcycle Arrival Night", "SFX", "High", "4s", "No", "None", "70", ""),
    cue("CUE-137", 71, "EXT. MOOSE RIVER - NIGHT", "campers AHHHHHHHH toward rapids", "Rapids Danger Ambience", "Ambience", "Critical", "Loop", "Yes", "In", "75", "Rushing water."),
    cue("CUE-138", 71, "INT. BETH'S OFFICE - NIGHT", "The phone RINGS", "Phone Ring SFX", "SFX", "Critical", "Loop", "Yes", "In", "80", "Urgent ring."),
    cue("CUE-139", 71, "INT. BETH'S OFFICE - NIGHT", "Paul traces call on devices", "Retro Phone Trace Beeps", "SFX", "Medium", "Loop", "Yes", "None", "55", "Comedy tech."),
    # PAGE 72
    cue("CUE-140", 72, "INT. INFIRMARY - NIGHT", "Beth and Neil bust in, break stuff", "Door Smash / Chaos SFX", "SFX", "High", "6s", "No", "None", "80", ""),
    cue("CUE-141", 72, "EXT. REC HALL - NIGHT", "People filing in for talent show", "Rec Hall Crowd Murmur", "Ambience", "High", "Loop", "Yes", "In", "55", ""),
    cue("CUE-142", 72, "EXT. REC HALL - NIGHT", "A silent moment, then Victor: Let's go!", "Hero Beat Silence", "Silence", "High", "2s", "No", "Out", "0", ""),
    cue("CUE-143", 72, "EXT. REC HALL - NIGHT", "Music kicks in as Neil and Victor run off", "Action Run Underscore", "Music", "Critical", "Loop", "Yes", "In", "80", "Royalty-free hero run."),
    cue("CUE-144", 72, "EXT. CAMP FIREWOOD SIGN - NIGHT", "Victor and Neil running full speed", "Running Feet / Night Ambience", "SFX", "High", "Loop", "Yes", "Under", "65", ""),
    # PAGE 73-74
    cue("CUE-145", 73, "EXT. PICNIC TABLE - NIGHT", "device sputters and pops", "Skylab Device Sputter SFX", "SFX", "Medium", "4s", "No", "None", "60", ""),
    cue("CUE-146", 73, "EXT. MOOSE RIVER - NIGHT", "raft inches from waterfall", "Rapids Intensify", "Ambience", "Critical", "Loop", "Yes", "In", "85", ""),
    cue("CUE-147", 74, "EXT. MOOSE RIVER - NIGHT", "Victor saves campers (off-screen heroism)", "Triumph Stinger SFX", "SFX", "High", "3s", "No", "None", "70", ""),
    cue("CUE-148", 74, "EXT. PICNIC TABLE - NIGHT", "class lay looking up at sky", "Night Crickets Ambience", "Ambience", "Low", "Loop", "Yes", "In", "40", ""),
    # PAGE 75-76
    cue("CUE-149", 75, "INT. REC HALL - NIGHT", "TALENT SHOW - Ben quiets everyone", "Talent Show Audience Settle", "Ambience", "High", "Loop", "Yes", "In", "50", "Pre-show hush."),
    cue("CUE-150", 76, "INT. REC HALL - NIGHT", "Beth busts in - audience quiets", "Audience Gasp / Quiet", "SFX", "Medium", "2s", "No", "None", "55", ""),
    cue("CUE-151", 76, "INT. REC HALL - NIGHT", "Muppet-like screaming for Alan Shemper", "Wild Audience Scream / Applause", "SFX", "Critical", "10s", "No", "None", "90", "Beatles-level chaos."),
    cue("CUE-152", 76, "INT. REC HALL - NIGHT", "Alan Shemper takes the stage", "Showbiz Entrance Stinger", "Transition", "Medium", "3s", "No", "In", "65", ""),
    cue("CUE-153", 76, "EXT. PICNIC TABLE - NIGHT", "Caped Boy rolls twenty sided die", "Dice Roll SFX", "SFX", "Medium", "1s", "No", "None", "60", ""),
    cue("CUE-154", 76, "EXT. PICNIC TABLE - NIGHT", "huge symphonic CRESCENDO", "Symphonic Hope Crescendo", "Music", "High", "8s", "No", "In/Out", "75", "Royalty-free orchestral."),
    # PAGE 77-78
    cue("CUE-155", 77, "INT. REC HALL - NIGHT", "Roger balances broomstick", "Awkward Talent Show Silence", "Silence", "Medium", "4s", "No", "In", "0", "Unimpressive act."),
    cue("CUE-156", 78, "INT. REC HALL - NIGHT", "They chat in Hebrew prayer", "Quiet Prayer Murmur", "Ambience", "Low", "3s", "No", "None", "40", ""),
    cue("CUE-157", 79, "INT. REC HALL - NIGHT", "Three girls sing You've Got a Friend", "You've Got a Friend (Campers)", "Music", "Critical", "Full", "No", "In/Out", "75", "Licensed. Bunk 7 dedication."),
    cue("CUE-158", 79, "INT. REC HALL - NIGHT", "Caped Boy rolls die - 18!", "Dice Roll SFX", "SFX", "Low", "1s", "No", "None", "55", ""),
    cue("CUE-159", 79, "INT. REC HALL - NIGHT", "Marty comedy impression - crowd eats it up", "Audience Laughter Loop", "SFX", "Medium", "Loop", "Yes", "None", "60", ""),
    # PAGE 80
    cue("CUE-160", 80, "INT. REC HALL - NIGHT", "ALL: Mooooooooooose!", "Crowd Chant MOOOSE", "SFX", "High", "5s", "No", "None", "80", ""),
    cue("CUE-161", 80, "INT. REC HALL - NIGHT", "Moose farts, giant flash of fire", "Fart Flamethrower SFX", "SFX", "Critical", "3s", "No", "None", "90", "Comedy centerpiece."),
    cue("CUE-162", 80, "INT. REC HALL - NIGHT", "crowd cheers Moose", "Big Cheer SFX", "SFX", "High", "6s", "No", "None", "80", ""),
    cue("CUE-163", 80, "INT. REC HALL - NIGHT", "Ron appears - Gail confrontation", "Dramatic Reveal Stinger", "Transition", "Medium", "2s", "No", "In", "55", ""),
    cue("CUE-164", 80, "INT. REC HALL - NIGHT", "campers applaud Gail", "Applause for Gail", "SFX", "Medium", "5s", "No", "None", "65", ""),
    # PAGE 81
    cue("CUE-165", 81, "INT. REC HALL - NIGHT", "Day By Day from Godspell", "Day By Day (Godspell)", "Music", "Critical", "Full number", "No", "In/Out", "85", "Licensed. Broadway-quality read."),
    cue("CUE-166", 81, "INT. REC HALL - NIGHT", "crowd clapping along", "Rhythmic Audience Clap", "SFX", "Medium", "Loop", "Yes", "Under", "55", ""),
    cue("CUE-167", 81, "INT. REC HALL - NIGHT", "whole crowd collectively BOOS", "Audience Boo / Hiss", "SFX", "Critical", "6s", "No", "None", "80", ""),
    cue("CUE-168", 81, "EXT. PICNIC TABLE - NIGHT", "Caped Boy rolls die - 5!", "Urgent Dice Roll", "SFX", "Medium", "1s", "No", "None", "60", ""),
    # PAGE 82-83
    cue("CUE-169", 82, "INT. REC HALL - NIGHT", "audience absolutely losing it at Shemper", "Roaring Laughter Bed", "SFX", "High", "Loop", "Yes", "None", "70", ""),
    cue("CUE-170", 82, "INT. REC HALL - NIGHT", "back door opens - new Coop entrance", "Door Creak / Gasp", "SFX", "Medium", "3s", "No", "None", "60", ""),
    cue("CUE-171", 83, "INT. REC HALL - NIGHT", "No applause - coughing and murmur", "Awkward Steve Intro Silence", "Silence", "High", "4s", "No", "In", "0", "Before Steve's act."),
    cue("CUE-172", 83, "INT. REC HALL - NIGHT", "Steve THRUSTS hands - small BREEZE", "Gentle Breeze SFX", "SFX", "High", "3s", "No", "In", "40", "Builds to wind."),
    # PAGE 84-85
    cue("CUE-173", 84, "EXT. REC HALL - NIGHT", "building shakes at foundations", "Rumbling / Building Shake", "SFX", "High", "Loop", "Yes", "In", "70", ""),
    cue("CUE-174", 84, "INT. REC HALL - NIGHT", "breeze builds to fierce WIND from Steve", "Wind Crescendo SFX", "SFX", "Critical", "15s", "No", "In/Out", "85", "Steve's power moment."),
    cue("CUE-175", 84, "INT. REC HALL - NIGHT", "benches tipped over, chaos", "Debris / Furniture Crash", "SFX", "High", "6s", "No", "None", "75", ""),
    cue("CUE-176", 85, "EXT. BEHIND REC HALL - NIGHT", "machine vibrates - It's working!", "Device Power-Up Hum", "SFX", "Medium", "Loop", "Yes", "In", "55", ""),
    cue("CUE-177", 85, "EXT. BEHIND REC HALL - NIGHT", "HUGE GUST OF WIND / Skylab redirected", "Massive Wind Gust", "SFX", "Critical", "8s", "No", "None", "90", ""),
    cue("CUE-178", 85, "EXT. BEHIND REC HALL - NIGHT", "CRASH! Skylab falls safely away", "Skylab Crash Impact", "SFX", "Critical", "5s", "No", "None", "95", "Flaming metal debris."),
    cue("CUE-179", 85, "INT. REC HALL - NIGHT", "wind STOPS - Silence for long moment", "Post-Wind Dead Silence", "Silence", "Critical", "5s", "No", "Out", "0", "Hold before slow clap."),
    cue("CUE-180", 85, "INT. REC HALL - NIGHT", "JJ starts slow clap, standing ovation", "Slow Clap to Thunderous Ovation", "SFX", "Critical", "15s", "No", "In", "85", "Beatles concert level."),
    cue("CUE-181", 85, "EXT. REC HALL - NIGHT", "Katie and Coop KISS", "Romantic Kiss Stinger", "Music", "Medium", "4s", "No", "In/Out", "60", "Optional swoon."),
    cue("CUE-182", 85, "EXT. REC HALL - NIGHT", "door flies off hinges at kiss", "Door Fly Off Hinges SFX", "SFX", "High", "2s", "No", "None", "80", ""),
    cue("CUE-183", 85, "EXT. REC HALL - NIGHT", "DISSOLVE TO morning", "Night to Morning Dissolve", "Transition", "Medium", "5s", "No", "Crossfade", "50", ""),
    # PAGE 86-87
    cue("CUE-184", 86, "EXT. PARKING AREA - MORNING", "Parents arriving, goodbyes", "Departure Day Ambience", "Ambience", "High", "Loop", "Yes", "In", "55", "Buses, families."),
    cue("CUE-185", 86, "EXT. PARKING AREA - MORNING", "HUGE laughter from all", "Group Laughter SFX", "SFX", "Medium", "4s", "No", "None", "60", "Shrimp cocktail joke."),
    cue("CUE-186", 87, "EXT. PARKING AREA - MORNING", "Gene mouths thank you to Can of Vegetables", "Sentimental Underscore (Optional)", "Music", "Optional", "8s", "No", "In/Out", "45", ""),
    cue("CUE-187", 87, "EXT. REC HALL - MORNING", "science kids at Skylab crash site", "Morning Birds / Field Ambience", "Ambience", "Low", "Loop", "Yes", "None", "40", ""),
    # PAGE 88-89
    cue("CUE-188", 88, "EXT. BUNK AREA - MORNING", "Katie's breakup speech to Coop", "Lonely Morning Ambience", "Ambience", "Medium", "Loop", "Yes", "Under", "40", ""),
    cue("CUE-189", 89, "EXT. BUNK AREA - MORNING", "station wagon drives off with Andy", "Car Drive Away SFX", "SFX", "Medium", "5s", "No", "Out", "55", ""),
    cue("CUE-190", 89, "EXT. BUNK AREA - MORNING", "Coop standing alone, last one left", "Melancholy Silence", "Silence", "High", "4s", "No", "Out", "0", ""),
    cue("CUE-191", 89, "EXT. BUNK AREA - MORNING", "Beth puts arm around Coop, walk off", "Gentle Ending Underscore", "Music", "High", "20s", "No", "In/Out", "55", "Royalty-free bittersweet."),
    cue("CUE-192", 89, "EXT. BUNK AREA - MORNING", "FADE TO BLACK", "Fade to Black", "Transition", "Critical", "3s", "No", "Out", "0", ""),
    # PAGE 90
    cue("CUE-193", 90, "INT. BETH'S OFFICE - NIGHT", "Ten Years Later - 9:30 AM", "Epilogue Title Sting", "Transition", "High", "3s", "No", "In", "60", ""),
    cue("CUE-194", 90, "INT. BETH'S OFFICE - NIGHT", "Gary fiddling with giant VCR projector", "VCR Projector Whir", "SFX", "Medium", "Loop", "Yes", "In", "50", ""),
    cue("CUE-195", 90, "INT. BETH'S OFFICE - NIGHT", "JJ: Sorry I'm late", "Epilogue Room Tone / Laughter", "Ambience", "Medium", "Loop", "Yes", "None", "45", "End of show."),
    cue("CUE-196", 90, "END", "CREDITS ROLL", "End Credits Music (Optional)", "Music", "Optional", "60s", "No", "Out", "50", "Reprise Jane or original."),
]

# Per-page coverage fill-ins for pages with lighter cue density
_PAGE_FILL = {
    4: [cue("CUE-197", 4, "INT. KATIE'S BUNK - DAWN", "girls putting on makeup", "Bunk Morning Activity", "Ambience", "Low", "Loop", "Yes", "None", "35", "Page coverage.")],
    5: [cue("CUE-198", 5, "EXT. FLAGPOLE - DAWN", "whole camp assembled", "Camp Assembly Murmur", "Ambience", "Medium", "Loop", "Yes", "None", "45", "Page coverage.")],
    8: [cue("CUE-199", 8, "EXT. PROFESSOR'S COTTAGE", "Beth embarrassed after NO", "Awkward Beat", "Silence", "Medium", "2s", "No", "None", "0", "Page coverage.")],
    10: [cue("CUE-200", 10, "INT. MESS HALL", "Gene Vietnam rant", "Kitchen Tension Bed", "Ambience", "Low", "Loop", "Yes", "None", "40", "Page coverage.")],
    13: [cue("CUE-201", 13, "INT. MESS HALL", "Victor refuses Moose River", "Mess Hall Tension", "Ambience", "Low", "Loop", "Yes", "None", "40", "Page coverage.")],
    16: [cue("CUE-202", 16, "EXT. PARKING LOT", "Where's the tape?", "Comedy Beat", "Silence", "Low", "2s", "No", "None", "0", "Page coverage.")],
    20: [cue("CUE-203", 20, "EXT. BETH'S OFFICE", "ten year reunion promise", "Nostalgic Wind (Optional)", "Ambience", "Optional", "Loop", "Yes", "None", "30", "Page coverage.")],
    24: [cue("CUE-204", 24, "EXT. BETH'S OFFICE", "Steve runs away robot voice", "Footsteps Running Away", "SFX", "Low", "3s", "No", "None", "50", "Page coverage.")],
    28: [cue("CUE-205", 28, "EXT. BUNK AREA", "Coop and Katie list girls", "Bunk Area Day Ambience", "Ambience", "Low", "Loop", "Yes", "None", "35", "Page coverage.")],
    32: [cue("CUE-206", 32, "EXT. PARKING AREA", "Come on!! Coop gets in truck", "Truck Door / Peel Out", "SFX", "Medium", "4s", "No", "None", "60", "Page coverage.")],
    36: [cue("CUE-207", 36, "EXT. BARBECUE PIT", "Gene fondue with cheddar cover", "Comedy Pause", "Silence", "Low", "2s", "No", "None", "0", "Page coverage.")],
    37: [cue("CUE-208", 37, "INT. RADIO STATION", "Arty picnic announcement", "Radio Broadcast Bed", "Ambience", "Low", "Loop", "Yes", "None", "40", "Page coverage.")],
    38: [cue("CUE-209", 38, "INT. ARTS AND CRAFTS", "Aaron shiatsu massage", "Soft Room Tone", "Ambience", "Low", "Loop", "Yes", "None", "35", "Page coverage.")],
    41: [cue("CUE-210", 41, "EXT. MOOSE RIVER", "campers float alone", "Ominous River Current", "Ambience", "Medium", "Loop", "Yes", "In", "50", "Page coverage.")],
    43: [cue("CUE-211", 43, "INT. EQUIPMENT SHACK", "knock on door", "Door Knock SFX", "SFX", "Low", "1s", "No", "None", "55", "Page coverage.")],
    46: [cue("CUE-212", 46, "EXT. FOREST LAKE", "JJ and Gary shocked at wedding", "Comedy Gasp", "SFX", "Medium", "2s", "No", "None", "55", "Page coverage.")],
    48: [cue("CUE-213", 48, "EXT. BUNK AREA", "Beth invites Steve to talent show", "Camp Afternoon Bed", "Ambience", "Low", "Loop", "Yes", "None", "35", "Page coverage.")],
    49: [cue("CUE-214", 49, "EXT. CAPTURE THE FLAG SIDELINES", "Andy and Katie on grass", "Distant Game Noise", "Ambience", "Low", "Loop", "Yes", "None", "40", "Page coverage.")],
    50: [cue("CUE-215", 50, "EXT. SCIENCE CLEARING", "Susie argues with Beth", "Tense Outdoor Bed", "Ambience", "Low", "Loop", "Yes", "None", "35", "Page coverage.")],
    51: [cue("CUE-216", 51, "EXT. BARBECUE PIT", "Andy and Lindsay sneak behind mess hall", "Mess Hall Exterior", "Ambience", "Low", "Loop", "Yes", "None", "35", "Page coverage.")],
    52: [cue("CUE-217", 52, "EXT. SIDELINES", "Medieval kid shushed", "Picnic Crowd Murmur", "Ambience", "Low", "Loop", "Yes", "None", "40", "Page coverage.")],
    53: [cue("CUE-218", 53, "EXT. WATERFRONT", "Lars waterskiing before fall", "Boat Engine Loop", "SFX", "Medium", "Loop", "Yes", "In", "55", "Page coverage.")],
    59: [cue("CUE-219", 59, "EXT. KATIE'S BUNK", "Coop finds Katie crying with Andy", "Emotional Door Creak", "SFX", "Low", "2s", "No", "None", "45", "Page coverage.")],
    61: [cue("CUE-220", 61, "INT. RADIO STATION", "Gary dinner interview silence", "Comedy Dead Air", "Silence", "Medium", "3s", "No", "Out", "0", "Beat before Gary speaks.")],
    63: [cue("CUE-221", 63, "EXT. MESS HALL", "Katie rejects Coop", "Heartbreak Sting (Optional)", "Music", "Optional", "3s", "No", "In/Out", "40", "Page coverage.")],
    64: [cue("CUE-222", 64, "INT. MESS HALL", "Gene military speech buildup", "Room Hush", "Silence", "Medium", "2s", "No", "Out", "0", "Page coverage.")],
    66: [cue("CUE-223", 66, "EXT. PATH TO PICNIC TABLE", "Professor distracted by sky", "Evening Lake Insects", "Ambience", "Low", "Loop", "Yes", "None", "40", "Page coverage.")],
    67: [cue("CUE-224", 67, "EXT. PICNIC TABLE", "Let's do it! science montage", "Science Montage Tick", "Transition", "Medium", "2s", "No", "In", "50", "Page coverage.")],
    68: [cue("CUE-225", 68, "EXT. ROCK BY LAKE", "Coop crying, Gene approaches", "Lonely Lake Lap", "Ambience", "Medium", "Loop", "Yes", "In", "45", "Page coverage.")],
    69: [cue("CUE-226", 69, "EXT. PICNIC TABLE", "Skylab device construction", "Tinkering / Building SFX", "SFX", "Low", "Loop", "Yes", "None", "40", "Page coverage.")],
    71: [cue("CUE-227", 71, "INT. BETH'S OFFICE", "He's calling from inside the camp!", "Suspense Sting", "Transition", "High", "2s", "No", "In", "65", "Page coverage.")],
    73: [cue("CUE-228", 73, "EXT. REC HALL", "Victor finds Abby with Moose", "Comedy Shock Sting", "SFX", "Medium", "2s", "No", "None", "60", "Page coverage.")],
    74: [cue("CUE-229", 74, "EXT. PICNIC TABLE", "Professor: Then all is lost", "Dramatic Pause", "Silence", "Medium", "3s", "No", "None", "0", "Page coverage.")],
    75: [cue("CUE-230", 75, "INT. REC HALL", "Good evening Camp Firewood!", "Talent Show Open Applause", "SFX", "High", "5s", "No", "In", "70", "Page coverage.")],
    77: [cue("CUE-231", 77, "INT. REC HALL", "Shemper Stone Age routine", "Comedy Rimshot (Optional)", "Comedy", "Optional", "1s", "No", "None", "45", "Page coverage.")],
    78: [cue("CUE-232", 78, "EXT. BEHIND REC HALL", "device setup behind rec hall", "Night Outdoor Work Ambience", "Ambience", "Low", "Loop", "Yes", "None", "40", "Page coverage.")],
    80: [cue("CUE-233", 80, "INT. REC HALL", "Gail defiant speech to Ron", "Dramatic Underscore Dip", "Silence", "Medium", "2s", "No", "Out", "0", "Page coverage.")],
    82: [cue("CUE-234", 82, "EXT. BEHIND REC HALL", "Beth: Hurry, see it coming", "Urgent Clock Tick (Optional)", "SFX", "Optional", "Loop", "Yes", "None", "45", "Page coverage.")],
    83: [cue("CUE-235", 83, "EXT. REC HALL", "Katie chases Coop - COOP!", "Night Exterior Running", "SFX", "Medium", "Loop", "Yes", "In", "55", "Page coverage.")],
    84: [cue("CUE-236", 84, "EXT. REC HALL", "Katie: I love you Gerald Cooperberg!", "Emotional Music Swell", "Music", "High", "6s", "No", "In", "65", "Page coverage.")],
    86: [cue("CUE-237", 86, "EXT. PARKING AREA", "Beth pregnant reveal hug", "Warm Morning Sting", "Music", "Medium", "5s", "No", "In/Out", "50", "Page coverage.")],
    88: [cue("CUE-238", 88, "EXT. BUNK AREA", "Mork Guy: Nanoo-nanoo", "Comedy Alien Sting (Optional)", "Comedy", "Optional", "2s", "No", "None", "40", "Page coverage.")],
    1: [cue("CUE-239", 1, "TITLE CARD", "Second Draft / February 2026", "Projector / Room Tone (Optional)", "Ambience", "Optional", "Loop", "Yes", "In", "25", "Pre-show optional.")],
}

for _page, _extra in _PAGE_FILL.items():
    CUES.extend(_extra)

# Sort chronologically by page then cue id
CUES.sort(key=lambda c: (c["Script Page"], c["Cue ID"]))

LICENSED_MUSIC = [
    {"Song": "Jane", "Artist": "Jefferson Starship", "Scene": "Opening Titles / Campfire", "Trigger": '"Jane" begins with opening TITLES over black', "Fade": "In at open; crossfade to scene", "Notes": "CUE-002, CUE-007. Primary opening theme."},
    {"Song": "Standing in the Rain (snippet)", "Artist": "Campers (diegetic, references rock lyrics)", "Scene": "Coop's Bunk - Dawn", "Trigger": 'Campers singing "Standing in the rain"', "Fade": "Short diegetic acapella", "Notes": "CUE-015. Not full licensed playback."},
    {"Song": "Danny's Song", "Artist": "Loggins & Messina", "Scene": "Country Road / Abby's Bunk", "Trigger": "Victor sings in van; tape player in bunk", "Fade": "Cut hard on crash; lo-fi in bunk", "Notes": "CUE-073, CUE-075."},
    {"Song": "Love Is Alright Tonight", "Artist": "Rick Springfield", "Scene": "Trip to Waterville Montage", "Trigger": "As Love is Alright Tonight plays-", "Fade": "FADE OUT MUSIC after montage", "Notes": "CUE-062, CUE-065."},
    {"Song": "Summer in the City", "Artist": "Lovin' Spoonful", "Scene": "Radio Station / Mess Hall Exterior", "Trigger": '"Summer in the City" starts and continues', "Fade": "Duck for Coop/Katie dialogue", "Notes": "CUE-116, CUE-118."},
    {"Song": "Day By Day", "Artist": "Godspell (Stephen Schwartz)", "Scene": "Talent Show", "Trigger": "performing Day By Day from Godspell", "Fade": "Full number; ends into boos", "Notes": "CUE-165. Also referenced CUE-033."},
    {"Song": "You've Got a Friend", "Artist": "Carole King (performed by campers)", "Scene": "Talent Show", "Trigger": "Three girls singing Winter Spring Summer or Fall", "Fade": "In/Out around act", "Notes": "CUE-157."},
]
