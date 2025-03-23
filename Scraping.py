import requests
from bs4 import BeautifulSoup
import pandas as pd
from IPython.display import display
import dill
from rapidfuzz import process
import re


def match_number_generator(match_link):
    parts = (match_link.split('/')[-2].split('-')[-3:-1])
    if parts[1] == 'match':
        match_number = parts[0][:-2]
    elif parts[0] == 'qualifier':
        if parts[1] == '1':
            match_number = 71
        elif parts[1] == '2':
            match_number = 73
    elif parts[1] == 'eliminator':
        match_number = 72
    elif parts[1] == 'final':
        match_number = 74
    return int(match_number)

def extract_team_players(players_list, impact_sub_class):
    team = []
    try:
        for i in range(16):
            if i > 10:
                impact_sub = players_list[i].find('span', class_= impact_sub_class)
                if impact_sub is None:
                    continue
                else:
                    player = clean_player_name(players_list[i].text)
                    team.append(player)
                    break
            player = clean_player_name(players_list[i].text)
            team.append(player)
        return team
    except:
        pass

def clean_player_name(text):
    return text.strip().split('  ')[0].split('(C & WK)')[0].split(' (C)')[0].split(' (WK)')[0].strip()

def match_squads_generator(ipl_url, match_number):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(ipl_url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        matches = soup.find_all('div', class_='cb-col-75 cb-col')
        match = matches[int(match_number) - 1]
        match_link = "https://www.cricbuzz.com" + match.find('a')['href']
        
        if 'live-cricket-scores' in match_link:
            match_link = match_link.replace('live-cricket-scores', 'cricket-match-squads')
        elif 'cricket-scores' in match_link:
            match_link = match_link.replace('cricket-scores', 'cricket-match-squads')

        response_squads = requests.get(match_link, headers=headers)
        soup_squads = BeautifulSoup(response_squads.content, "html.parser")
        team_matchup = soup_squads.find('h1',class_='cb-nav-hdr cb-font-18 line-ht24').text.strip()
        team1_name = team_matchup.split(' vs ')[0]
        team2_name = team_matchup.split(' vs ')[1].split(',')[0].strip()

        required_classes_team1 = {'cb-col', 'cb-col-100', 'pad10', 'cb-player-card-left'}

        players_team1 = [
        a for a in soup_squads.find_all('a', class_=True) 
        if required_classes_team1.issubset(set(a['class']))
    ]
        required_classes_team2 = {'cb-col', 'cb-col-100', 'pad10', 'cb-player-card-right'}

        players_team2 = [
        a for a in soup_squads.find_all('a', class_=True) 
        if required_classes_team2.issubset(set(a['class']))
    ]
        #players_team2 = soup_squads.find_all('a', class_='cb-col cb-col-100 pad10 cb-player-card-right')

        team1 = extract_team_players(players_team1, "cb-plus-match-change-icon cb-bg-min cb-match-change-left")
        team2 = extract_team_players(players_team2, "cb-plus-match-change-icon cb-bg-min cb-match-change-right")
        teams = {team1_name:team1,team2_name:team2}

        return teams
    except:
        return {}

def dismissals_scraper(soup,innings_id):
    innings = soup.find('div',id=innings_id)
    innings_name = innings.find('span').text.split(' Innings')[0]
    #print(innings_name)
    player_batting = innings.find_all('div',class_="cb-col cb-col-100 cb-scrd-itms")
    dismissals = []
    for player in player_batting:
        dismissal = player.find('span',class_='text-gray')
        if dismissal:
            dismissal = dismissal.text
            dismissals.append(dismissal)
    return innings_name,dismissals

def match_dismissals_output(ipl_url, match_number):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(ipl_url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        matches = soup.find_all('div', class_='cb-col-75 cb-col')
        match = matches[int(match_number) - 1]
        match_link = "https://www.cricbuzz.com" + match.find('a')['href']
        
        if 'live-cricket-scores' in match_link:
            match_link = match_link.replace('live-cricket-scores', 'live-cricket-scorecard')
        elif 'cricket-scores' in match_link:
            match_link = match_link.replace('cricket-scores', 'live-cricket-scorecard')

        response_score = requests.get(match_link, headers=headers)
        soup_score = BeautifulSoup(response_score.content, "html.parser")
        innings1,dismissals1 = dismissals_scraper(soup_score,"innings_1")
        innings2,dismissals2 = dismissals_scraper(soup_score,"innings_2")   
        dismissals = {innings2:dismissals1,innings1:dismissals2}
        return dismissals
    except:
        print("Error",match_number,"not scraping properly")

def find_full_name(team,short_name):
    try:
        if "Varun Chak" in short_name:
            return "Varun Chakaravarthy"
        if "Reddy" in short_name and "Nitish" in short_name:
            return "Nitish Reddy"
        player = ""
        for player in team:
            if len(player)>len(short_name):
                count = 0
                parts = short_name.split(' ')
                parts_dup = []
                for part in parts:
                    word = ""
                    for letter_number in range(len(part)):
                        char = part[letter_number]
                        word += char
                        if letter_number == len(part)-1:
                            parts_dup.append(word)
                            break
                        if part[letter_number+1].isupper():
                            parts_dup.append(word)
                            word = ""
                parts = parts_dup
                for part in parts:
                    if part not in player:
                        count += 1
                if count == 0:
                    #team_copy.append(player)
                    return player
            else:
                count = 0
                parts = player.split(' ')
                parts_dup = []
                for part in parts:
                    word = ""
                    for letter_number in range(len(part)):
                        char = part[letter_number]
                        word += char
                        if letter_number == len(part)-1:
                            parts_dup.append(word)
                            break
                        if part[letter_number+1].isupper():
                            parts_dup.append(word)
                            word = ""
                parts = parts_dup
                for part in parts:
                    if part not in short_name:
                        count += 1
                if count == 0:
                    return player
                
        if player == "":
            try:
                best_match, score, _ = process.extractOne(short_name, team)
                if score > 70:
                    return best_match
                else:
                    print(short_name,"not found")
            except:
                print(short_name,"not found")
                pass
    except:
        return None

def dismissals_final_generator(ipl_url,game_number):
    players = match_squads_generator(ipl_url,game_number)
    #print("Players:",players)
    dismissals = match_dismissals_output(ipl_url,game_number)
    #print("Dismissals:",dismissals)
    # Step 2: Extract players involved in dismissals
    catchers = {}
    stumpers = {}
    runouters_main = {}
    runouters_secondary = {}
    lbw = {}
    bowled = {}
    try:
        for key in dismissals.keys():
            for dismissal in dismissals[key]:
                if dismissal.startswith("c and b "):  # Catchers
                    catcher_name = dismissal.split("c and b ")[1]
                    catchers.setdefault(key, []).append(catcher_name)
                elif dismissal.startswith("c "):  # Catchers
                    catcher_name = dismissal.split("c ",1)[1].split(' b ')[0]
                    catchers.setdefault(key, []).append(catcher_name)
                elif dismissal.startswith("st "):  # Stumpers
                    stumper_name = dismissal.split("st ",1)[1].split(' b ')[0]
                    stumpers.setdefault(key, []).append(stumper_name)
                elif dismissal.startswith("run out ("):  # Stumpers
                    runouter_name = dismissal.split("run out (",1)[1].split(')')
                    #print(runouter_name)
                    runouters = runouter_name[-2].split('/')
                    if len(runouters) == 2:
                        runouter_second_name = runouters[1]
                        runouters_secondary.setdefault(key, []).append(runouter_second_name)
                    runouter_main_name = runouters[0]
                    runouters_main.setdefault(key, []).append(runouter_main_name)
                elif dismissal.startswith("b "):  # Stumpers
                    bowled_name = dismissal.split("b ",1)[1]
                    bowled.setdefault(key, []).append(bowled_name)
                elif dismissal.startswith("lbw b "):  # Stumpers
                    bowled_name = dismissal.split("lbw b ",1)[1]
                    lbw.setdefault(key, []).append(bowled_name)    
    except:
        pass

    mapped_catchers = mapped_stumpers = mapped_main_runouters = mapped_secondary_runouters = mapped_bowled = mapped_lbw = {}

    mapped_catchers = [full_name for team, names in catchers.items() 
    for name in names 
    if (full_name := find_full_name(players[team], name)) is not None]

    mapped_stumpers = [full_name for team, names in stumpers.items() 
    for name in names 
    if (full_name := find_full_name(players[team], name)) is not None]

    mapped_main_runouters = [full_name for team, names in runouters_main.items() 
    for name in names 
    if (full_name := find_full_name(players[team], name)) is not None]

    mapped_secondary_runouters = [full_name for team, names in runouters_secondary.items() 
    for name in names 
    if (full_name := find_full_name(players[team], name)) is not None]

    mapped_bowled = [full_name for team, names in bowled.items() 
    for name in names 
    if (full_name := find_full_name(players[team], name)) is not None]


    mapped_lbw = [   full_name for team, names in lbw.items() 
    for name in names 
    if (full_name := find_full_name(players[team], name)) is not None]

    return players,mapped_catchers,mapped_stumpers,mapped_main_runouters, mapped_secondary_runouters, mapped_bowled, mapped_lbw

class Score:
    team_names_sf = ["KKR","GT","MI","CSK","RR","RCB","PBKS","DC","SRH","LSG"]
    team_names_ff = ["Kolkata Knight Riders", "Gujarat Titans", "Mumbai Indians", "Chennai Super Kings","Rajasthan Royals","Royal Challengers Bengaluru", "Punjab Kings","Delhi Capitals","Sunrisers Hyderabad","Lucknow Super Giants"]

    def __init__(self,url,cricbuzz_page_link):
        self.cricbuzz_page_link = cricbuzz_page_link
        self.url = url
        self.full_player_list,self.player_list,self.winner,self.man_of_the_match,self.catchers,self.stumpers,self.main_runouters,self.secondary_runouters,self.bowled,self.lbw,self.innings_list,self.batsmen_list,self.bowlers_info = self.scorecard()

    def find_team(self,text):
        def check_list(team_list):
            matches = [word for word in team_list if word in text]
            if len(matches) > 1:
                raise ValueError(f"Error: More than one match found: {matches}")
            elif len(matches) == 1:
                return matches[0]
            return None

        match = check_list(self.team_names_sf)
        if match:
            return self.team_names_ff[self.team_names_sf.index(match)]
        match = check_list(self.team_names_ff)
        if match:
            return match
        raise ValueError("Error: No match found in either list")

    def scorecard(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }
        #catches, stumpings, runouts = 0,0,0
        response = requests.get(self.url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        
        innings_list = []
        batsmen_list = pd.DataFrame()
        bowlers_info = pd.DataFrame()
        #player_list = [[],[]]

        match_number = match_number_generator(self.url)
        player_list,catchers,stumpers,main_runouters,secondary_runouters,bowled,lbw = dismissals_final_generator(self.cricbuzz_page_link,match_number)
        team_names = list(player_list.keys())
        full_player_list = [player for team in team_names for player in player_list[team]]
        try:
            winner = soup.find('p',class_="ds-text-tight-s ds-font-medium ds-truncate ds-text-typo").text.strip()
            winner = self.find_team(winner)
        except:
            winner = ""

        match_details_table = soup.find('table',class_= "ds-w-full ds-table ds-table-sm ds-table-auto") 
        table_rows = match_details_table.find_all('tr')
        c1 = 0
        for row in table_rows:
            if "Player Of The Match" in row.text:
                man_of_the_match = row.find('td',class_="ds-text-typo").text.strip()
                man_of_the_match = find_full_name(full_player_list,man_of_the_match)
                c1+=1
                break
        if c1==0:
            man_of_the_match = ""
        
        innings_tables = soup.find_all('div', class_='ds-rounded-lg ds-mt-2')

        for innings_table in innings_tables:

            innings_number = innings_tables.index(innings_table) + 1

            team_innings_div = innings_table.find('div', class_='ds-flex ds-px-4 ds-border-b ds-border-line ds-py-3 ds-bg-ui-fill-translucent-hover')
            batting_innings = team_innings_div.text.strip().replace('\xa0',' ')
            batting_innings = self.find_team(batting_innings)
            for team in team_names:
                if team!= batting_innings:
                    bowling_innings = team
            innings_list.append(batting_innings)
            
            batsmen_table = innings_table.find('table', class_='ds-w-full ds-table ds-table-md ds-table-auto ci-scorecard-table')
        
            batting_info = batsmen_table.find('tbody')
            batting_info = batting_info.find_all('tr')

            for batter in batting_info:
                try:
                    batsman_stats = batter.find_all('td')
                    name = batsman_stats[0].text.strip()
                    if '†' in name:
                        name = name.replace('†','').strip()
                    if '(c)' in name:
                        name = name.replace('(c)','').strip()
                    name = find_full_name(player_list[batting_innings],name)
                    dismissal = batsman_stats[1].text.strip()
                    runs = int(batsman_stats[2].text.strip())
                    balls = int(batsman_stats[3].text.strip())
                    fours = int(batsman_stats[5].text.strip())
                    sixes = int(batsman_stats[6].text.strip())
                    strike_rate = float(batsman_stats[7].text.strip())
                    strike_rate = float(strike_rate)
                            
                    batsmen_stat = {'Innings Number': innings_number,
                        'Innings Name': batting_innings,
                        'Batsman': name,
                        'Dismissal': dismissal,
                        'Runs': runs,
                        'Balls': balls,
                        '4s': fours,
                        '6s': sixes,
                        'Strike Rate': strike_rate
                    }
                    batsmen_list = batsmen_list._append(batsmen_stat, ignore_index = True)
                except:
                    pass
                    
            bowling_table = innings_table.find('table', class_='ds-w-full ds-table ds-table-md ds-table-auto')

            if bowling_table:
                headers = []
                head_data = bowling_table.find_all('th')
                for bowler_header in head_data:
                    headers.append(bowler_header.text.strip())
                headers = list(map(lambda x: "Bowler" if x == "Bowling" else x, headers))
                headers = list(map(lambda x: "Overs" if x == "O" else x, headers))
                headers = list(map(lambda x: "Maidens" if x == "M" else x, headers))
                headers = list(map(lambda x: "Runs" if x == "R" else x, headers))
                headers = list(map(lambda x: "Wickets" if x == "W" else x, headers))
                headers = list(map(lambda x: "Economy" if x == "ECON" else x, headers))
                
                bowler_rows = bowling_table.find('tbody').find_all('tr')
                for row in bowler_rows:
                    bowler_data = {}
                    bowler_data['Innings Number'] = innings_number
                    bowler_data['Innings Name'] = batting_innings
                    bowler_row_data = row.find_all('td')

                    try:
                        for i in range(len(headers)):
                            if headers[i] in ["Maidens","Runs", "Wickets","0s"]:
                                bowler_data[headers[i]] = int(bowler_row_data[i].text.strip())
                            elif headers[i] in ["Overs","Economy"]:
                                overs_economy_data = float(bowler_row_data[i].text.strip())
                                bowler_data[headers[i]] = float(overs_economy_data)
                            elif headers[i] == "Bowler":
                                bowler = bowler_row_data[i].text.strip()
                                bowler = find_full_name(player_list[bowling_innings],bowler)
                                bowler_data[headers[i]] = bowler
                        bowlers_info = bowlers_info._append(bowler_data, ignore_index = True)
                    except:
                        pass
        #dismissal_list = batsmen_list['Dismissal'].tolist()
        #print(dismissal_list)
        return full_player_list,player_list, winner, man_of_the_match, catchers, stumpers, main_runouters, secondary_runouters, bowled, lbw, innings_list, batsmen_list, bowlers_info
    
    def printing_scorecard(self):
        print("Player List:")
        print(self.player_list)
        print()
        for innings in self.innings_list:
            print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")  
            print(innings + ":")
            print()
        
            print("Batsmen:")
            print(self.batsmen_list[self.batsmen_list['Innings Name'] == innings].drop(columns=['Innings Number', 'Innings Name']))
            print()

            print("Bowlers:")
            print(self.bowlers_info[self.bowlers_info['Innings Name'] == innings].drop(columns=['Innings Number', 'Innings Name']))
            print()

        print("Catchers:")
        print(self.catchers)
        print()

        print("Stumpings:")
        print(self.stumpers)
        print()

        print("Main Run Outs:")
        print(self.main_runouters)
        print()

        print("Secondary Run Outs:")
        print(self.secondary_runouters)
        print()
        
        print("Bowled:")
        print(self.bowled)
        print()
        
        print("LBW:")
        print(self.lbw)
        print()
        print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ") 
        print("Winner: ",self.winner)
        print()
        print("Man of the Match: ",self.man_of_the_match)
        
class Series:
    def __init__(self,url,cricbuzz_page_link,database_name):
        self.url = url
        self.cricbuzz_page_link = cricbuzz_page_link
        self.database_name = database_name
        self.match_objects = {}
        self.match_links = []
        match_links = self.match_link_generator()
        #self.player_list,self.team_links = self.TeamLinks()
        try:
            with open(self.database_name, "rb") as file:
                ipl = dill.load(file)
        except:
            ipl = {}
        match_objects = ipl
        match_links_list = list(ipl.keys())
        if len(match_links)>=len(match_links_list):
            for match in match_links:
                url = match
                if match not in match_links_list or match == match_links[-1]:
                    # if match == last_match_stored:
                    #     if 'full-scorecard' in last_match_stored:
                    #         break
                    #     else:
                    #         url = url.replace('live-cricket-score','full-scorecard')
                    try:
                        match_object = Score(url,self.cricbuzz_page_link)
                        match_objects[match] = match_object
                        print("Added:",url)
                    except:
                        print("Match Number",match,"Abandoned")
            if len(list(match_objects.keys())) == len(match_links):
                self.match_links = match_links
                #print(match_links)
                self.match_objects = match_objects
                with open(self.database_name, "wb") as file:
                    dill.dump(match_objects, file)
                print("LOADING SUCCESSFUL")
            else:
                print("No. of match objects",len(match_objects))
                print("Number of extracted links",len(match_links))
                print("Missing Links:")
                for match_url in match_links:
                    if match_url not in list(match_objects.keys()):
                        print(match_url)
        else:
            print("DATA UP TO DATE")
            self.match_objects = match_objects
            self.match_links = match_links

    def match_link_generator(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

        response = requests.get(self.url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        match_links = []
        match_boxes = soup.find_all('div')
        for match_box in match_boxes:     
            match_block = match_box.find('a',class_="ds-no-tap-higlight")
            try:
                link_part = match_block['href']
                abandoned = ""
                abandoned = match_block.find('p',class_='ds-text-tight-s ds-font-medium ds-line-clamp-2 ds-text-typo').text.strip()
                # print("Match Result:",abandoned)
                # print("Match url",link_part)
                if "Match yet to begin" in abandoned:
                    break
                if 'bandoned without a ball bowled' not in abandoned and 'bandoned with a toss' not in abandoned:
                    if "indian-premier-league" in link_part or "ipl-2025" in link_part:
                        if 'full-scorecard' in link_part:
                            match_link = "https://www.espncricinfo.com" + link_part
                            if match_link not in match_links:
                                match_links.append(match_link)
                        elif 'live-cricket-score' in link_part:
                            match_link = "https://www.espncricinfo.com" + link_part.replace('live-cricket-score','full-scorecard')
                            if match_link not in match_links:
                                match_links.append(match_link)
                            break
            except:
                pass
        return match_links
    
if __name__ == "__main__":  
    cricbuzz_page_link = "https://www.cricbuzz.com/cricket-series/7607/indian-premier-league-2024/matches"   
    ipl24_url = "https://www.espncricinfo.com/series/indian-premier-league-2024-1410320/match-schedule-fixtures-and-results"
    ipl2024 = Series(ipl24_url,cricbuzz_page_link)

