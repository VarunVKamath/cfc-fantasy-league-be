from flask import Flask, jsonify
from flask_cors import CORS
import time
import pandas as pd
from Scraping import Series
from Points import Match

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for demonstration purposes

team_names_sf = ["KKR","GT","MI","CSK","RR","RCB","PBKS","DC","SRH","LSG"]
team_names_ff = ["Kolkata Knight Riders", "Gujarat Titans", "Mumbai Indians", "Chennai Super Kings","Rajasthan Royals","Royal Challengers Bengaluru", "Punjab Kings","Delhi Capitals","Sunrisers Hyderabad","Lucknow Super Giants"]

cricbuzz_page_link = "https://www.cricbuzz.com/cricket-series/7607/indian-premier-league-2024/matches"
ipl24_url = "https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/match-schedule-fixtures-and-results"
ipl2024 = Series(ipl24_url, cricbuzz_page_link)
match_objects = ipl2024.match_objects

# teams = {
#     'Participant1': ['K Sharma', 'Kohli', 'Narine', 'V Iyer'],
#     'Participant2': ['Shivam Dube', 'Mahendra Singh Dhoni', 'Sai Kishore', 'Noor Ahmad', 'Sandeep Sharma'],
#     # 'Participant3': ['Rohit Sharma', 'Jadeja', 'Buttler', 'Bumrah'],
#     # 'Participant4': ['David Warner', 'K L Rahul', 'Axar Patel', 'Mitchell Starc'],
#     # 'Participant5': ['Faf du Plessis', 'Shreyas Iyer', 'Mohammed Shami', 'Rashid Khan'],
#     # 'Participant6': ['Glenn Maxwell', 'Sam Curran', 'Hardik Pandya', 'Trent Boult'],
#     # 'Participant7': ['Shubman Gill', 'Jos Buttler', 'Andre Russell', 'Jofra Archer'],
#     # 'Participant8': ['Sanju Samson', 'Yuzvendra Chahal', 'Mark Wood', 'Pat Cummins']
# }
entire_team_details={
    "Gujju Gang (Nisarg)": {
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
    "Hilarious Hooligans (KARAM)": {
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
    "Tormented Titans (Aryan)": {
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
    "La Furia Roja (Abhinav)": {
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
    "Supa Jinx Strikas (Varun)": {
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
    "Raging Raptors (Aditya)": {
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
    "The Traveling Bankers (Aakash)": {
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


teams= {team: details["players"] for team, details in entire_team_details.items()}


@app.route('/generate-points', methods=['GET'])
def generate_points():
    begin = time.time()
    spreadsheet = {'Teams': {}}
    match_urls = list(match_objects.keys())

    for match_number in range(1, 72):
        match_url = match_urls[match_number - 1]
        match_object = match_objects[match_url]
        match_name = match_url.split('/')[-2].title().replace('Vs', 'vs')

        for ipl_team in team_names_ff:
            if ipl_team in match_name:
                match_name = match_name.replace(ipl_team, team_names_sf[team_names_ff.index(ipl_team)])

        match = Match(teams, match_object)
        team_breakdown = match.match_points_breakdown
        General_points_list = match.general_player_points_list

        spreadsheet[(match_name + " Points Breakdown")] = General_points_list
        spreadsheet[(match_name + " CFC Points")] = team_breakdown

        final_points = spreadsheet['Teams']
        for team in list(team_breakdown.index):
            final_points.setdefault(team, {}).setdefault("Total Points", 0)
            final_points[team][match_name] = team_breakdown.loc[team, 'Total Points']
            final_points[team]['Total Points'] += final_points[team][match_name]

    file_path = "CFC_Fantasy_League.xlsx"
    with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
        for sheet_name, data in spreadsheet.items():
            df = pd.DataFrame.from_dict(data, orient='index') if isinstance(data, dict) else pd.DataFrame(data)
            df.to_excel(writer, sheet_name=sheet_name)

    end = time.time()
    total_time_taken = f"{int((end - begin) / 60)}m {round((end - begin) % 60, 3)}s"
    return jsonify({"message": "Excel file saved successfully", "file_path": file_path, "runtime": total_time_taken})

# @app.route('/last-match-and-overall-points', methods=['GET'])
# def last_match_and_overall_points():
#     match_urls = list(match_objects.keys())
#     last_match_url = match_urls[-1]
#     match_object = match_objects[last_match_url]
#     match_name = last_match_url.split('/')[-2].title().replace('Vs', 'vs')

#     for ipl_team in team_names_ff:
#         if ipl_team in match_name:
#             match_name = match_name.replace(ipl_team, team_names_sf[team_names_ff.index(ipl_team)])

#     match = Match(teams, match_object)
#     team_breakdown = match.match_points_breakdown

#     overall_points = {}

#     # Accumulate total points across all matches
#     for match_url in match_urls:
#         match_object = match_objects[match_url]
#         match = Match(teams, match_object)
#         team_breakdown = match.match_points_breakdown

#         for team in list(team_breakdown.index):
#             if team not in overall_points:
#                 overall_points[team] = {"Total Points": 0}
#             overall_points[team]["Total Points"] += int(team_breakdown.loc[team, 'Total Points'])


#     tb = pd.DataFrame(team_breakdown)
#     json_result = filter_participant_data(tb, teams)

    
#     # json_result_new = tb.T.to_dict()
            

#     return jsonify({
#         "last_match": match_name,
#         "last_match_points":json_result,
#         "overall_points": overall_points,
#         "entire_team_details":entire_team_details
#     })

# def filter_participant_data(df, teams):
#     filtered_data = {}

#     for participant, players in teams.items():
#         if participant in df.index:
#             filtered_data[participant] = {
#                 player: df.loc[participant, player] for player in players if player in df.columns
#             }

#     return filtered_data


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
    last_match = Match(teams, last_match_object)
    team_breakdown = last_match.match_points_breakdown

    # Calculate overall points across all matches
    overall_points = {}
    for match_url in match_urls:
        match = Match(teams, match_objects[match_url])
        match_breakdown = match.match_points_breakdown

        for team in match_breakdown.index:
            overall_points.setdefault(team, {"Total Points": 0})
            overall_points[team]["Total Points"] += int(match_breakdown.loc[team, 'Total Points'])

    # Convert DataFrame to JSON
    json_result = filter_participant_data(team_breakdown, teams)

    return jsonify({
        "last_match": match_name,
        "last_match_points": json_result,
        "overall_points": overall_points,
        "entire_team_details": entire_team_details
    })


def filter_participant_data(df, teams):
    return {
        participant: {
            player: df.loc[participant, player]
            for player in players if player in df.columns
        }
        for participant, players in teams.items() if participant in df.index
    }


# Convert to JSON format

if __name__ == '__main__':
    app.run(debug=True)
