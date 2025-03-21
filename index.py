from flask import Flask, jsonify
from flask_cors import CORS
import time
import pandas as pd
from Scraping import Series
from Points import Match
import dill
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
import json
import numpy as np

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for demonstration purposes

team_names_sf = ["KKR","GT","MI","CSK","RR","RCB","PBKS","DC","SRH","LSG"]
team_names_ff = ["Kolkata Knight Riders", "Gujarat Titans", "Mumbai Indians", "Chennai Super Kings","Rajasthan Royals","Royal Challengers Bengaluru", "Punjab Kings","Delhi Capitals","Sunrisers Hyderabad","Lucknow Super Giants"]

cricbuzz_page_link = "https://www.cricbuzz.com/cricket-series/7607/indian-premier-league-2024/matches"
ipl24_url = "https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/match-schedule-fixtures-and-results"
database = "ipl2024matches.pkl" #Change this later
ipl2024 = Series(ipl24_url,cricbuzz_page_link,database) #Change this later
match_objects = ipl2024.match_objects

entire_team_details={
    "Gujju Gang": {
        "players": [
            "Travis Head", "Varun Chakaravarthy", "Rahul Chahar", "Mukesh Choudhary", "Harshit Rana", 
            "Ishant Sharma", "Jaydev Unadkat", "Mukesh Kumar", "Abdul Samad", "Riyan Parag", 
            "Khaleel Ahmed", "Avesh Khan", "Faf Du Plessis", "Arjun Tendulkar", "Mohammed Shami", 
            "Shivam Dube", "Lockie Ferguson", "Josh Hazlewood", "Prabhsimran Singh", "Rishabh Pant", 
            "Corbin Bosch", "Mohammed Siraj", "Prasidh Krishna", "Marcus Stoinis", "Harpreet Brar", 
            "Rahmanullah Gurbaz", "Rashid Khan", "Washington Sundar"
        ],
        "captain": "NA",
        "vice_captain": "NA",
        "team_color": "#995C00"

    },
    "Hilarious Hooligans": {
        "players": [
            "Hardik Pandya", "Heinrich Klaasen", "Rinku Singh", "Nehal Wadhera", "Romario Shepherd", 
            "Manav Suthar", "Vijaykumar Vyshak", "Himmat Singh", "Ayush Badoni", "Liam Livingstone", 
            "Nathan Ellis", "Moeen Ali", "Karn Sharma", "Yashasvi Jaiswal", "Shimron Hetmyer", 
            "Axar Patel", "Mayank Yadav", "Abhinav Manohar", "Ashutosh Sharma", "Rachin Ravindra", 
            "Shahrukh Khan", "Anrich Nortje", "Mayank Markande", "Yuzvendra Chahal", "Tushar Deshpande", 
            "Noor Ahmad", "Kagiso Rabada", "Marco Jansen"
        ],
    "captain": "Yashasvi Jaiswal",
        "vice_captain": "Axar Patel",
        "team_color": "#FFFF00"
    },
    "Tormented Titans": {
        "players": [
            "Virat Kohli", "Abhishek Sharma", "Jitesh Sharma", "Harnoor Singh", "Bhuvneshwar Kumar", 
            "Abhishek Porel", "Angkrish Raghuvanshi", "Kuldeep Yadav", "David Miller", "Anuj Rawat", 
            "Josh Inglis", "Kumar Kartikeya", "Akash Deep", "Rahul Tewatia", "Ramandeep Singh", 
            "Sherfane Rutherford", "Glenn Maxwell", "Sandeep Sharma", "Suryakumar Yadav", "Shamar Joseph", 
            "Pat Cummins", "Quinton de Kock", "Ravichandran Ashwin"
        ],
           "captain": "Virat Kohli",
        "vice_captain": "Suryakumar Yadav",
        "team_color": "#FFA500"
    },
    "La Furia Roja": {
        "players": [
            "Jasprit Bumrah", "Sai Sudharsan", "Shreyas Iyer", "Swastik Chikara", "Rajvardhan Hangargekar", 
            "Manoj Bhandage", "Nitish Rana", "Rasikh Salam Dar", "Deepak Chahar", "MS Dhoni", 
            "Aaron Hardie", "Priyansh Arya", "Phil Salt", "Sameer Rizvi", "Mitchell Santner", 
            "Manish Pandey", "Suyash Sharma", "Kamlesh Nagarkoti", "Will Jacks", "Azmatullah Omarzai", 
            "Adam Zampa", "Spencer Johnson", "Jamie Overton", "Shashank Singh", "Rovman Powell", 
            "Suryansh Shedge", "Maheesh Theekshana"
        ],
        "captain": "Shreyas Iyer",
        "vice_captain": "Sai Sudharsan",
        "team_color": "#FF0000"
    },
    "Supa Jinx Strikas": {
        "players": [
            "Ruturaj Gaikwad", "Shubman Gill", "Mohit Sharma", "Sai Kishore", "Raj Bawa", 
            "Ishan Kishan", "Mitchell Marsh", "Nitish Kumar Reddy", "Karim Janat", "Yash Dayal", 
            "Bevon Jacobs", "Ryan Rickleton", "Rajat Patidar", "Tristan Stubbs", "Gerald Coetzee", 
            "Glenn Phillips", "Tim David", "Ravi Bishnoi", "Donovan Ferreira", "Jayant Yadav", 
            "Trent Boult", "Jofra Archer", "Akash Madhwal", "Darshan Nalkande", "Kwena Maphaka"
        ],
        "captain": "Shubman Gill",
        "vice_captain": "Ruturaj Gaikwad",
        "team_color": "#0000FF"
    },
    "Raging Raptors": {
        "players": [
            "KL Rahul", "Arshdeep Singh", "Aiden Markram", "Sachin Baby", "Dushmantha Chameera", 
            "Naman Dhir", "Karun Nair", "Wanindu Hasaranga", "Arshad Khan", "Devdutt Paddikal", 
            "Robin Minz", "Shahbaz Ahmed", "Mohsin Khan", "Krunal Pandya", "Ravindra Jadeja", 
            "Mitchell Starc", "Sanju Samson", "Jos Buttler", "Atharva Taide", "Musheer Khan", 
            "Devon Conway", "Venkatesh Iyer"
        ],
        "captain": "KL Rahul",
        "vice_captain": "Venkatesh Iyer",
        "team_color": "#008000"
    },
    "The Travelling Bankers": {
        "players": [
            "Andre Russell", "Sunil Narine", "Umran Malik", "T Natarajan", "Ajinkya Rahane", 
            "Shreyas Gopal", "Tilak Varma", "Vijay Shankar", "Shubham Dubey", "Anukul Roy", 
            "Deepak Hooda", "Harshal Patel", "Rahul Tripathi", "Lungi Ngidi", "Matheesha Pathirana", 
            "Vaibhav Arora", "Nicholas Pooran", "Jake Fraser-McGurk", "Sam Curran", "Rohit Sharma", 
            "Mujeeb Ur Rahman", "Anshul Kamboj", "Mahipal Lomror"
        ],
        "vice_captain": "Andre Russell",
        "captain": "Sunil Narine",
        "injured": ["Umran Malik"],
        "replacements": ["Chetan Sakariya"],
        "team_owner": "Aakash",
        "team_color": "#800080"
    }
}

