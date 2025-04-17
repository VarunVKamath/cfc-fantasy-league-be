from flask import Flask, jsonify
import json
from flask_cors import CORS
import os
import re

app = Flask(__name__)
CORS(app)

# Set your JSON file path here
JSON_FILE_PATH = "CFC Fantasy League 2025.json"

# List of team names
entire_team_details = {
    "Gujju Gang": {
        "players":  ['Varun Chakaravarthy','Travis Head','Harshit Rana','Rahul Chahar','Mukesh Choudhary','Ishant Sharma','Jaydev Unadkat','Mukesh Kumar','Abdul Samad','Riyan Parag','Khaleel Ahmed','Avesh Khan','Faf du Plessis','Arjun Tendulkar','Mohammed Shami','Shivam Dube','Lockie Ferguson','Josh Hazlewood','Prabhsimran Singh','Rishabh Pant','Corbin Bosch','Mohammed Siraj','Prasidh Krishna','Marcus Stoinis','Harpreet Brar','Rahmanullah Gurbaz','Rashid Khan','Washington Sundar'],

        "captain": "Varun Chakaravarthy",
        "vice_captain": "Travis Head",
        "team_color": "#995C00",
        "team_owner": "Nisarg",
        "injured": ['Lockie Ferguson']
    },
    "Hilarious Hooligans": {
        "players":              ['Yashasvi Jaiswal','Axar Patel','Hardik Pandya','Heinrich Klaasen','Rinku Singh','Nehal Wadhera','Romario Shepherd','Manav Suthar','Vijaykumar Vyshak','Himmat Singh','Ayush Badoni','Liam Livingstone','Nathan Ellis','Moeen Ali','Karn Sharma','Shimron Hetmyer','Mayank Yadav','Abhinav Manohar','Ashutosh Sharma','Rachin Ravindra','Shahrukh Khan','Anrich Nortje','Mayank Markande','Yuzvendra Chahal','Tushar Deshpande','Noor Ahmad','Kagiso Rabada','Marco Jansen'],

        "captain": "Yashasvi Jaiswal",
        "vice_captain": "Axar Patel",
        "team_color": "#FFFF00",
        "team_owner": "Karam"
    },
    "Tormented Titans": {
        "players":              ['Virat Kohli','Suryakumar Yadav','Abhishek Sharma','Jitesh Sharma','Harnoor Singh','Bhuvneshwar Kumar','Abishek Porel','Angkrish Raghuvanshi','Kuldeep Yadav','Dhruv Jurel','David Miller','Anuj Rawat','Josh Inglis','Kumar Kartikeya','Akash Deep','Rahul Tewatia','Ramandeep Singh','Sherfane Rutherford','Glenn Maxwell','Sandeep Sharma','Shamar Joseph','Pat Cummins','Quinton de Kock','Ravichandran Ashwin'],

        "captain": "Virat Kohli",
        "vice_captain": "Suryakumar Yadav",
        "team_color": "#FFA500",
        "team_owner": "Aryan"
    },
    "La Furia Roja": {
        "players":    
            ['Shreyas Iyer','Sai Sudharsan','Jasprit Bumrah','Swastik Chikara','Rajvardhan Hangargekar','Manoj Bhandage','Nitish Rana','Rasikh Salam Dar','Deepak Chahar','MS Dhoni','Aaron Hardie','Priyansh Arya','Phil Salt','Sameer Rizvi','Mitchell Santner','Manish Pandey','Suyash Sharma','Kamlesh Nagarkoti','Will Jacks','Azmatullah Omarzai','Adam Zampa','Spencer Johnson','Jamie Overton','Shashank Singh','Rovman Powell','Suryansh Shedge','Maheesh Theekshana','Smaran Ravichandran'],
          
        "captain": "Shreyas Iyer",
        "vice_captain": "Sai Sudharsan",
        "team_color": "#FF0000",
        "team_owner": "Abhinav",
        "injured": ['Adam Zampa']

    },
    "Supa Jinx Strikas": {
        "players": 
             ['Shubman Gill','Ruturaj Gaikwad','Nitish Reddy','Mohit Sharma','Sai Kishore','Raj Bawa','Ishan Kishan','Mitchell Marsh','Karim Janat','Yash Dayal','Bevon Jacobs','Ryan Rickelton','Rajat Patidar','Tristan Stubbs','Gerald Coetzee','Glenn Phillips','Tim David','Ravi Bishnoi','Donovan Ferreira','Jayant Yadav','Trent Boult','Jofra Archer','Akash Madhwal','Darshan Nalkande','Kwena Maphaka','Ayush Mhatre'],
         
        "captain": "Shubman Gill",
        # "vice_captain": "Ruturaj Gaikwad",
        "vice_captain": "Ayush Mhatre",
        "team_color": "#0000FF",
        "team_owner": "Varun",
        "injured": ["Ruturaj Gaikwad",'Glenn Phillips']

    },
    "Raging Raptors": {
        "players":              ['KL Rahul','Venkatesh Iyer','Arshdeep Singh','Ravindra Jadeja','Aiden Markram','Sachin Baby','Dushmantha Chameera','Naman Dhir','Karun Nair','Wanindu Hasaranga','Arshad Khan','Devdutt Padikkal','Robin Minz','Shahbaz Ahmed','Mohsin Khan','Krunal Pandya','Mitchell Starc','Sanju Samson','Jos Buttler','Atharva Taide','Musheer Khan','Devon Conway','Shardul Thakur'],

        "captain": "KL Rahul",
        "vice_captain": "Venkatesh Iyer",
        "team_color": "#008000",
        "team_owner": "Aditya",
        "injured": ["Mohsin Khan"],
        # "replacements": ['Shardul Thakur'],
    },
    "The Travelling Bankers": {
        "players": ['Sunil Narine','Andre Russell','Harshal Patel','Umran Malik','Chetan Sakariya','T Natarajan','Ajinkya Rahane','Shreyas Gopal','Tilak Varma','Vijay Shankar','Shubham Dubey','Anukul Roy','Deepak Hooda','Rahul Tripathi','Lungi Ngidi','Matheesha Pathirana','Vaibhav Arora','Nicholas Pooran','Jake Fraser-McGurk','Sam Curran','Rohit Sharma','Mujeeb Ur Rahman','Anshul Kamboj','Mahipal Lomror'],
        "captain": "Sunil Narine",
        "vice_captain": "Andre Russell",
        "injured": ["Umran Malik"],
        # "replacements": ["Chetan Sakariya"],
        "team_color": "#800080",
        "team_owner": "Aakash"
    }
}

