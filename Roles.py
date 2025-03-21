from fuzzywuzzy import process
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import time

begin = time.time()

# Set up Chrome options
options = Options()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
}

# Set up WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Open the webpage
url = "https://www.espncricinfo.com/auction/ipl-2025-auction-1460972/sold-players"
driver.get(url)

# Wait for initial elements to load
time.sleep(1)

last_height = driver.execute_script("return document.body.scrollHeight")  # Get initial height

while True:
    # Scroll to the bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    # Wait for new content to load
    time.sleep(1)
    
    # Get new scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    
    # If no new content is loaded, break
    if new_height == last_height:
        print("No more new content. Stopping scroll.")
        break

    last_height = new_height  # Update the last height

print("Reached the bottom of the page.")
#print(driver.page_source)

player_list = []
position_list = []

soup = BeautifulSoup(driver.page_source, "html.parser")
table = soup.find('table',class_='ds-w-full ds-table ds-table-md ds-table-auto ds-overflow-scroll ds-scrollbar-hide').find('tbody')
players = table.find_all('tr')
for player in players:
    player_name = player.find('td').find('a',class_='ds-inline-flex ds-items-start ds-leading-none')
    name = player_name['title'].strip()
    player_link = "https://www.espncricinfo.com/"+player_name['href']
    response2 = requests.get(player_link, headers=headers)
    soup2 = BeautifulSoup(response2.content, "html.parser")
    grid = soup2.find('div',class_="ds-grid lg:ds-grid-cols-3 ds-grid-cols-2 ds-gap-4 ds-mb-8")
    info = grid.find_all('div')
    for part in info:
        if "Playing Role" in part.text:
            position = part.find('span').text.strip()
            print(name,position)
            break
    player_list.append(name)
    position_list.append(position)

#Close the browser
driver.quit()
end = time.time()
print(end-begin)

players = ['Travis Head','Varun Chakaravarthy','Rahul Chahar','Mukesh Choudhary','Harshit Rana','Ishant Sharma','Jaydev Unadkat','Mukesh Kumar','Abdul Samad','Riyan Parag','Khaleel Ahmed','Avesh Khan','Faf du Plessis','Arjun Tendulkar','Mohammed Shami','Shivam Dube','Lockie Ferguson','Josh Hazlewood','Prabhsimran Singh','Rishabh Pant','Corbin Bosch','Mohammed Siraj','Prasidh Krishna','Marcus Stoinis','Harpreet Brar','Rahmanullah Gurbaz','Rashid Khan','Washington Sundar','Hardik Pandya','Heinrich Klaasen','Rinku Singh','Nehal Wadhera','Romario Shepherd','Manav Suthar','Vijaykumar Vyshak','Himmat Singh','Ayush Badoni','Liam Livingstone','Nathan Ellis','Moeen Ali','Karn Sharma','Yashasvi Jaiswal','Shimron Hetmyer','Axar Patel','Mayank Yadav','Abhinav Manohar','Ashutosh Sharma','Rachin Ravindra','Shahrukh Khan','Anrich Nortje','Mayank Markande','Yuzvendra Chahal','Tushar Deshpande','Noor Ahmad','Kagiso Rabada','Marco Jansen',
'Virat Kohli','Abhishek Sharma','Jitesh Sharma','Harnoor Singh','Bhuvneshwar Kumar','Abishek Porel','Angkrish Raghuvanshi','Kuldeep Yadav','David Miller','Anuj Rawat','Josh Inglis','Kumar Kartikeya','Akash Deep','Rahul Tewatia','Ramandeep Singh','Sherfane Rutherford','Glenn Maxwell','Sandeep Sharma','Suryakumar Yadav','Shamar Joseph','Pat Cummins','Quinton de Kock','Ravichandran Ashwin',
'Jasprit Bumrah','Sai Sudharsan','Shreyas Iyer','Swastik Chikara','Rajvardhan Hangargekar','Manoj Bhandage','Nitish Rana','Rasikh Salam Dar','Deepak Chahar','MS Dhoni','Aaron Hardie','Priyansh Arya','Phil Salt','Sameer Rizvi','Mitchell Santner','Manish Pandey','Suyash Sharma','Kamlesh Nagarkoti','Will Jacks','Azmatullah Omarzai','Adam Zampa','Spencer Johnson','Jamie Overton','Shashank Singh','Rovman Powell','Suryansh Shedge','Maheesh Theekshana',
'Ruturaj Gaikwad','Shubman Gill','Mohit Sharma','Sai Kishore','Raj Bawa','Ishan Kishan','Mitchell Marsh','Nitish Kumar Reddy','Karim Janat','Yash Dayal','Bevon Jacobs','Ryan Rickelton','Rajat Patidar','Tristan Stubbs','Gerald Coetzee','Glenn Phillips','Tim David','Ravi Bishnoi','Donovan Ferreira','Jayant Yadav','Trent Boult','Jofra Archer','Akash Madhwal','Darshan Nalkande','Kwena Maphaka',
'KL Rahul','Arshdeep Singh','Aiden Markram','Sachin Baby','Dushmantha Chameera','Naman Dhir','Karun Nair','Wanindu Hasaranga','Arshad Khan','Devdutt Padikkal','Robin Minz','Shahbaz Ahmed','Mohsin Khan','Krunal Pandya','Ravindra Jadeja','Mitchell Starc','Sanju Samson','Jos Buttler','Atharva Taide','Musheer Khan','Devon Conway','Venkatesh Iyer',
'Andre Russell','Sunil Narine','Chetan Sakariya','T Natarajan','Ajinkya Rahane','Shreyas Gopal','Tilak Varma','Vijay Shankar','Shubham Dubey','Anukul Roy','Deepak Hooda','Harshal Patel','Rahul Tripathi','Lungi Ngidi','Matheesha Pathirana','Vaibhav Arora','Nicholas Pooran','Jake Fraser-McGurk','Sam Curran','Rohit Sharma','Mujeeb Ur Rahman','Anshul Kamboj','Mahipal Lomror'
]
final_player_list = []
for player in players:
    if 'Mujeeb' in player:
        final_player_list.append(('Mujeeb ur Rahman','BOWL'))
        continue
    if 'Corbin Bosch' in player:
        final_player_list.append(('Corbin Bosch','AR'))
        continue
    if 'Chetan Sak' in player:
        final_player_list.append(('Chetan Sakariya','BOWL'))
        continue
    if player in player_list:
        position = position_list[player_list.index(player)]
    else:
        best_match, score = process.extractOne(player, player_list)
        #best_match3, score, _ = process.extractOne(parts[0], player_list)
        if score>70:
            print(player,"Best Match",best_match)
            position = position_list[player_list.index(best_match)]
        else:
            print("Not found",player)
            position = ""
    if position!="":
        if "Allrounder" in position:
            position = "AR"
        elif "Wicketkeeper" in position:
            position = "WK"
        elif "Bowler" in position:
            position = "BOWL"
        elif "Batter" in position:
            position = "BAT"
        final_player_list.append((player,position))

names = []
roles = []
for player in final_player_list:
    name, role = player
    names.append(name)
    roles.append(role)

print(names)
print(roles)
