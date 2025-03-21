import dill
from Scraping import Series
import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
from Points import Match
from collections import OrderedDict
import json


def excel_to_dict(file_path):
    # Read all sheets into a dictionary of DataFrames
    excel_data = pd.read_excel(file_path, sheet_name=None, index_col=0)  

    parsed_dict = {}

    for sheet_name, df in excel_data.items():
        # Convert DataFrame back to its original structure
        if df.index.dtype == 'O':  # If index is non-integer, it's likely a dictionary
            parsed_dict[sheet_name] = df.to_dict(orient='index')  
        else:  # Otherwise, assume it was originally a list
            parsed_dict[sheet_name] = df.to_dict(orient='records')

    return parsed_dict

def op_caps(url):
    #url = "https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/stats" #ipl-2025-1449924
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
    }

    # Send an HTTP request
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")  # Parse the HTML
    stats = soup.find_all('div',class_="ds-p-0")
    batsmen = stats[1]
    orange_cap = batsmen.find('span',class_="ds-text-title-xs ds-font-bold").text.strip()
    bowlers = stats[2]
    purple_cap = bowlers.find('span',class_="ds-text-title-xs ds-font-bold").text.strip()
    return orange_cap,purple_cap

def match_name_generator(url):
    match_name = match_url.split('/')[-2]
    parts = match_name.split('-')
    #print(parts)
    #print(match_name)
    #print(match_name)
    if 'eliminator' in parts:
        match_name = 'Eliminator'
    elif 'final' in parts:
        match_name = 'Final'
    elif 'qualifier' in parts:
        if '1' in parts:
            match_name = "Qualifier 1"
        else:
            match_name = "Qualifier 2"
    else:
        match_name = " ".join(parts[:-3])
    match_name = match_name.title()
    match_name = match_name.replace('Vs','vs')
    for ipl_team in team_names_ff:
        if ipl_team in match_name:
            match_name = match_name.replace(ipl_team,team_names_sf[team_names_ff.index(ipl_team)])
    return match_name


begin = time.time()

team_names_sf = ["KKR","GT","MI","CSK","RR","RCB","PBKS","DC","SRH","LSG"]
team_names_ff = ["Kolkata Knight Riders", "Gujarat Titans", "Mumbai Indians", "Chennai Super Kings",
                 "Rajasthan Royals","Royal Challengers Bengaluru", "Punjab Kings","Delhi Capitals",
                 "Sunrisers Hyderabad","Lucknow Super Giants"]

cricbuzz_page_link = "https://www.cricbuzz.com/cricket-series/7607/indian-premier-league-2024/matches"
ipl24_url = "https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/match-schedule-fixtures-and-results"
database = "ipl2024matches.pkl"

ipl2024 = Series(ipl24_url, cricbuzz_page_link, database)  

match_objects = ipl2024.match_objects

# Define teams and boosters
teams = {
    'Gujju Gang': ['Varun Chakaravarthy','Travis Head','Rahul Chahar'],
    'Hilarious Hooligans': ['Yashasvi Jaiswal','Axar Patel','Hardik Pandya'],
    'Tormented Titans': ['Virat Kohli','Suryakumar Yadav','Abhishek Sharma'],
    'La Furia Roja': ['Shreyas Iyer','Sai Sudharsan','Jasprit Bumrah'],
    'Supa Jinx Strikas': ['Shubman Gill','Ruturaj Gaikwad','Mohit Sharma'],
    'Raging Raptors': ['KL Rahul','Venkatesh Iyer','Arshdeep Singh'],
    'The Travelling Bankers': ['Sunil Narine','Andre Russell','Chetan Sakariya']
}

boosters = {
    'Gujju Gang': {"match_url_1": "Triple Power"},
    'Hilarious Hooligans': {"match_url_1": "Double Power"},
    'Tormented Titans': {"match_url_1": "Batting Powerplay"},
    'La Furia Roja': {"match_url_1": "Bowling Powerplay"},
    'Supa Jinx Strikas': {"match_url_1": "Double Power", "match_url_2": "Triple Captain"},
    'Raging Raptors': {},
    'The Travelling Bankers': {}
}

orange_cap, purple_cap = op_caps("https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/stats")

# Processing matches
match_urls = list(match_objects.keys())
number_of_matches = len(match_objects)

for match_number in range(number_of_matches, 0, -1):
    match_url = match_urls[match_number - 1]
    match_object = match_objects[match_url]
    match_name = match_name_generator(match_url)
    
    match = Match(teams, match_object, boosters)
    
    team_breakdown = match.match_points_breakdown
    General_points_list = match.general_player_points_list

    print(f"\nMatch: {match_name}")
    print("General Player Points List:")
    print(General_points_list.to_string())  # Display full player points

    print("\nTeam Points Breakdown:")
    print(team_breakdown.to_string())  # Display full team breakdown
    
    # Updating team total points
    final_points = {}
    for team in list(team_breakdown.index):
        if team not in final_points:
            final_points[team] = {"Total Points": 0, "Orange Cap": 0, "Purple Cap": 0}
        
        final_points[team][match_name] = team_breakdown.loc[team, 'Total Points']
        final_points[team]["Total Points"] += final_points[team][match_name]

    print("\nUpdated Team Points:")
    for team, points in final_points.items():
        print(f"{team}: {points}")

# Processing Orange Cap and Purple Cap
for team in teams:
    orange_cap_points = 500 if orange_cap in teams[team] else 0
    purple_cap_points = 500 if purple_cap in teams[team] else 0
    
    total_points = final_points[team]["Total Points"] + orange_cap_points + purple_cap_points
    final_points[team]["Total Points"] = total_points
    final_points[team]["Orange Cap"] = orange_cap_points
    final_points[team]["Purple Cap"] = purple_cap_points

print("\nFinal Team Points (After Orange/Purple Cap Bonus):")
for team, points in sorted(final_points.items(), key=lambda x: x[1]['Total Points'], reverse=True):
    print(f"{team}: {points}")

end = time.time()
print(f"\nTotal Execution Time: {end - begin:.2f} seconds")