boosters = {'Gujju Gang':{},
             'Hilarious Hooligans':{},
             'Tormented Titans':{},
             'La Furia Roja':{},
             'Supa Jinx Strikas':{
                 'https://www.espncricinfo.com/series/ipl-2025-1449924/mumbai-indians-vs-sunrisers-hyderabad-33rd-match-1473470/full-scorecard':"Batting Powerplay"
             },
             'Raging Raptors':{
                 'https://www.espncricinfo.com/series/ipl-2025-1449924/delhi-capitals-vs-rajasthan-royals-32nd-match-1473469/full-scorecard':"Batting Powerplay"

             },
             'The Travelling Bankers':{
                 "https://www.espncricinfo.com/series/ipl-2025-1449924/kolkata-knight-riders-vs-lucknow-super-giants-21st-match-1473456/full-scorecard":"Batting Powerplay"
             }
             }


booster_types = ["Triple Power", "Double Power", "Batting Powerplay", "Bowling Powerplay", "Triple Captain"]

# Team short forms (for abbreviation)
team_aliases = {
    'royal challengers bengaluru': 'RCB',
    'kolkata knight riders': 'KKR',
    'sunrisers hyderabad': 'SRH',
    'mumbai indians': 'MI',
    'chennai super kings': 'CSK',
    'delhi capitals': 'DC',
    'punjab kings': 'PBKS',
    'lucknow super giants': 'LSG',
    'rajasthan royals': 'RR',
    'gujarat titans': 'GT'
}