boosters = {'Gujju Gang':{"https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/royal-challengers-bengaluru-vs-kolkata-knight-riders-10th-match-1422128/full-scorecard":"Triple Power"},
             'Hilarious Hooligans':{"https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/royal-challengers-bengaluru-vs-kolkata-knight-riders-10th-match-1422128/full-scorecard":"Double Power"},
             'Tormented Titans':{"https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/royal-challengers-bengaluru-vs-kolkata-knight-riders-10th-match-1422128/full-scorecard":"Batting Powerplay"},
             'La Furia Roja':{"https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/royal-challengers-bengaluru-vs-kolkata-knight-riders-10th-match-1422128/full-scorecard":"Bowling Powerplay"},
             'Supa Jinx Strikas':{"https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/royal-challengers-bengaluru-vs-kolkata-knight-riders-10th-match-1422128/full-scorecard":"Double Power","https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/kolkata-knight-riders-vs-sunrisers-hyderabad-3rd-match-1422121/full-scorecard":"Triple Captain"},
             'Raging Raptors':{},
             'The Travelling Bankers':{}
             } #for example Change this later
    

teams= {team: details["players"] for team, details in entire_team_details.items()}


@app.route('/last-match-and-overall-points', methods=['GET'])
def last_match_and_overall_points():
    match_urls = list(match_objects.keys())
    last_match_url = match_urls[-1]
    last_match_object = match_objects[last_match_url]

    # Format the last match name efficiently
    match_name = last_match_url.split('/')[-2].title().replace('Vs', 'vs')
    team_name_map = dict(zip(team_names_ff, team_names_sf))
    for ff_name, sf_name in team_name_map.items():
        match_name = match_name.replace(ff_name, sf_name)

    # Get last match breakdown
    last_match = Match(teams, last_match_object,boosters)
    team_breakdown = last_match.match_points_breakdown

    # Calculate overall points across all matches
    overall_points = {}
    player_overall_points = {}
    for match_url in match_urls:
        match = Match(teams, match_objects[match_url],boosters)
        match_breakdown = match.match_points_breakdown


        for team in match_breakdown.index:
            overall_points.setdefault(team, {"Total Points": 0})
            overall_points[team]["Total Points"] += int(match_breakdown.loc[team, 'Total Points'])

        General_points_list = match.general_player_points_list

        for player in General_points_list.index:
            points = General_points_list.loc[player, "Player Points"]
            if player in player_overall_points:
                player_overall_points[player] += points
            else:
                player_overall_points[player] = points

    # Embed `player_overall_points` inside `overall_points`
    for team, details in overall_points.items():
        gujju_players = teams[team]
        converted_players=convert_types(player_overall_points)
        filtered_players = {player: converted_players[player] for player in gujju_players if player in converted_players}
        details["player_points"] = filtered_players

    json_result = filter_participant_data(team_breakdown, teams)


    orange_cap,purple_cap = '',''
    # orange_cap,purple_cap = op_caps("https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/stats") #ipl-2025-1449924 #Change this later

    return jsonify({
        "last_match": match_name,
        "last_match_points": json_result,
        "overall_points": overall_points,
        "entire_team_details": entire_team_details,
        "orange_cap":orange_cap,
        'purple_cap':purple_cap
    })

def convert_types(obj):
    """ Recursively convert NumPy/Pandas types to Python native types """
    if isinstance(obj, dict):
        return {key: convert_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_types(item) for item in obj]
    elif isinstance(obj, (np.int64, np.float64)):  # Convert NumPy numbers
        return obj.item()
    elif isinstance(obj, pd.DataFrame):  # Convert DataFrame to dict
        return obj.to_dict(orient='records')
    elif isinstance(obj, pd.Series):  # Convert Series to list
        return obj.tolist()
    return obj

def filter_participant_data(df, teams):
    return {
        participant: {
            player: df.loc[participant, player]
            for player in players if player in df.columns
        }
        for participant, players in teams.items() if participant in df.index
    }


# Convert to JSON format

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

if __name__ == '__main__':
    app.run(debug=True)
