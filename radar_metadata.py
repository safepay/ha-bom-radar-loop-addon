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
    'IDR631': (-12.457, 130.925, 4.0),  # Darwin (Berrimah) 512km
    'IDR632': (-12.457, 130.925, 2.0),  # Darwin 256km
    'IDR633': (-12.457, 130.925, 1.0),  # Darwin 128km
    'IDR634': (-12.457, 130.925, 0.5),  # Darwin 64km
    'IDR1121': (-12.27, 136.82, 4.0),   # Gove 512km
    'IDR1122': (-12.27, 136.82, 2.0),   # Gove 256km
    'IDR1123': (-12.27, 136.82, 1.0),   # Gove 128km
    'IDR1124': (-12.27, 136.82, 0.5),   # Gove 64km
    'IDR421': (-14.521, 132.378, 4.0),  # Katherine (Tindal) 512km
    'IDR422': (-14.521, 132.378, 2.0),  # Katherine 256km
    'IDR423': (-14.521, 132.378, 1.0),  # Katherine 128km
    'IDR424': (-14.521, 132.378, 0.5),  # Katherine 64km

    # Western Australia
    'IDR391': (-18.229, 127.66, 4.0),   # Halls Creek 512km
    'IDR392': (-18.229, 127.66, 2.0),   # Halls Creek 256km
    'IDR393': (-18.229, 127.66, 1.0),   # Halls Creek 128km
    'IDR394': (-18.229, 127.66, 0.5),   # Halls Creek 64km
    'IDR171': (-17.951, 122.235, 4.0),  # Broome 512km
    'IDR172': (-17.951, 122.235, 2.0),  # Broome 256km
    'IDR173': (-17.951, 122.235, 1.0),  # Broome 128km
    'IDR174': (-17.951, 122.235, 0.5),  # Broome 64km
    'IDR161': (-20.372, 118.631, 4.0),  # Port Hedland 512km
    'IDR162': (-20.372, 118.631, 2.0),  # Port Hedland 256km
    'IDR163': (-20.372, 118.631, 1.0),  # Port Hedland 128km
    'IDR164': (-20.372, 118.631, 0.5),  # Port Hedland 64km
    'IDR1111': (-20.7375, 116.8467, 4.0), # Karratha 512km
    'IDR1112': (-20.7375, 116.8467, 2.0), # Karratha 256km
    'IDR1113': (-20.7375, 116.8467, 1.0), # Karratha 128km
    'IDR1114': (-20.7375, 116.8467, 0.5), # Karratha 64km
    'IDR1141': (-24.888, 113.671, 4.0),  # Carnarvon 512km
    'IDR1142': (-24.888, 113.671, 2.0),  # Carnarvon 256km
    'IDR1143': (-24.888, 113.671, 1.0),  # Carnarvon 128km
    'IDR1144': (-24.888, 113.671, 0.5),  # Carnarvon 64km
    'IDR061': (-28.778333, 114.614444, 4.0), # Geraldton 512km
    'IDR062': (-28.778333, 114.614444, 2.0), # Geraldton 256km
    'IDR063': (-28.778333, 114.614444, 1.0), # Geraldton 128km
    'IDR064': (-28.778333, 114.614444, 0.5), # Geraldton 64km
    'IDR701': (-32.393, 115.867, 4.0),   # Perth (Serpentine) 512km
    'IDR702': (-32.393, 115.867, 2.0),   # Perth 256km
    'IDR703': (-32.393, 115.867, 1.0),   # Perth 128km
    'IDR704': (-32.393, 115.867, 0.5),   # Perth 64km
    'IDR311': (-34.941806, 117.816361, 4.0), # Albany 512km
    'IDR312': (-34.941806, 117.816361, 2.0), # Albany 256km
    'IDR313': (-34.941806, 117.816361, 1.0), # Albany 128km
    'IDR314': (-34.941806, 117.816361, 0.5), # Albany 64km
    'IDR321': (-33.859444, 121.891111, 4.0), # Esperance 512km
    'IDR322': (-33.859444, 121.891111, 2.0), # Esperance 256km
    'IDR323': (-33.859444, 121.891111, 1.0), # Esperance 128km
    'IDR324': (-33.859444, 121.891111, 0.5), # Esperance 64km

    # South Australia
    'IDR271': (-31.144, 136.818, 4.0),   # Woomera 512km
    'IDR272': (-31.144, 136.818, 2.0),   # Woomera 256km
    'IDR273': (-31.144, 136.818, 1.0),   # Woomera 128km
    'IDR274': (-31.144, 136.818, 0.5),   # Woomera 64km
    'IDR641': (-34.617, 138.469, 4.0),   # Adelaide (Buckland Park) 512km
    'IDR642': (-34.617, 138.469, 2.0),   # Adelaide 256km
    'IDR643': (-34.617, 138.469, 1.0),   # Adelaide 128km
    'IDR644': (-34.617, 138.469, 0.5),   # Adelaide 64km
    'IDR141': (-37.747, 140.774, 4.0),   # Mt Gambier 512km
    'IDR142': (-37.747, 140.774, 2.0),   # Mt Gambier 256km
    'IDR143': (-37.747, 140.774, 1.0),   # Mt Gambier 128km
    'IDR144': (-37.747, 140.774, 0.5),   # Mt Gambier 64km

    # Victoria
    'IDR971': (-34.287111, 141.598194, 4.0), # Mildura 512km
    'IDR972': (-34.287111, 141.598194, 2.0), # Mildura 256km
    'IDR973': (-34.287111, 141.598194, 1.0), # Mildura 128km
    'IDR974': (-34.287111, 141.598194, 0.5), # Mildura 64km
    'IDR951': (-35.997556, 142.013306, 4.0), # Rainbow 512km
    'IDR952': (-35.997556, 142.013306, 2.0), # Rainbow 256km
    'IDR953': (-35.997556, 142.013306, 1.0), # Rainbow 128km
    'IDR954': (-35.997556, 142.013306, 0.5), # Rainbow 64km
    'IDR021': (-37.855222, 144.755417, 4.0), # Melbourne 512km
    'IDR022': (-37.855222, 144.755417, 2.0), # Melbourne 256km
    'IDR023': (-37.855222, 144.755417, 1.0), # Melbourne 128km
    'IDR024': (-37.855222, 144.755417, 0.5), # Melbourne 64km
    'IDR681': (-37.885, 147.567, 4.0),   # Bairnsdale 512km
    'IDR682': (-37.885, 147.567, 2.0),   # Bairnsdale 256km
    'IDR683': (-37.885, 147.567, 1.0),   # Bairnsdale 128km
    'IDR684': (-37.885, 147.567, 0.5),   # Bairnsdale 64km

    # Tasmania
    'IDR761': (-42.832, 147.502, 4.0),   # Hobart 512km
    'IDR762': (-42.832, 147.502, 2.0),   # Hobart 256km
    'IDR763': (-42.832, 147.502, 1.0),   # Hobart 128km
    'IDR764': (-42.832, 147.502, 0.5),   # Hobart 64km

    # New South Wales
    'IDR551': (-35.165, 147.457, 4.0),   # Wagga Wagga 512km
    'IDR552': (-35.165, 147.457, 2.0),   # Wagga Wagga 256km
    'IDR553': (-35.165, 147.457, 1.0),   # Wagga Wagga 128km
    'IDR554': (-35.165, 147.457, 0.5),   # Wagga Wagga 64km
    'IDR941': (-33.552194, 145.52861, 4.0), # Hillston 512km
    'IDR942': (-33.552194, 145.52861, 2.0), # Hillston 256km
    'IDR943': (-33.552194, 145.52861, 1.0), # Hillston 128km
    'IDR944': (-33.552194, 145.52861, 0.5), # Hillston 64km
    'IDR961': (-32.744472, 148.708083, 4.0), # Yeoval 512km
    'IDR962': (-32.744472, 148.708083, 2.0), # Yeoval 256km
    'IDR963': (-32.744472, 148.708083, 1.0), # Yeoval 128km
    'IDR964': (-32.744472, 148.708083, 0.5), # Yeoval 64km
    'IDR711': (-33.70083, 151.209417, 4.0),  # Sydney (Terrey Hills) 512km
    'IDR712': (-33.70083, 151.209417, 2.0),  # Sydney 256km
    'IDR713': (-33.70083, 151.209417, 1.0),  # Sydney 128km
    'IDR714': (-33.70083, 151.209417, 0.5),  # Sydney 64km
    'IDR041': (-32.852, 151.385, 4.0),   # Newcastle 512km
    'IDR042': (-32.852, 151.385, 2.0),   # Newcastle 256km
    'IDR043': (-32.852, 151.385, 1.0),   # Newcastle 128km
    'IDR044': (-32.852, 151.385, 0.5),   # Newcastle 64km
    'IDR281': (-29.623, 152.982, 4.0),   # Grafton 512km
    'IDR282': (-29.623, 152.982, 2.0),   # Grafton 256km
    'IDR283': (-29.623, 152.982, 1.0),   # Grafton 128km
    'IDR284': (-29.623, 152.982, 0.5),   # Grafton 64km

    # Queensland
    'IDR661': (-27.501667, 153.116389, 4.0), # Brisbane (Mt Stapylton) 512km
    'IDR662': (-27.501667, 153.116389, 2.0), # Brisbane 256km
    'IDR663': (-27.501667, 153.116389, 1.0), # Brisbane 128km
    'IDR664': (-27.501667, 153.116389, 0.5), # Brisbane 64km
    'IDR501': (-27.658056, 152.595556, 4.0), # Marburg 512km
    'IDR502': (-27.658056, 152.595556, 2.0), # Marburg 256km
    'IDR503': (-27.658056, 152.595556, 1.0), # Marburg 128km
    'IDR504': (-27.658056, 152.595556, 0.5), # Marburg 64km
    'IDR1081': (-27.56, 151.95, 4.0),    # Toowoomba 512km
    'IDR1082': (-27.56, 151.95, 2.0),    # Toowoomba 256km
    'IDR1083': (-27.56, 151.95, 1.0),    # Toowoomba 128km
    'IDR1084': (-27.56, 151.95, 0.5),    # Toowoomba 64km
    'IDR081': (-26.183, 152.667, 4.0),   # Gympie 512km
    'IDR082': (-26.183, 152.667, 2.0),   # Gympie 256km
    'IDR083': (-26.183, 152.667, 1.0),   # Gympie 128km
    'IDR084': (-26.183, 152.667, 0.5),   # Gympie 64km
    'IDR231': (-23.847, 151.263, 4.0),   # Gladstone 512km
    'IDR232': (-23.847, 151.263, 2.0),   # Gladstone 256km
    'IDR233': (-23.847, 151.263, 1.0),   # Gladstone 128km
    'IDR234': (-23.847, 151.263, 0.5),   # Gladstone 64km
    'IDR721': (-23.534, 148.164, 4.0),   # Emerald 512km
    'IDR722': (-23.534, 148.164, 2.0),   # Emerald 256km
    'IDR723': (-23.534, 148.164, 1.0),   # Emerald 128km
    'IDR724': (-23.534, 148.164, 0.5),   # Emerald 64km
    'IDR1071': (-20.702, 143.143, 4.0),  # Richmond 512km
    'IDR1072': (-20.702, 143.143, 2.0),  # Richmond 256km
    'IDR1073': (-20.702, 143.143, 1.0),  # Richmond 128km
    'IDR1074': (-20.702, 143.143, 0.5),  # Richmond 64km
    'IDR1061': (-19.406, 146.77, 4.0),   # Townsville 512km
    'IDR1062': (-19.406, 146.77, 2.0),   # Townsville 256km
    'IDR1063': (-19.406, 146.77, 1.0),   # Townsville 128km
    'IDR1064': (-19.406, 146.77, 0.5),   # Townsville 64km
    'IDR741': (-19.252222, 145.018056, 4.0), # Greenvale 512km
    'IDR742': (-19.252222, 145.018056, 2.0), # Greenvale 256km
    'IDR743': (-19.252222, 145.018056, 1.0), # Greenvale 128km
    'IDR744': (-19.252222, 145.018056, 0.5), # Greenvale 64km
    'IDR191': (-16.885, 145.755, 4.0),   # Cairns 512km
    'IDR192': (-16.885, 145.755, 2.0),   # Cairns 256km
    'IDR193': (-16.885, 145.755, 1.0),   # Cairns 128km
    'IDR194': (-16.885, 145.755, 0.5),   # Cairns 64km
    'IDR411': (-16.289, 149.972, 4.0),   # Willis Island 512km
    'IDR412': (-16.289, 149.972, 2.0),   # Willis Island 256km
    'IDR413': (-16.289, 149.972, 1.0),   # Willis Island 128km
    'IDR414': (-16.289, 149.972, 0.5),   # Willis Island 64km

    # Australian Capital Territory
    'IDR401': (-35.3075, 149.191, 4.0),  # Canberra 512km
    'IDR402': (-35.3075, 149.191, 2.0),  # Canberra 256km
    'IDR403': (-35.3075, 149.191, 1.0),  # Canberra 128km
    'IDR404': (-35.3075, 149.191, 0.5),  # Canberra 64km
}
