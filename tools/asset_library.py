"""Canonical reusable sound asset library and cue-to-asset resolution."""

from __future__ import annotations

PLAYBACK_DEFAULTS = {
    "Loop": 30,
    "One Shot": 85,
    "Music": 70,
    "Silence": 0,
}

# Canonical assets: key -> definition. Filenames are stable production paths.
CANONICAL_ASSETS: dict[str, dict] = {
    # --- Silence ---
    "silence_hold": {
        "name": "Silence Hold",
        "category": "Silence",
        "playback_mode": "Silence",
        "filename": "assets/generated/silence_hold.mp3",
        "royalty_free": "Yes",
        "source": "Digital silence",
        "duration": "Variable",
        "notes": "Reusable silence bed; cue duration/fade control behavior.",
    },
    # --- Music (licensed + royalty-free beds) ---
    "music_jane": {
        "name": "Jane (Jefferson Starship)",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_jane_jefferson_starship.mp3",
        "royalty_free": "No",
        "source": "Licensed - Jefferson Starship",
        "duration": "Full excerpt",
        "notes": "Opening titles and title montage.",
    },
    "music_danny_song": {
        "name": "Danny's Song (Loggins & Messina)",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_danny_song_loggins_messina.mp3",
        "royalty_free": "No",
        "source": "Licensed - Loggins & Messina",
        "duration": "Verse+",
        "notes": "Victor van sing + Abby bunk tape.",
    },
    "music_love_is_alright": {
        "name": "Love Is Alright Tonight (Rick Springfield)",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_love_is_alright_tonight.mp3",
        "royalty_free": "No",
        "source": "Licensed - Rick Springfield",
        "duration": "Montage",
        "notes": "Waterville trip montage.",
    },
    "music_summer_in_the_city": {
        "name": "Summer in the City (Lovin' Spoonful)",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_summer_in_the_city.mp3",
        "royalty_free": "No",
        "source": "Licensed - Lovin' Spoonful",
        "duration": "Full/skip",
        "notes": "Arty radio into mess hall exteriors.",
    },
    "music_godspell_day_by_day": {
        "name": "Day By Day (Godspell)",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_godspell_day_by_day.mp3",
        "royalty_free": "No",
        "source": "Licensed - Godspell",
        "duration": "Full number",
        "notes": "Talent show centerpiece.",
    },
    "music_youve_got_a_friend": {
        "name": "You've Got a Friend (Campers)",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_youve_got_a_friend_campers.mp3",
        "royalty_free": "No",
        "source": "Licensed - Carole King",
        "duration": "Full",
        "notes": "Bunk 7 talent show act.",
    },
    "music_ceremony_flute": {
        "name": "Ceremony Flute",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_ceremony_flute.mp3",
        "royalty_free": "Yes",
        "source": "Royalty-free flute",
        "duration": "Loop",
        "notes": "Ben/McKinley wedding at forest lake.",
    },
    "music_montage_80s": {
        "name": "80s Training Montage",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_80s_training_montage.mp3",
        "royalty_free": "Yes",
        "source": "Royalty-free synth rock",
        "duration": "Montage",
        "notes": "Coop/Gene training montage.",
    },
    "music_action_run": {
        "name": "Action Run Underscore",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_action_run_underscore.mp3",
        "royalty_free": "Yes",
        "source": "Royalty-free",
        "duration": "Loop",
        "notes": "Victor/Neil hero run.",
    },
    "music_chase_comedy": {
        "name": "Chase Sequence Underscore",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_chase_comedy_underscore.mp3",
        "royalty_free": "Yes",
        "source": "Royalty-free",
        "duration": "Loop",
        "notes": "Motorcycle chase.",
    },
    "music_slo_mo_sports": {
        "name": "Slo-Mo Sports Underscore",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_slo_mo_sports.mp3",
        "royalty_free": "Yes",
        "source": "Royalty-free",
        "duration": "30s",
        "notes": "Capture the flag chase beat.",
    },
    "music_symphonic_crescendo": {
        "name": "Symphonic Hope Crescendo",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_symphonic_hope_crescendo.mp3",
        "royalty_free": "Yes",
        "source": "Royalty-free orchestral",
        "duration": "8s",
        "notes": "D20 die reveal.",
    },
    "music_acapella_snippet": {
        "name": "Campers Acapella Rock Snippet",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_campers_acapella_snippet.mp3",
        "royalty_free": "Yes",
        "source": "Live table read / original",
        "duration": "15s",
        "notes": "Diegetic camper singing.",
    },
    "music_godspell_sting": {
        "name": "Godspell Announcement Sting",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_godspell_sting.mp3",
        "royalty_free": "No",
        "source": "Licensed - Godspell",
        "duration": "5s",
        "notes": "Mess hall announcement tease.",
    },
    "music_paul_guitar": {
        "name": "Paul's Guitar (Diegetic)",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_paul_guitar_diegetic.mp3",
        "royalty_free": "Yes",
        "source": "Live / recorded guitar",
        "duration": "Loop",
        "notes": "Hill before dinner.",
    },
    "music_ending_bittersweet": {
        "name": "Gentle Ending Underscore",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_gentle_ending_bittersweet.mp3",
        "royalty_free": "Yes",
        "source": "Royalty-free",
        "duration": "20s",
        "notes": "Coop/Beth walk-off.",
    },
    "music_emotional_swell": {
        "name": "Emotional Music Swell",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_emotional_swell.mp3",
        "royalty_free": "Yes",
        "source": "Royalty-free",
        "duration": "6s",
        "notes": "Katie/Coop exterior reunion.",
    },
    "music_romantic_stinger": {
        "name": "Romantic Kiss Stinger",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_romantic_kiss_stinger.mp3",
        "royalty_free": "Yes",
        "source": "Royalty-free",
        "duration": "4s",
        "notes": "Optional kiss moments.",
    },
    "music_warm_morning": {
        "name": "Warm Morning Sting",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_warm_morning_sting.mp3",
        "royalty_free": "Yes",
        "source": "Royalty-free",
        "duration": "5s",
        "notes": "Departure morning beats.",
    },
    "music_epilogue_sting": {
        "name": "Epilogue Title Sting",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_epilogue_title_sting.mp3",
        "royalty_free": "Yes",
        "source": "Royalty-free",
        "duration": "3s",
        "notes": "Ten years later.",
    },
    "music_end_credits": {
        "name": "End Credits Music",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/generated/music_end_credits.mp3",
        "royalty_free": "Yes",
        "source": "Royalty-free / Jane reprise",
        "duration": "60s",
        "notes": "Optional post-show.",
    },
    # --- Looping ambience ---
    "amb_campfire_night": {
        "name": "Campfire Night",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/campfire_night.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Fire crackle, crickets, night camp.",
    },
    "amb_outdoor_dawn": {
        "name": "Outdoor Dawn Nature",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/outdoor_dawn_nature.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Lake sunrise, garden morning, woods day, birds.",
    },
    "amb_camp_exterior_day": {
        "name": "Camp Exterior Day",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/camp_exterior_day.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Hill, parking lot, bunk area, mess hall exterior, porches.",
    },
    "amb_camp_morning_bustle": {
        "name": "Camp Morning Bustle",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/camp_morning_bustle.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Field scramble, flagpole assembly murmur.",
    },
    "amb_mess_hall_crowd": {
        "name": "Mess Hall Crowd",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/mess_hall_crowd.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Breakfast, dinner, tension, continue variants.",
    },
    "amb_kitchen_backroom": {
        "name": "Kitchen Backroom",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/kitchen_backroom.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Gene/Gary kitchen scenes.",
    },
    "amb_radio_station": {
        "name": "WCFW Radio Station",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/wcfw_radio_station.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / original",
        "duration": "Loop",
        "notes": "Booth tone, static bed, broadcast under VO.",
    },
    "amb_lake_waterfront": {
        "name": "Lake Waterfront",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/lake_waterfront.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Swimming area, docks, lonely lake laps.",
    },
    "amb_arts_crafts": {
        "name": "Arts & Crafts Room",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/arts_crafts_room.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Gail sessions, soft room tone.",
    },
    "amb_bunk_interior": {
        "name": "Bunk Interior",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/bunk_interior.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Counselor bunks, office phone scenes.",
    },
    "amb_bbq_pit": {
        "name": "BBQ Pit / Picnic",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/bbq_pit_picnic.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Sizzle, sidelines, ribs ready.",
    },
    "amb_river": {
        "name": "River / Rapids",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/river_rapids.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Raft, danger rapids, Moose River.",
    },
    "amb_highway_drive": {
        "name": "Highway / Rural Road",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/highway_rural_road.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Van drive, lonely walk wind.",
    },
    "amb_talent_show_audience": {
        "name": "Talent Show Audience",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/talent_show_audience.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Rec hall murmur, settle, laughter bed.",
    },
    "amb_capture_the_flag": {
        "name": "Capture The Flag Game",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/capture_the_flag_game.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Running, yelling, distant game.",
    },
    "amb_evening_lakeside": {
        "name": "Evening Lakeside",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/evening_lakeside.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Path to picnic table, insects.",
    },
    "amb_night_exterior": {
        "name": "Night Exterior Camp",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/night_exterior_camp.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Crickets, night work behind rec hall.",
    },
    "amb_science_clearing": {
        "name": "Science Clearing",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/science_clearing.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Outdoor class, picnic table work.",
    },
    "amb_rehearsal_room": {
        "name": "Rehearsal / Rec Hall Day",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/rehearsal_rec_hall_day.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Talent show rehearsal.",
    },
    "amb_swimming_hole": {
        "name": "Swimming Hole Woods",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/swimming_hole_woods.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "JJ/Gary sneak scenes.",
    },
    "amb_group_emotional": {
        "name": "Soft Emotional Room",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/soft_emotional_room.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Crying, therapy, Gail breakdown support.",
    },
    "amb_projector_room": {
        "name": "Projector Room Tone",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/projector_room_tone.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Pre-show optional.",
    },
    "amb_epilogue_room": {
        "name": "Epilogue Lounge",
        "category": "Ambience",
        "playback_mode": "Loop",
        "filename": "assets/ambience/epilogue_lounge.mp3",
        "royalty_free": "Yes",
        "source": "Freesound / BBC",
        "duration": "Loop",
        "notes": "Ten years later gathering.",
    },
    # --- One-shot SFX ---
    "sfx_transition_whoosh": {
        "name": "Scene Transition Whoosh",
        "category": "Transition",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/scene_transition_whoosh.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "2s",
        "notes": "Cuts, dissolves, title cards, montage ticks.",
    },
    "sfx_applause_cheer": {
        "name": "Applause / Cheer",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/applause_cheer.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "3-15s",
        "notes": "Light applause through standing ovation.",
    },
    "sfx_audience_laugh": {
        "name": "Audience Laughter",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/audience_laughter.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "4-8s",
        "notes": "Talent show hysterics, group laughs.",
    },
    "sfx_audience_scream": {
        "name": "Audience Scream / Whoop",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/audience_scream_whoop.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "10s",
        "notes": "Muppet-level Shemper entrance.",
    },
    "sfx_audience_boo": {
        "name": "Audience Boo / Hiss",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/audience_boo_hiss.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "6s",
        "notes": "Post-Godspell reaction.",
    },
    "sfx_crowd_chant": {
        "name": "Crowd Chant",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/crowd_chant.wav",
        "royalty_free": "Yes",
        "source": "Freesound / live",
        "duration": "5s",
        "notes": "MOOOSE chant.",
    },
    "sfx_running_footsteps": {
        "name": "Running Footsteps",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/running_footsteps.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "4s",
        "notes": "Chases, bunk exits, night runs.",
    },
    "sfx_vehicle_bus": {
        "name": "Bus Diesel",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/vehicle_bus_diesel.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "6s",
        "notes": "Tiger Claw arrival/departure.",
    },
    "sfx_vehicle_truck": {
        "name": "Truck / Pickup",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/vehicle_truck_pickup.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "4s",
        "notes": "Beth's truck, door, peel-out.",
    },
    "sfx_vehicle_van": {
        "name": "Van Engine",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/vehicle_van_engine.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "4s",
        "notes": "Acceleration, doors, raft fall.",
    },
    "sfx_vehicle_motorcycle": {
        "name": "Motorcycle",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/vehicle_motorcycle.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "4s",
        "notes": "Approach, start, skid, night arrival.",
    },
    "sfx_crash_vehicle": {
        "name": "Vehicle Crash",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/crash_vehicle.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "4s",
        "notes": "Van into tree.",
    },
    "sfx_crash_impact": {
        "name": "Impact / Crash Debris",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/crash_impact_debris.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "3s",
        "notes": "Plates, benches, door off hinges, Skylab.",
    },
    "sfx_water_splash": {
        "name": "Water Splash",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/water_splash.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "4s",
        "notes": "Lake fall, pool, ski drag.",
    },
    "sfx_body_tumble": {
        "name": "Body Tumble / Roll",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/body_tumble_roll.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "3s",
        "notes": "Thrown from van gags.",
    },
    "sfx_slapstick": {
        "name": "Slapstick Comedy Pack",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/slapstick_comedy_pack.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "1-3s",
        "notes": "Rake bonk, banana slip, bucket clunk.",
    },
    "sfx_fart": {
        "name": "Comedy Fart",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/comedy_fart.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "2s",
        "notes": "Van seat + Moose flamethrower layer.",
    },
    "sfx_phone": {
        "name": "Telephone",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/telephone_ring.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "3s",
        "notes": "Ring + mime ring in arts & crafts.",
    },
    "sfx_phone_beeps": {
        "name": "Phone Trace Beeps",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/phone_trace_beeps.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "Loop",
        "notes": "Paul traces call.",
    },
    "sfx_whistle": {
        "name": "Whistle",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/whistle.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "2s",
        "notes": "Capture flag, wolf whistles.",
    },
    "sfx_door": {
        "name": "Door",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/door.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "2s",
        "notes": "Knock, creak, smash, infirmary bust-in.",
    },
    "sfx_dice_roll": {
        "name": "Dice Roll",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/dice_roll.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "1s",
        "notes": "D20 calibration scenes.",
    },
    "sfx_wind_light": {
        "name": "Wind Gentle",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/wind_gentle.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "3s",
        "notes": "Steve's initial breeze.",
    },
    "sfx_wind_heavy": {
        "name": "Wind Heavy / Gust",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/wind_heavy_gust.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "15s",
        "notes": "Steve power + Skylab redirect gust.",
    },
    "sfx_rumble": {
        "name": "Rumble / Building Shake",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/rumble_building_shake.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "6s",
        "notes": "Rec hall foundation shake.",
    },
    "sfx_device_scifi": {
        "name": "Sci-Fi Device",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/scifi_device.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "4s",
        "notes": "Skylab tracker sputter/power-up.",
    },
    "sfx_prop_impact": {
        "name": "Prop Impact",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/prop_impact.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "2s",
        "notes": "Tray thud, tool clatter, mud squish, flag rope.",
    },
    "sfx_comedy_stinger": {
        "name": "Comedy Stinger",
        "category": "Comedy",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/comedy_stinger.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "1-3s",
        "notes": "Crickets, rimshot, alien sting, shock stings.",
    },
    "sfx_dramatic_stinger": {
        "name": "Dramatic Stinger",
        "category": "Transition",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/dramatic_stinger.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "2s",
        "notes": "Reveal, suspense, hero beats.",
    },
    "sfx_human_reaction": {
        "name": "Human Reaction",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/human_reaction.wav",
        "royalty_free": "Yes",
        "source": "Freesound / live",
        "duration": "2-5s",
        "notes": "Screams, shouts, kid pile-on, wrestling.",
    },
    "sfx_smooch": {
        "name": "Smooch / Makeout",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/smooch_makeout.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "2s",
        "notes": "Comedy smooch layers.",
    },
    "sfx_banana": {
        "name": "Banana / Eating",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/banana_eating.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "3s",
        "notes": "Groundskeeper gag.",
    },
    "sfx_shower": {
        "name": "Shower Spray",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/shower_spray.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "8s",
        "notes": "Arty forced shower.",
    },
    "sfx_car_door": {
        "name": "Car Door",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/car_door.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "2s",
        "notes": "Silas departure, wagon leave.",
    },
    "sfx_mic_click": {
        "name": "Mic / Headphone Click",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/mic_headphone_click.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "1s",
        "notes": "Radio booth.",
    },
    "sfx_box_roll": {
        "name": "Large Box Roll",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/large_box_roll.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "4s",
        "notes": "Crate and Barrel chaise.",
    },
    "sfx_vocal_callout": {
        "name": "Vocal Callout",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/vocal_callout.wav",
        "royalty_free": "Yes",
        "source": "Live table read",
        "duration": "2s",
        "notes": "DINNER, CAPTURE THE FLAG, kitchen yell.",
    },
    "sfx_vcr_projector": {
        "name": "VCR / Projector",
        "category": "SFX",
        "playback_mode": "Loop",
        "filename": "assets/sfx/vcr_projector_loop.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "Loop",
        "notes": "BetaMax gag + epilogue projector.",
    },
    "sfx_tinkering": {
        "name": "Tinkering / Building",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/tinkering_building.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "Loop",
        "notes": "Skylab device construction.",
    },
    "sfx_boat_engine": {
        "name": "Boat Engine",
        "category": "SFX",
        "playback_mode": "One Shot",
        "filename": "assets/sfx/boat_engine.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "Loop",
        "notes": "Motorboat pass, ski boat.",
    },
    "sfx_clock_tick": {
        "name": "Clock Tick (Optional)",
        "category": "Comedy",
        "playback_mode": "Loop",
        "filename": "assets/sfx/clock_tick_optional.wav",
        "royalty_free": "Yes",
        "source": "Freesound",
        "duration": "Loop",
        "notes": "Urgent Skylab countdown optional.",
    },
}

