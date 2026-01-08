"""GO Transit Route and Station Reference Data"""

# GO Transit Route Names (from GTFS)
GO_ROUTES = {
    # Train Lines
    "ST": "Stouffville",
    "RH": "Richmond Hill",
    "MI": "Milton",
    "LW": "Lakeshore West",
    "LE": "Lakeshore East",
    "KI": "Kitchener",
    "BR": "Barrie",
    "GT": "GO Train",

    # Bus Routes
    "96": "Oshawa / Finch Express",
    "94": "Pickering / Square One",
    "92": "Oshawa / Yorkdale",
    "90": "Lakeshore East",
    "88": "Peterborough / Oshawa",
    "71": "Stouffville",
    "70": "Uxbridge / Mount Joy",
    "68": "Barrie / Newmarket",
    "67": "Keswick / North York",
    "65": "Newmarket / Toronto",
    "61": "Richmond Hill",
    "56": "Oshawa / Oakville",
    "52": "Oshawa / Hwy 407 Terminal",
    "48": "Guelph / Hwy 407 Terminal",
    "47": "Hamilton / Hwy 407 Terminal",
    "41": "Hamilton / Pickering",
    "40": "Hamilton / Richmond Hill",
    "38": "Bolton / Malton",
    "37": "Orangeville / Brampton",
    "36": "Brampton / North York Express",
    "33": "Guelph / North York",
    "32": "Brampton Trinity Common / North York",
    "31": "Guelph / Toronto",
    "30": "Kitchener / Bramalea",
    "29": "Guelph / Mississauga",
    "27": "Milton / North York",
    "25": "Waterloo / Mississauga",
    "22": "Milton / Oakville",
    "21": "Milton",
    "19": "Mississauga / North York",
    "18": "Lakeshore West",
    "17": "Waterloo / Hamilton",
    "16": "Hamilton / Toronto Express",
    "15": "Brantford / Aldershot",
    "12": "Niagara Falls / Toronto",
    "11": "Brock University"
}

# Major GO Transit Stations
GO_STATIONS = {
    "UN": "Union Station",
    "AL": "Aldershot GO",
    "BR": "Bramalea GO",
    "BU": "Burlington GO",
    "CL": "Clarkson GO",
    "ER": "Erindale GO",
    "EX": "Exhibition GO",
    "GU": "Guildwood GO",
    "KE": "Kennedy GO",
    "LI": "Liberty Village GO",
    "LO": "Long Branch GO",
    "MI": "Mimico GO",
    "OA": "Oakville GO",
    "PO": "Port Credit GO",
    "RO": "Rouge Hill GO",
    "SC": "Scarborough GO",
    "WE": "West Harbour GO",
    "AG": "Agincourt GO",
    "MI": "Milliken GO",
    "SC": "Scarborough GO",
    "UN": "Unionville GO",
    "CE": "Centennial GO",
    "MA": "Malton GO",
    "BR": "Bramalea GO",
    "MT": "Mount Pleasant GO",
    "DA": "Danforth GO",
    "GE": "Gerrard GO"
}

def get_route_name(route_code):
    """Get full route name from code"""
    return GO_ROUTES.get(str(route_code), f"Route {route_code}")

def get_station_name(station_code):
    """Get full station name from code"""
    return GO_STATIONS.get(str(station_code), station_code)
