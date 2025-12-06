"""
Bureau of Meteorology (BOM) Radar Metadata

This file contains the geographical coordinates and scale information for all
Australian BOM weather radars. Each radar entry contains:
- Latitude: Radar center latitude in decimal degrees
- Longitude: Radar center longitude in decimal degrees
- km_per_pixel: Approximate kilometers per pixel at the given radar range

Product ID format: IDRXYZ where:
- X indicates the radar range (typically 1=512km, 2=256km, 3=128km, 4=64km)
- YZ is a unique identifier for each radar location

Data format: 'PRODUCT_ID': (latitude, longitude, km_per_pixel)
"""

RADAR_METADATA = {
    # Northern Territory
    'IDR631': (-12.46, 130.93, 2.0),    # Darwin (Berrimah) 512km
    'IDR632': (-12.46, 130.93, 1.0),    # Darwin 256km
    'IDR633': (-12.46, 130.93, 0.5),    # Darwin 128km
    'IDR634': (-12.46, 130.93, 0.25),   # Darwin 64km
    'IDR1121': (-12.27, 136.82, 2.0),   # Gove 512km
    'IDR1122': (-12.27, 136.82, 1.0),   # Gove 256km
    'IDR1123': (-12.27, 136.82, 0.5),   # Gove 128km
    'IDR1124': (-12.27, 136.82, 0.25),  # Gove 64km
    'IDR421': (-14.51, 132.45, 2.0),    # Katherine (Tindal) 512km
    'IDR422': (-14.51, 132.45, 1.0),    # Katherine 256km
    'IDR423': (-14.51, 132.45, 0.5),    # Katherine 128km
    'IDR424': (-14.51, 132.45, 0.25),   # Katherine 64km
    'IDR771': (-11.6494, 133.38, 2.0),  # Warruwi 512km
    'IDR772': (-11.6494, 133.38, 1.0),  # Warruwi 256km
    'IDR773': (-11.6494, 133.38, 0.5),  # Warruwi 128km
    'IDR774': (-11.6494, 133.38, 0.25), # Warruwi 64km
    'IDR251': (-23.82, 133.90, 2.0),    # Alice Springs 512km
    'IDR252': (-23.82, 133.90, 1.0),    # Alice Springs 256km
    'IDR253': (-23.82, 133.90, 0.5),    # Alice Springs 128km
    'IDR254': (-23.82, 133.90, 0.25),   # Alice Springs 64km

    # Western Australia
    'IDR391': (-18.23, 127.66, 2.0),    # Halls Creek 512km
    'IDR392': (-18.23, 127.66, 1.0),    # Halls Creek 256km
    'IDR393': (-18.23, 127.66, 0.5),    # Halls Creek 128km
    'IDR394': (-18.23, 127.66, 0.25),   # Halls Creek 64km
    'IDR171': (-17.95, 122.23, 2.0),    # Broome 512km
    'IDR172': (-17.95, 122.23, 1.0),    # Broome 256km
    'IDR173': (-17.95, 122.23, 0.5),    # Broome 128km
    'IDR174': (-17.95, 122.23, 0.25),   # Broome 64km
    'IDR161': (-20.37, 118.63, 2.0),    # Port Hedland 512km
    'IDR162': (-20.37, 118.63, 1.0),    # Port Hedland 256km
    'IDR163': (-20.37, 118.63, 0.5),    # Port Hedland 128km
    'IDR164': (-20.37, 118.63, 0.25),   # Port Hedland 64km
    'IDR1111': (-20.99, 116.87, 2.0),   # Karratha 512km
    'IDR1112': (-20.99, 116.87, 1.0),   # Karratha 256km
    'IDR1113': (-20.99, 116.87, 0.5),   # Karratha 128km
    'IDR1114': (-20.99, 116.87, 0.25),  # Karratha 64km
    'IDR151': (-20.65, 116.69, 2.0),    # Dampier 512km
    'IDR152': (-20.65, 116.69, 1.0),    # Dampier 256km
    'IDR153': (-20.65, 116.69, 0.5),    # Dampier 128km
    'IDR154': (-20.65, 116.69, 0.25),   # Dampier 64km
    'IDR051': (-24.88, 113.67, 2.0),    # Carnarvon 512km
    'IDR052': (-24.88, 113.67, 1.0),    # Carnarvon 256km
    'IDR053': (-24.88, 113.67, 0.5),    # Carnarvon 128km
    'IDR054': (-24.88, 113.67, 0.25),   # Carnarvon 64km
    'IDR1141': (-24.88, 113.67, 2.0),   # Carnarvon (alt product ID) 512km
    'IDR1142': (-24.88, 113.67, 1.0),   # Carnarvon 256km
    'IDR1143': (-24.88, 113.67, 0.5),   # Carnarvon 128km
    'IDR1144': (-24.88, 113.67, 0.25),  # Carnarvon 64km
    'IDR061': (-28.80, 114.70, 2.0),    # Geraldton 512km
    'IDR062': (-28.80, 114.70, 1.0),    # Geraldton 256km
    'IDR063': (-28.80, 114.70, 0.5),    # Geraldton 128km
    'IDR064': (-28.80, 114.70, 0.25),   # Geraldton 64km
    'IDR291': (-22.10, 114.00, 2.0),    # Learmonth 512km
    'IDR292': (-22.10, 114.00, 1.0),    # Learmonth 256km
    'IDR293': (-22.10, 114.00, 0.5),    # Learmonth 128km
    'IDR294': (-22.10, 114.00, 0.25),   # Learmonth 64km
    'IDR701': (-32.39, 115.87, 2.0),    # Perth (Serpentine) 512km
    'IDR702': (-32.39, 115.87, 1.0),    # Perth 256km
    'IDR703': (-32.39, 115.87, 0.5),    # Perth 128km
    'IDR704': (-32.39, 115.87, 0.25),   # Perth 64km
    'IDR261': (-31.93, 115.98, 2.0),    # Perth Airport 512km
    'IDR262': (-31.93, 115.98, 1.0),    # Perth Airport 256km
    'IDR263': (-31.93, 115.98, 0.5),    # Perth Airport 128km
    'IDR264': (-31.93, 115.98, 0.25),   # Perth Airport 64km
    'IDR311': (-34.94, 117.80, 2.0),    # Albany 512km
    'IDR312': (-34.94, 117.80, 1.0),    # Albany 256km
    'IDR313': (-34.94, 117.80, 0.5),    # Albany 128km
    'IDR314': (-34.94, 117.80, 0.25),   # Albany 64km
    'IDR321': (-33.83, 121.89, 2.0),    # Esperance 512km
    'IDR322': (-33.83, 121.89, 1.0),    # Esperance 256km
    'IDR323': (-33.83, 121.89, 0.5),    # Esperance 128km
    'IDR324': (-33.83, 121.89, 0.25),   # Esperance 64km
    'IDR071': (-15.45, 128.12, 2.0),    # Wyndham 512km
    'IDR072': (-15.45, 128.12, 1.0),    # Wyndham 256km
    'IDR073': (-15.45, 128.12, 0.5),    # Wyndham 128km
    'IDR074': (-15.45, 128.12, 0.25),   # Wyndham 64km
    'IDR441': (-25.03, 128.30, 2.0),    # Giles 512km
    'IDR442': (-25.03, 128.30, 1.0),    # Giles 256km
    'IDR443': (-25.03, 128.30, 0.5),    # Giles 128km
    'IDR444': (-25.03, 128.30, 0.25),   # Giles 64km
    'IDR481': (-30.79, 121.45, 2.0),    # Kalgoorlie-Boulder 512km
    'IDR482': (-30.79, 121.45, 1.0),    # Kalgoorlie-Boulder 256km
    'IDR483': (-30.79, 121.45, 0.5),    # Kalgoorlie-Boulder 128km
    'IDR484': (-30.79, 121.45, 0.25),   # Kalgoorlie-Boulder 64km
    'IDR581': (-31.78, 117.95, 2.0),    # South Doodlakine 512km
    'IDR582': (-31.78, 117.95, 1.0),    # South Doodlakine 256km
    'IDR583': (-31.78, 117.95, 0.5),    # South Doodlakine 128km
    'IDR584': (-31.78, 117.95, 0.25),   # South Doodlakine 64km
    'IDR791': (-30.36, 116.29, 2.0),    # Watheroo 512km
    'IDR792': (-30.36, 116.29, 1.0),    # Watheroo 256km
    'IDR793': (-30.36, 116.29, 0.5),    # Watheroo 128km
    'IDR794': (-30.36, 116.29, 0.25),   # Watheroo 64km
    'IDR381': (-33.097, 119.009, 2.0),  # Newdegate 512km
    'IDR382': (-33.097, 119.009, 1.0),  # Newdegate 256km
    'IDR383': (-33.097, 119.009, 0.5),  # Newdegate 128km
    'IDR384': (-33.097, 119.009, 0.25), # Newdegate 64km

    # South Australia
    'IDR271': (-31.16, 136.80, 2.0),    # Woomera 512km
    'IDR272': (-31.16, 136.80, 1.0),    # Woomera 256km
    'IDR273': (-31.16, 136.80, 0.5),    # Woomera 128km
    'IDR274': (-31.16, 136.80, 0.25),   # Woomera 64km
    'IDR641': (-34.617, 138.469, 2.0),  # Adelaide (Buckland Park) 512km
    'IDR642': (-34.617, 138.469, 1.0),  # Adelaide 256km
    'IDR643': (-34.617, 138.469, 0.5),  # Adelaide 128km
    'IDR644': (-34.617, 138.469, 0.25), # Adelaide 64km
    'IDR461': (-35.33, 138.50, 2.0),    # Adelaide (Sellicks Hill) 512km
    'IDR462': (-35.33, 138.50, 1.0),    # Adelaide (Sellicks Hill) 256km
    'IDR463': (-35.33, 138.50, 0.5),    # Adelaide (Sellicks Hill) 128km
    'IDR464': (-35.33, 138.50, 0.25),   # Adelaide (Sellicks Hill) 64km
    'IDR141': (-37.75, 140.77, 2.0),    # Mt Gambier 512km
    'IDR142': (-37.75, 140.77, 1.0),    # Mt Gambier 256km
    'IDR143': (-37.75, 140.77, 0.5),    # Mt Gambier 128km
    'IDR144': (-37.75, 140.77, 0.25),   # Mt Gambier 64km
    'IDR331': (-32.13, 133.70, 2.0),    # Ceduna 512km
    'IDR332': (-32.13, 133.70, 1.0),    # Ceduna 256km
    'IDR333': (-32.13, 133.70, 0.5),    # Ceduna 128km
    'IDR334': (-32.13, 133.70, 0.25),   # Ceduna 64km

    # Victoria
    'IDR971': (-34.28, 141.59, 2.0),    # Mildura 512km
    'IDR972': (-34.28, 141.59, 1.0),    # Mildura 256km
    'IDR973': (-34.28, 141.59, 0.5),    # Mildura 128km
    'IDR974': (-34.28, 141.59, 0.25),   # Mildura 64km
    'IDR951': (-35.99, 142.01, 2.0),    # Rainbow 512km
    'IDR952': (-35.99, 142.01, 1.0),    # Rainbow 256km
    'IDR953': (-35.99, 142.01, 0.5),    # Rainbow 128km
    'IDR954': (-35.99, 142.01, 0.25),   # Rainbow 64km
    'IDR491': (-36.03, 146.03, 2.0),    # Yarrawonga 512km
    'IDR492': (-36.03, 146.03, 1.0),    # Yarrawonga 256km
    'IDR493': (-36.03, 146.03, 0.5),    # Yarrawonga 128km
    'IDR494': (-36.03, 146.03, 0.25),   # Yarrawonga 64km
    'IDR021': (-37.86, 144.76, 2.0),    # Melbourne 512km
    'IDR022': (-37.86, 144.76, 1.0),    # Melbourne 256km
    'IDR023': (-37.86, 144.76, 0.5),    # Melbourne 128km
    'IDR024': (-37.86, 144.76, 0.25),   # Melbourne 64km
    'IDR681': (-37.89, 147.56, 2.0),    # Bairnsdale 512km
    'IDR682': (-37.89, 147.56, 1.0),    # Bairnsdale 256km
    'IDR683': (-37.89, 147.56, 0.5),    # Bairnsdale 128km
    'IDR684': (-37.89, 147.56, 0.25),   # Bairnsdale 64km

    # Tasmania
    'IDR761': (-43.1122, 147.8061, 2.0),  # Hobart (Mt Koonya) 512km
    'IDR762': (-43.1122, 147.8061, 1.0),  # Hobart 256km
    'IDR763': (-43.1122, 147.8061, 0.5),  # Hobart 128km
    'IDR764': (-43.1122, 147.8061, 0.25), # Hobart 64km
    'IDR371': (-42.83, 147.51, 2.0),      # Hobart Airport 512km
    'IDR372': (-42.83, 147.51, 1.0),      # Hobart Airport 256km
    'IDR373': (-42.83, 147.51, 0.5),      # Hobart Airport 128km
    'IDR374': (-42.83, 147.51, 0.25),     # Hobart Airport 64km
    'IDR521': (-41.181, 145.579, 2.0),    # West Takone 512km
    'IDR522': (-41.181, 145.579, 1.0),    # West Takone 256km
    'IDR523': (-41.181, 145.579, 0.5),    # West Takone 128km
    'IDR524': (-41.181, 145.579, 0.25),   # West Takone 64km

    # New South Wales
    'IDR551': (-35.17, 147.47, 2.0),    # Wagga Wagga 512km
    'IDR552': (-35.17, 147.47, 1.0),    # Wagga Wagga 256km
    'IDR553': (-35.17, 147.47, 0.5),    # Wagga Wagga 128km
    'IDR554': (-35.17, 147.47, 0.25),   # Wagga Wagga 64km
    'IDR941': (-33.55, 145.52, 2.0),    # Hillston 512km
    'IDR942': (-33.55, 145.52, 1.0),    # Hillston 256km
    'IDR943': (-33.55, 145.52, 0.5),    # Hillston 128km
    'IDR944': (-33.55, 145.52, 0.25),   # Hillston 64km
    'IDR961': (-32.74, 148.70, 2.0),    # Yeoval 512km
    'IDR962': (-32.74, 148.70, 1.0),    # Yeoval 256km
    'IDR963': (-32.74, 148.70, 0.5),    # Yeoval 128km
    'IDR964': (-32.74, 148.70, 0.25),   # Yeoval 64km
    'IDR711': (-33.701, 151.210, 2.0),  # Sydney (Terrey Hills) 512km
    'IDR712': (-33.701, 151.210, 1.0),  # Sydney 256km
    'IDR713': (-33.701, 151.210, 0.5),  # Sydney 128km
    'IDR714': (-33.701, 151.210, 0.25), # Sydney 64km
    'IDR041': (-32.730, 152.027, 2.0),  # Newcastle (Lemon Tree Passage) 512km
    'IDR042': (-32.730, 152.027, 1.0),  # Newcastle 256km
    'IDR043': (-32.730, 152.027, 0.5),  # Newcastle 128km
    'IDR044': (-32.730, 152.027, 0.25), # Newcastle 64km
    'IDR281': (-29.62, 152.97, 2.0),    # Grafton 512km
    'IDR282': (-29.62, 152.97, 1.0),    # Grafton 256km
    'IDR283': (-29.62, 152.97, 0.5),    # Grafton 128km
    'IDR284': (-29.62, 152.97, 0.25),   # Grafton 64km
    'IDR401': (-35.66, 149.51, 2.0),    # Canberra (Captain's Flat) 512km
    'IDR402': (-35.66, 149.51, 1.0),    # Canberra 256km
    'IDR403': (-35.66, 149.51, 0.5),    # Canberra 128km
    'IDR404': (-35.66, 149.51, 0.25),   # Canberra 64km
    'IDR031': (-34.264, 150.874, 2.0),  # Wollongong (Appin) 512km
    'IDR032': (-34.264, 150.874, 1.0),  # Wollongong 256km
    'IDR033': (-34.264, 150.874, 0.5),  # Wollongong 128km
    'IDR034': (-34.264, 150.874, 0.25), # Wollongong 64km
    'IDR531': (-29.50, 149.85, 2.0),    # Moree 512km
    'IDR532': (-29.50, 149.85, 1.0),    # Moree 256km
    'IDR533': (-29.50, 149.85, 0.5),    # Moree 128km
    'IDR534': (-29.50, 149.85, 0.25),   # Moree 64km
    'IDR691': (-31.0240, 150.1915, 2.0),  # Namoi (Blackjack Mountain) 512km
    'IDR692': (-31.0240, 150.1915, 1.0),  # Namoi 256km
    'IDR693': (-31.0240, 150.1915, 0.5),  # Namoi 128km
    'IDR694': (-31.0240, 150.1915, 0.25), # Namoi 64km
    'IDR931': (-29.96, 146.81, 2.0),    # Brewarrina 512km
    'IDR932': (-29.96, 146.81, 1.0),    # Brewarrina 256km
    'IDR933': (-29.96, 146.81, 0.5),    # Brewarrina 128km
    'IDR934': (-29.96, 146.81, 0.25),   # Brewarrina 64km
    'IDR621': (-29.033, 167.933, 2.0),  # Norfolk Island 512km
    'IDR622': (-29.033, 167.933, 1.0),  # Norfolk Island 256km
    'IDR623': (-29.033, 167.933, 0.5),  # Norfolk Island 128km
    'IDR624': (-29.033, 167.933, 0.25), # Norfolk Island 64km

    # Queensland
    'IDR661': (-27.718, 153.240, 2.0),  # Brisbane (Mt Stapylton) 512km
    'IDR662': (-27.718, 153.240, 1.0),  # Brisbane 256km
    'IDR663': (-27.718, 153.240, 0.5),  # Brisbane 128km
    'IDR664': (-27.718, 153.240, 0.25), # Brisbane 64km
    'IDR501': (-27.61, 152.54, 2.0),    # Marburg 512km
    'IDR502': (-27.61, 152.54, 1.0),    # Marburg 256km
    'IDR503': (-27.61, 152.54, 0.5),    # Marburg 128km
    'IDR504': (-27.61, 152.54, 0.25),   # Marburg 64km
    'IDR1081': (-27.2740, 151.9930, 2.0),  # Toowoomba 512km
    'IDR1082': (-27.2740, 151.9930, 1.0),  # Toowoomba 256km
    'IDR1083': (-27.2740, 151.9930, 0.5),  # Toowoomba 128km
    'IDR1084': (-27.2740, 151.9930, 0.25), # Toowoomba 64km
    'IDR081': (-25.957, 152.577, 2.0),  # Gympie (Mt Kanigan) 512km
    'IDR082': (-25.957, 152.577, 1.0),  # Gympie 256km
    'IDR083': (-25.957, 152.577, 0.5),  # Gympie 128km
    'IDR084': (-25.957, 152.577, 0.25), # Gympie 64km
    'IDR231': (-23.86, 151.26, 2.0),    # Gladstone 512km
    'IDR232': (-23.86, 151.26, 1.0),    # Gladstone 256km
    'IDR233': (-23.86, 151.26, 0.5),    # Gladstone 128km
    'IDR234': (-23.86, 151.26, 0.25),   # Gladstone 64km
    'IDR721': (-23.5494, 148.2392, 2.0),  # Emerald 512km
    'IDR722': (-23.5494, 148.2392, 1.0),  # Emerald 256km
    'IDR723': (-23.5494, 148.2392, 0.5),  # Emerald 128km
    'IDR724': (-23.5494, 148.2392, 0.25), # Emerald 64km
    'IDR1071': (-20.75, 143.14, 2.0),   # Richmond 512km
    'IDR1072': (-20.75, 143.14, 1.0),   # Richmond 256km
    'IDR1073': (-20.75, 143.14, 0.5),   # Richmond 128km
    'IDR1074': (-20.75, 143.14, 0.25),  # Richmond 64km
    'IDR1061': (-19.406, 146.77, 2.0),  # Townsville (Hervey Range) 512km
    'IDR1062': (-19.406, 146.77, 1.0),  # Townsville 256km
    'IDR1063': (-19.406, 146.77, 0.5),  # Townsville 128km
    'IDR1064': (-19.406, 146.77, 0.25), # Townsville 64km
    'IDR741': (-18.99, 144.99, 2.0),    # Greenvale 512km
    'IDR742': (-18.99, 144.99, 1.0),    # Greenvale 256km
    'IDR743': (-18.99, 144.99, 0.5),    # Greenvale 128km
    'IDR744': (-18.99, 144.99, 0.25),   # Greenvale 64km
    'IDR191': (-16.82, 145.68, 2.0),    # Cairns (Saddle Mountain) 512km
    'IDR192': (-16.82, 145.68, 1.0),    # Cairns 256km
    'IDR193': (-16.82, 145.68, 0.5),    # Cairns 128km
    'IDR194': (-16.82, 145.68, 0.25),   # Cairns 64km
    'IDR411': (-16.288, 149.965, 2.0),  # Willis Island 512km
    'IDR412': (-16.288, 149.965, 1.0),  # Willis Island 256km
    'IDR413': (-16.288, 149.965, 0.5),  # Willis Island 128km
    'IDR414': (-16.288, 149.965, 0.25), # Willis Island 64km
    'IDR221': (-21.12, 149.22, 2.0),    # Mackay (Mt Bassett) 512km
    'IDR222': (-21.12, 149.22, 1.0),    # Mackay 256km
    'IDR223': (-21.12, 149.22, 0.5),    # Mackay 128km
    'IDR224': (-21.12, 149.22, 0.25),   # Mackay 64km
    'IDR241': (-19.88, 148.08, 2.0),    # Bowen (Abbot Point) 512km
    'IDR242': (-19.88, 148.08, 1.0),    # Bowen 256km
    'IDR243': (-19.88, 148.08, 0.5),    # Bowen 128km
    'IDR244': (-19.88, 148.08, 0.25),   # Bowen 64km
    'IDR561': (-23.43, 144.29, 2.0),    # Longreach 512km
    'IDR562': (-23.43, 144.29, 1.0),    # Longreach 256km
    'IDR563': (-23.43, 144.29, 0.5),    # Longreach 128km
    'IDR564': (-23.43, 144.29, 0.25),   # Longreach 64km
    'IDR751': (-20.7114, 139.5553, 2.0),  # Mount Isa 512km
    'IDR752': (-20.7114, 139.5553, 1.0),  # Mount Isa 256km
    'IDR753': (-20.7114, 139.5553, 0.5),  # Mount Isa 128km
    'IDR754': (-20.7114, 139.5553, 0.25), # Mount Isa 64km
    'IDR361': (-16.67, 139.17, 2.0),    # Mornington Island 512km
    'IDR362': (-16.67, 139.17, 1.0),    # Mornington Island 256km
    'IDR363': (-16.67, 139.17, 0.5),    # Mornington Island 128km
    'IDR364': (-16.67, 139.17, 0.25),   # Mornington Island 64km
    'IDR781': (-12.67, 141.92, 2.0),    # Weipa 512km
    'IDR782': (-12.67, 141.92, 1.0),    # Weipa 256km
    'IDR783': (-12.67, 141.92, 0.5),    # Weipa 128km
    'IDR784': (-12.67, 141.92, 0.25),   # Weipa 64km
    'IDR671': (-26.44, 147.35, 2.0),    # Warrego 512km
    'IDR672': (-26.44, 147.35, 1.0),    # Warrego 256km
    'IDR673': (-26.44, 147.35, 0.5),    # Warrego 128km
    'IDR674': (-26.44, 147.35, 0.25),   # Warrego 64km
    'IDR981': (-25.696, 149.898, 2.0),  # Taroom 512km
    'IDR982': (-25.696, 149.898, 1.0),  # Taroom 256km
    'IDR983': (-25.696, 149.898, 0.5),  # Taroom 128km
    'IDR984': (-25.696, 149.898, 0.25), # Taroom 64km
}