# Explicit cue-id overrides for edge cases (highest priority).
CUE_ASSET_OVERRIDES: dict[str, str] = {}

# Keyword rules: (predicate on cue dict, asset key). First match wins.
_CUE_RULES: list[tuple] = []


def _name(cue: dict) -> str:
    return cue["Cue Name"].lower()


def _build_rules():
    global _CUE_RULES
    if _CUE_RULES:
        return

    def r(pred, key):
        _CUE_RULES.append((pred, key))

    # Silence
    r(lambda c: c["Category"] == "Silence", "silence_hold")

    # Licensed / specific music
    r(lambda c: "jane" in _name(c), "music_jane")
    r(lambda c: "danny" in _name(c), "music_danny_song")
    r(lambda c: "love is alright" in _name(c), "music_love_is_alright")
    r(lambda c: "summer in the city" in _name(c), "music_summer_in_the_city")
    r(lambda c: "day by day" in _name(c), "music_godspell_day_by_day")
    r(lambda c: "you've got a friend" in _name(c), "music_youve_got_a_friend")
    r(lambda c: "godspell" in _name(c) and "sting" in _name(c), "music_godspell_sting")
    r(lambda c: "ceremony flute" in _name(c) or ("flute" in _name(c) and "continue" in _name(c)), "music_ceremony_flute")
    r(lambda c: "training montage" in _name(c) or "montage music" in _name(c) and c["Category"] == "Ambience" and "music" in _name(c), "music_montage_80s")
    r(lambda c: "montage music dip" in _name(c) or "montage music swell" in _name(c), "music_montage_80s")
    r(lambda c: "action run" in _name(c), "music_action_run")
    r(lambda c: "chase sequence" in _name(c), "music_chase_comedy")
    r(lambda c: "slo-mo sports" in _name(c), "music_slo_mo_sports")
    r(lambda c: "symphonic" in _name(c), "music_symphonic_crescendo")
    r(lambda c: "acapella" in _name(c), "music_acapella_snippet")
    r(lambda c: "paul" in _name(c) and "guitar" in _name(c), "music_paul_guitar")
    r(lambda c: "ending underscore" in _name(c) or "gentle ending" in _name(c), "music_ending_bittersweet")
    r(lambda c: "emotional music swell" in _name(c), "music_emotional_swell")
    r(lambda c: "romantic kiss stinger" in _name(c) and c["Category"] == "Ambience" and "music" in _name(c), "music_romantic_stinger")
    r(lambda c: "warm morning sting" in _name(c), "music_warm_morning")
    r(lambda c: "epilogue title" in _name(c), "music_epilogue_sting")
    r(lambda c: "end credits" in _name(c), "music_end_credits")
    r(lambda c: "title music continue" in _name(c) or "jane / title" in _name(c), "music_jane")
    r(lambda c: "heartbreak" in _name(c) and c["Category"] == "Ambience" and "music" in _name(c), "music_romantic_stinger")
    r(lambda c: "sentimental underscore" in _name(c), "music_ending_bittersweet")
    r(lambda c: "fade out music" in _name(c), "music_love_is_alright")
    r(lambda c: "rehearsal piano" in _name(c), "amb_rehearsal_room")
    r(lambda c: c["Category"] == "Ambience" and any(k in _name(c) for k in ("underscore", "montage", "credits", "jane", "flute")), "music_montage_80s")

    # Ambience pools
    r(lambda c: "campfire night" in _name(c), "amb_campfire_night")
    r(lambda c: any(x in _name(c) for x in ("dawn lake", "garden morning", "woods day", "wind through trees", "morning birds")), "amb_outdoor_dawn")
    r(lambda c: any(x in _name(c) for x in (
        "camp exterior", "hill / office", "office porch", "camp afternoon",
        "mess hall door", "mess hall exterior", "bunk area day", "tense outdoor",
        "picnic crowd", "departure day", "lonely morning", "exterior lawn",
        "nostalgic wind", "camp parking", "group therapy", "dance shack",
    )), "amb_camp_exterior_day")
    r(lambda c: any(x in _name(c) for x in ("morning bustle", "flagpole crowd", "camp assembly")), "amb_camp_morning_bustle")
    r(lambda c: "mess hall" in _name(c) and c["Category"] == "Ambience", "amb_mess_hall_crowd")
    r(lambda c: "kitchen" in _name(c) and c["Category"] == "Ambience", "amb_kitchen_backroom")
    r(lambda c: any(x in _name(c) for x in ("radio", "wcfw", "rock block", "broadcast bed", "radio booth")), "amb_radio_station")
    r(lambda c: any(x in _name(c) for x in ("waterfront", "lake", "lakeside", "lonely lake")), "amb_lake_waterfront")
    r(lambda c: "arts" in _name(c) or "soft room" in _name(c), "amb_arts_crafts")
    r(lambda c: "bunk interior" in _name(c) or "bunk morning" in _name(c) or "office phone" in _name(c), "amb_bunk_interior")
    r(lambda c: any(x in _name(c) for x in ("bbq", "ribs", "picnic", "grill")), "amb_bbq_pit")
    r(lambda c: any(x in _name(c) for x in ("river", "rapids", "raft", "moose river")), "amb_river")
    r(lambda c: any(x in _name(c) for x in ("highway", "rural road", "lonely road", "van highway", "barren road")), "amb_highway_drive")
    r(lambda c: any(x in _name(c) for x in ("talent show", "rec hall crowd", "audience settle", "roaring laughter bed", "rec hall murmur")), "amb_talent_show_audience")
    r(lambda c: any(x in _name(c) for x in ("capture the flag", "distant game", "game ambience", "game noise")), "amb_capture_the_flag")
    r(lambda c: any(x in _name(c) for x in ("evening lake", "lakeside evening", "lake insects", "path to picnic")), "amb_evening_lakeside")
    r(lambda c: any(x in _name(c) for x in ("night forest", "night exterior", "night outdoor", "night crickets", "behind the rec hall")), "amb_night_exterior")
    r(lambda c: "science clearing" in _name(c) or "science montage" in _name(c), "amb_science_clearing")
    r(lambda c: "swimming hole" in _name(c), "amb_swimming_hole")
    r(lambda c: any(x in _name(c) for x in ("crying", "emotional", "shiatsu", "therapy session")), "amb_group_emotional")
    r(lambda c: "projector" in _name(c) and c["Category"] == "Ambience", "amb_projector_room")
    r(lambda c: "epilogue" in _name(c) and c["Category"] == "Ambience", "amb_epilogue_room")
    r(lambda c: c["Category"] == "Ambience", "amb_camp_exterior_day")

    # SFX pools
    r(lambda c: any(x in _name(c) for x in ("applause", "cheer", "ovation", "clap", "chant mooo")), "sfx_applause_cheer")
    r(lambda c: "moooo" in _name(c), "sfx_crowd_chant")
    r(lambda c: "boo" in _name(c), "sfx_audience_boo")
    r(lambda c: "scream" in _name(c) and "audience" in _name(c) or "muppet" in _name(c), "sfx_audience_scream")
    r(lambda c: "laughter" in _name(c), "sfx_audience_laugh")
    r(lambda c: "running" in _name(c) or "footsteps" in _name(c) or "panting" in _name(c), "sfx_running_footsteps")
    r(lambda c: "bus" in _name(c), "sfx_vehicle_bus")
    r(lambda c: "truck" in _name(c) or "pickup" in _name(c) or "peel out" in _name(c), "sfx_vehicle_truck")
    r(lambda c: "motorcycle" in _name(c), "sfx_vehicle_motorcycle")
    r(lambda c: "van crash" in _name(c) or "vehicle crash" in _name(c), "sfx_crash_vehicle")
    r(lambda c: "van engine" in _name(c) or ("van" in _name(c) and "accelerat" in _name(c)), "sfx_vehicle_van")
    r(lambda c: any(x in _name(c) for x in ("skylab crash", "debris", "door fly", "door off", "bench", "foundation")), "sfx_crash_impact")
    r(lambda c: "plate" in _name(c) or "plates crash" in _name(c), "sfx_crash_impact")
    r(lambda c: any(x in _name(c) for x in ("splash", "drown", "pool", "ski drag", "water ski")), "sfx_water_splash")
    r(lambda c: "tumble" in _name(c) or "thrown out" in _name(c), "sfx_body_tumble")
    r(lambda c: any(x in _name(c) for x in ("rake", "banana peel", "bucket", "slapstick")), "sfx_slapstick")
    r(lambda c: "fart" in _name(c), "sfx_fart")
    r(lambda c: "phone" in _name(c) and "beep" in _name(c), "sfx_phone_beeps")
    r(lambda c: "phone" in _name(c) or "ring ring" in _name(c), "sfx_phone")
    r(lambda c: "whistle" in _name(c), "sfx_whistle")
    r(lambda c: "door" in _name(c) or "bust in" in _name(c) or "door smash" in _name(c), "sfx_door")
    r(lambda c: "dice" in _name(c), "sfx_dice_roll")
    r(lambda c: "gentle breeze" in _name(c) or "small breeze" in _name(c), "sfx_wind_light")
    r(lambda c: any(x in _name(c) for x in ("fierce wind", "wind crescendo", "massive wind", "gust")), "sfx_wind_heavy")
    r(lambda c: "rumbl" in _name(c) or "shake" in _name(c), "sfx_rumble")
    r(lambda c: any(x in _name(c) for x in ("device", "sputter", "power-up", "tracker")), "sfx_device_scifi")
    r(lambda c: any(x in _name(c) for x in ("tray thud", "tool clatter", "mud", "flagpole", "tinkering", "building sfx")), "sfx_prop_impact")
    r(lambda c: any(x in _name(c) for x in ("cricket", "rimshot", "alien", "shock sting", "gasp", "trombone")), "sfx_comedy_stinger")
    r(lambda c: any(x in _name(c) for x in ("dramatic", "suspense", "hero beat", "reveal", "showbiz entrance")), "sfx_dramatic_stinger")
    r(lambda c: any(x in _name(c) for x in ("scream", "shout", "wrestling", "pile-on", "struggle", "yelling")), "sfx_human_reaction")
    r(lambda c: "smooch" in _name(c) or "makeout" in _name(c) or "make out" in _name(c), "sfx_smooch")
    r(lambda c: "banana" in _name(c) and "eating" in _name(c) or "banana peel / eating" in _name(c), "sfx_banana")
    r(lambda c: "shower" in _name(c), "sfx_shower")
    r(lambda c: "car door" in _name(c) or "drive away" in _name(c) or "station wagon" in _name(c), "sfx_car_door")
    r(lambda c: "mic" in _name(c) or "headphone" in _name(c), "sfx_mic_click")
    r(lambda c: "box roll" in _name(c) or "crate" in _name(c), "sfx_box_roll")
    r(lambda c: any(x in _name(c) for x in ("dinner", "capture the fl", "kitchen call", "victor yelling")), "sfx_vocal_callout")
    r(lambda c: "vcr" in _name(c) or "projector whir" in _name(c), "sfx_vcr_projector")
    r(lambda c: "motorboat" in _name(c) or "boat engine" in _name(c), "sfx_boat_engine")
    r(lambda c: "clock tick" in _name(c), "sfx_clock_tick")
    r(lambda c: "triumph stinger" in _name(c), "sfx_dramatic_stinger")

    # Transitions
    r(lambda c: c["Category"] == "Transition", "sfx_transition_whoosh")
    r(lambda c: c["Category"] == "Comedy", "sfx_comedy_stinger")
    r(lambda c: c["Category"] == "SFX", "sfx_prop_impact")


_build_rules()


def resolve_asset_key(cue: dict) -> str:
    """Map a cue to a canonical asset key while preserving cue-level mix behavior."""
    cid = cue["Cue ID"]
    if cid in CUE_ASSET_OVERRIDES:
        return CUE_ASSET_OVERRIDES[cid]
    _build_rules()
    for pred, key in _CUE_RULES:
        if pred(cue):
            return key
    return "sfx_prop_impact"


def suggested_volume_for_mode(mode: str) -> int:
    return PLAYBACK_DEFAULTS[mode]