def extract_match_name(url):
    match = re.search(r'/([^/]+)/full-scorecard', url)
    if match:
        slug = match.group(1)
        slug = re.sub(r'-\d+(st|nd|rd|th)-match.*', '', slug)
        teams = slug.split('-vs-')
        if len(teams) == 2:
            team1_raw = teams[0].replace('-', ' ')
            team2_raw = teams[1].replace('-', ' ')
            team1 = team_aliases.get(team1_raw.lower(), team1_raw.upper())
            team2 = team_aliases.get(team2_raw.lower(), team2_raw.upper())
            return f"{team1} Vs {team2}"
    return "Unknown Match"


@app.route('/last-match-and-overall-points', methods=['GET'])
def get_all_points():
    if not os.path.exists(JSON_FILE_PATH):
        return jsonify({"error": "File not found"}), 404

    try:
        with open(JSON_FILE_PATH, 'r') as file:
            data = json.load(file)
        
        team_final_points = data.get("Team Final Points", {})
        
        # Extract total points for all teams
        results = {}
        for team in entire_team_details.keys():
            results[team] = team_final_points.get(team, {}).get("Total Points", "Not found")

        last_match_key=find_key_with_points_breakdown(data)

        last_match= list(last_match_key.keys())[0].replace(" - Points Breakdown", "")

        
        # Extract total points for all teams
        team_last_match_points = {}
        for team in entire_team_details.keys():
            team_last_match_points[team] = team_final_points.get(team, {}).get(last_match, "Not found")


# Create final team points structure
        team_points = {"player_final_points": {}}

        for team, details in entire_team_details.items():
            team_points["player_final_points"][team] = {}

            for player in details["players"]:
                if player in data["Player Final Points"]:
                    team_points["player_final_points"][team][player] = data["Player Final Points"][player]["Total Points"]



        last_match_points = {"player_final_points": {}}

        for team, details in entire_team_details.items():
            last_match_points["player_final_points"][team] = {}

            for player in details["players"]:
                if player in data["Player Final Points"]:
                    last_match_points["player_final_points"][team][player] = data["Player Final Points"][player][last_match]
        
        purple_team_name = None
        for team, details in data["Team Final Points"].items():
            if details.get("Purple Cap") == 500:
                purple_team_name = team

        purple_player_name = None
        for player, details in data["Player Final Points"].items():
            if details.get("Purple Cap") == 500:
                purple_player_name = player

        orange_player_name = None
        for player, details in data["Player Final Points"].items():
            if details.get("Orange Cap") == 500:
                orange_player_name = player

        orange_team_name = None
        for team, details in data["Team Final Points"].items():
            if details.get("Orange Cap") == 500:
                orange_team_name = team

        team_booster_summary = {}

        for team, matches in boosters.items():
            used = {booster: "NA" for booster in booster_types}
            for match_url, booster in matches.items():
                match_name = extract_match_name(match_url)
                used[booster] = match_name
            team_booster_summary[team] = used
        return jsonify(
            {
                "total_points_per_team": results,
                "team_last_match_points":team_last_match_points,
                'last_match':last_match,
                'total_points_per_player':team_points["player_final_points"],
                'last_match_points_per_player':last_match_points["player_final_points"],
                'entire_team_details': entire_team_details,
                'purple_cap':{
                    'team':purple_team_name,
                    'player':purple_player_name
                },
                'orange_cap':{
                    'team':orange_team_name,
                    'player':orange_player_name
                },

                'team_booster_summary':team_booster_summary
                
                }
        )
    
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    


def find_key_with_points_breakdown(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if "Points Breakdown" in key:  # Updated to check if key contains the phrase
                return {key: value}
            result = find_key_with_points_breakdown(value)
            if result:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = find_key_with_points_breakdown(item)
            if result:
                return result
    return None
    
if __name__ == '__main__':
    app.run(debug=True)
