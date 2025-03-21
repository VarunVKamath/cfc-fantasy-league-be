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


if __name__ == '__main__':
    begin = time.time()
    team_names_sf = ["KKR","GT","MI","CSK","RR","RCB","PBKS","DC","SRH","LSG"]
    team_names_ff = ["Kolkata Knight Riders", "Gujarat Titans", "Mumbai Indians", "Chennai Super Kings","Rajasthan Royals","Royal Challengers Bengaluru", "Punjab Kings","Delhi Capitals","Sunrisers Hyderabad","Lucknow Super Giants"]
    cricbuzz_page_link = "https://www.cricbuzz.com/cricket-series/7607/indian-premier-league-2024/matches" #Change this later
    ipl24_url = "https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/match-schedule-fixtures-and-results" #Change this later
    #cricbuzz_page_link = "https://www.cricbuzz.com/cricket-series/9237/indian-premier-league-2025/matches"
    #ipl24_url = "https://www.espncricinfo.com/series/ipl-2025-1449924/match-schedule-fixtures-and-results"
    database = "ipl2024matches.pkl" #Change this later
    ipl2024 = Series(ipl24_url,cricbuzz_page_link,database) #Change this later
    file_path = "CFC Fantasy League.xlsx"
    try:
        spreadsheet = excel_to_dict(file_path)
    except:
        spreadsheet = {}
        spreadsheet['Team Final Points'] = {}
        spreadsheet['Player Final Points'] = {}

    match_objects = ipl2024.match_objects

    teams = {'Gujju Gang':['Varun Chakaravarthy','Travis Head','Rahul Chahar','Mukesh Choudhary','Harshit Rana','Ishant Sharma','Jaydev Unadkat','Mukesh Kumar','Abdul Samad','Riyan Parag','Khaleel Ahmed','Avesh Khan','Faf du Plessis','Arjun Tendulkar','Mohammed Shami','Shivam Dube','Lockie Ferguson','Josh Hazlewood','Prabhsimran Singh','Rishabh Pant','Corbin Bosch','Mohammed Siraj','Prasidh Krishna','Marcus Stoinis','Harpreet Brar','Rahmanullah Gurbaz','Rashid Khan','Washington Sundar'],
             'Hilarious Hooligans':['Yashasvi Jaiswal','Axar Patel','Hardik Pandya','Heinrich Klaasen','Rinku Singh','Nehal Wadhera','Romario Shepherd','Manav Suthar','Vijaykumar Vyshak','Himmat Singh','Ayush Badoni','Liam Livingstone','Nathan Ellis','Moeen Ali','Karn Sharma','Shimron Hetmyer','Mayank Yadav','Abhinav Manohar','Ashutosh Sharma','Rachin Ravindra','Shahrukh Khan','Anrich Nortje','Mayank Markande','Yuzvendra Chahal','Tushar Deshpande','Noor Ahmad','Kagiso Rabada','Marco Jansen'],
             'Tormented Titans':['Virat Kohli','Suryakumar Yadav','Abhishek Sharma','Jitesh Sharma','Harnoor Singh','Bhuvneshwar Kumar','Abishek Porel','Angkrish Raghuvanshi','Kuldeep Yadav','David Miller','Anuj Rawat','Josh Inglis','Kumar Kartikeya','Akash Deep','Rahul Tewatia','Ramandeep Singh','Sherfane Rutherford','Glenn Maxwell','Sandeep Sharma','Shamar Joseph','Pat Cummins','Quinton de Kock','Ravichandran Ashwin'],
             'La Furia Roja':['Shreyas Iyer','Sai Sudharsan','Jasprit Bumrah','Swastik Chikara','Rajvardhan Hangargekar','Manoj Bhandage','Nitish Rana','Rasikh Dar Salam','Deepak Chahar','MS Dhoni','Aaron Hardie','Priyansh Arya','Phil Salt','Sameer Rizvi','Mitchell Santner','Manish Pandey','Suyash Sharma','Kamlesh Nagarkoti','Will Jacks','Azmatullah Omarzai','Adam Zampa','Spencer Johnson','Jamie Overton','Shashank Singh','Rovman Powell','Suryansh Shedge','Maheesh Theekshana'],
             'Supa Jinx Strikas':['Shubman Gill','Ruturaj Gaikwad','Mohit Sharma','Sai Kishore','Raj Bawa','Ishan Kishan','Mitchell Marsh','Nitish Kumar Reddy','Karim Janat','Yash Dayal','Bevon Jacobs','Ryan Rickelton','Rajat Patidar','Tristan Stubbs','Gerald Coetzee','Glenn Phillips','Tim David','Ravi Bishnoi','Donovan Ferreira','Jayant Yadav','Trent Boult','Jofra Archer','Akash Madhwal','Darshan Nalkande','Kwena Maphaka'],
             'Raging Raptors':['KL Rahul','Venkatesh Iyer','Arshdeep Singh','Aiden Markram','Sachin Baby','Dushmantha Chameera','Naman Dhir','Karun Nair','Wanindu Hasaranga','Arshad Khan','Devdutt Padikkal','Robin Minz','Shahbaz Ahmed','Mohsin Khan','Krunal Pandya','Ravindra Jadeja','Mitchell Starc','Sanju Samson','Jos Buttler','Atharva Taide','Musheer Khan','Devon Conway'],
             'The Travelling Bankers':['Sunil Narine','Andre Russell','Chetan Sakariya','T Natarajan','Ajinkya Rahane','Shreyas Gopal','Tilak Varma','Vijay Shankar','Shubham Dubey','Anukul Roy','Deepak Hooda','Harshal Patel','Rahul Tripathi','Lungi Ngidi','Matheesha Pathirana','Vaibhav Arora','Nicholas Pooran','Jake Fraser-McGurk','Sam Curran','Rohit Sharma','Mujeeb Ur Rahman','Anshul Kamboj','Mahipal Lomror']
             }
    boosters = {'Gujju Gang':{"https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/royal-challengers-bengaluru-vs-kolkata-knight-riders-10th-match-1422128/full-scorecard":"Triple Power"},
             'Hilarious Hooligans':{"https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/royal-challengers-bengaluru-vs-kolkata-knight-riders-10th-match-1422128/full-scorecard":"Double Power"},
             'Tormented Titans':{"https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/royal-challengers-bengaluru-vs-kolkata-knight-riders-10th-match-1422128/full-scorecard":"Batting Powerplay"},
             'La Furia Roja':{"https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/royal-challengers-bengaluru-vs-kolkata-knight-riders-10th-match-1422128/full-scorecard":"Bowling Powerplay"},
             'Supa Jinx Strikas':{"https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/royal-challengers-bengaluru-vs-kolkata-knight-riders-10th-match-1422128/full-scorecard":"Double Power","https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/kolkata-knight-riders-vs-sunrisers-hyderabad-3rd-match-1422121/full-scorecard":"Triple Captain"},
             'Raging Raptors':{},
             'The Travelling Bankers':{}
             } #for example Change this later
    
    orange_cap,purple_cap = op_caps("https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/stats") #ipl-2025-1449924 #Change this later
    
    # Reset all team total points before processing matches
    if 'Team Final Points' in spreadsheet:
        for team in teams:
            if team in spreadsheet['Team Final Points']:
                spreadsheet['Team Final Points'][team]['Total Points'] = 0
                spreadsheet['Team Final Points'][team]['Orange Cap'] = 0
                spreadsheet['Team Final Points'][team]['Purple Cap'] = 0
    
    # Reset all player total points before processing matches
    if 'Player Final Points' in spreadsheet:
        for player in list(spreadsheet['Player Final Points'].keys()):
            spreadsheet['Player Final Points'][player]['Total Points'] = 0
            spreadsheet['Player Final Points'][player]['Orange Cap'] = 0
            spreadsheet['Player Final Points'][player]['Purple Cap'] = 0

    #url = "https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/kolkata-knight-riders-vs-sunrisers-hyderabad-3rd-match-1422121/full-scorecard"             
    cricbuzz_page_link = "https://www.cricbuzz.com/cricket-series/7607/indian-premier-league-2024/matches"   
    match_urls = list(match_objects.keys())
    number_of_matches = len(match_objects)
    for match_number in range(number_of_matches,0,-1):
        
        match_url = match_urls[match_number-1]
        # if match_url in
        match_object = match_objects[match_url]
        #match_object.printing_scorecard()
        match_name = match_name_generator(match_url)
        match = Match(teams,match_object,boosters)
        team_breakdown = match.match_points_breakdown
        # if "KKR vs RCB" in match_name:
        #     print(team_breakdown)
        General_points_list = match.general_player_points_list
        points_key = match_name+" - Points Breakdown"
        # To safely check if data has changed:
        if points_key in spreadsheet.keys():
            existing_data = spreadsheet[points_key]
            #print(existing_data)
            # Check if key columns are the same length
            if len(list(existing_data.keys())) == len(list(General_points_list.index)):
                
                # Check if the sum of player points is the same
                if sum([existing_data[player]['Player Points'] for player in existing_data.keys()]) == sum([General_points_list['Player Points'][player] for player in General_points_list.index]):
                    print(f"Match {match_name} already processed and unchanged, skipping...")
                    break

        spreadsheet[(match_name+" - Points Breakdown")] = General_points_list
        spreadsheet[(match_name+" - CFC Points")] = team_breakdown
        final_points = spreadsheet['Team Final Points']

        for team in list(team_breakdown.index):
            final_points.setdefault(team, {}).setdefault("Total Points", 0)
            final_points.setdefault(team, {}).setdefault("Orange Cap", 0)
            final_points.setdefault(team, {}).setdefault("Purple Cap", 0)
            final_points[team][match_name] = team_breakdown.loc[team,'Total Points']
            final_points[team]['Total Points'] += final_points[team][match_name]
        print(match_name,"added")
    try:
        for team in list(final_points.keys()):
            orange_cap_points = 0
            purple_cap_points = 0
            if orange_cap in teams[team]:
                orange_cap_points = 500
            if purple_cap in teams[team]:
                purple_cap_points = 500
            final_points[team]['Total Points'] += orange_cap_points + purple_cap_points
            final_points[team]['Orange Cap'] = orange_cap_points
            final_points[team]['Purple Cap'] = purple_cap_points
        print("Purple Cap, Orange Cap, Total Points added")
        spreadsheet['Team Final Points'] = dict(sorted(final_points.items(), key=lambda x: x[1]['Total Points'], reverse=True))

        player_list_points = []
        match_list_points = []
        for key in spreadsheet.keys():
            if " - Points Breakdown" in key:
                match_breakdown = spreadsheet[key]
                match_name = key.split(' - Points Breakdown')[0]
                for player in list(match_breakdown.index):
                    spreadsheet['Player Final Points'].setdefault(player,{}).setdefault("Total Points",0)
                    spreadsheet['Player Final Points'].setdefault(player,{}).setdefault("Orange Cap",0)
                    spreadsheet['Player Final Points'].setdefault(player,{}).setdefault("Purple Cap",0)
                    spreadsheet['Player Final Points'].setdefault(player,{}).setdefault(match_name,0)
                    spreadsheet['Player Final Points'][player]['Total Points'] += match_breakdown['Player Points'][player]
                    spreadsheet['Player Final Points'][player][match_name] = match_breakdown['Player Points'][player]
                for player in list(spreadsheet['Player Final Points'].keys()):
                    if player not in player_list_points:
                        player_list_points.append(player)
                    if match_name not in match_list_points:
                        match_list_points.append(match_name)
                    try:
                        hululu = spreadsheet['Player Final Points'][player][match_name]
                    except:
                        spreadsheet['Player Final Points'][player][match_name] = 0
        for player in spreadsheet['Player Final Points'].keys():  
            if player not in player_list_points:
                player_list_points.append(player)      
            if player == orange_cap:
                spreadsheet['Player Final Points'][player]['Orange Cap'] += 500
                spreadsheet['Player Final Points'][player]['Total Points'] += 500
            if player == purple_cap:
                spreadsheet['Player Final Points'][player]['Purple Cap'] += 500
                spreadsheet['Player Final Points'][player]['Total Points'] += 500
        for player in player_list_points:
            for match in match_list_points:
                try:
                    hululu2 = spreadsheet['Player Final Points'][player][match]
                except:
                    spreadsheet['Player Final Points'][player][match] = 0

        # Extract the first player's column order before sorting
        first_player = next(iter(spreadsheet['Player Final Points'].values()))  # Get the first player's stats
        column_order = list(first_player.keys())  # Maintain the original column order

        # Sort players by 'Total Points'
        sorted_players = OrderedDict(
            sorted(spreadsheet['Player Final Points'].items(), key=lambda x: x[1]['Total Points'], reverse=True)
        )

        # Reorder each player's stats to match the original column order
        for player in sorted_players:
            sorted_players[player] = OrderedDict((key, sorted_players[player][key]) for key in column_order)

        # Assign back to the spreadsheet
        spreadsheet['Player Final Points'] = sorted_players

                    
        print("Player Points Added")

        with open("CFC Fantasy League.json", "w") as json_file:
            json.dump(spreadsheet, json_file, indent=4)
        print("JSON file created successfully!")

        # Write to Excel
        with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
            for sheet_name, data in spreadsheet.items():
                if isinstance(data, dict):  # If it's a dictionary, convert it to a DataFrame
                    df = pd.DataFrame.from_dict(data, orient='index')
                elif isinstance(data, list):  # If it's a list, convert to DataFrame
                    df = pd.DataFrame(data)
                else:
                    df = data  # If it's already a DataFrame

                df.to_excel(writer, sheet_name=sheet_name)  # Keep index for readability

            print(f"Excel file saved successfully as {file_path} in the current folder.")
    except:
        print("No New Data was Added")
        with open("CFC Fantasy League.json", "w") as json_file:
            json.dump(spreadsheet, json_file, indent=4)
        print("JSON file created successfully!")
        
    

    end = time.time()
    total_time_taken = end-begin
    minutes = str(int(total_time_taken/60))
    seconds = str(round(total_time_taken % 60,3))
    total_time_taken = minutes+"m "+seconds+"s"
    print(f"Time taken to process data: {total_time_taken}")        





        

