import json
import os
import requests
import colorama
from colorama import Fore, Style
import msvcrt

colorama.init()

#replacements = [
#    b"\x1b[33m",
#    b"\x1b[92m",
#    b"\x1b[0m",
#    b"\x1b[31m",
#    b"\x1b[36m"
#]

replacements = [
    Fore.CYAN.encode('utf-8'),
    Style.RESET_ALL.encode('utf-8'),
    Fore.RED.encode('utf-8'),
    Fore.YELLOW.encode('utf-8'),
    Fore.LIGHTGREEN_EX.encode('utf-8')
]

class Ranks:
    MVP = f"[{Fore.CYAN}MVP{Style.RESET_ALL}]"
    MVP_PLUS = f"[{Fore.CYAN}MVP{Fore.RED}+{Style.RESET_ALL}]"
    VIP_PLUS = f"[{Fore.LIGHTGREEN_EX}VIP{Fore.YELLOW}+{Style.RESET_ALL}]"
    VIP = f"[{Fore.LIGHTGREEN_EX}VIP{Style.RESET_ALL}]"
    NON = f"[NON]{Style.RESET_ALL}"
    MVP_PLUS_PLUS = f"[{Fore.YELLOW}MVP{Fore.RED}++{Style.RESET_ALL}]"
    
    def get_color_by_rank(name, rank):
        if rank == Ranks.MVP or rank == Ranks.MVP_PLUS:
            return Fore.CYAN + name + Style.RESET_ALL
        elif rank == Ranks.VIP or rank == Ranks.VIP_PLUS:
            return Fore.LIGHTGREEN_EX + name + Style.RESET_ALL
        elif rank == Ranks.MVP_PLUS_PLUS:
            return Fore.YELLOW + name + Style.RESET_ALL
        else:
            return name

with open("config.json") as json_file:
    CONFIG = json.loads(json_file.read())

user = os.getlogin() # gets environment username

latest_logs = None

if CONFIG['mc_type'] == "lunar" or CONFIG['mc_type'] == 'lc':
    latest_logs = rf'C:\Users\{user}\.lunarclient\offline\multiver\logs\latest.log' #  fix 0.11
else:
    raise NotImplementedError('{} support has not yet been implemented.'.format(CONFIG["mc_type"]))

prev_players = {}

def find(string, char):
    res = []
    for i, c in enumerate(string):
        if c == char:
            res.append(i+2)
    return res

def get_api_key():
    occurrences = []
    if latest_logs is None:
        os.system("cls")
        print()
        quit()
    with open(latest_logs, "r") as f:
        for line in f:
            if "[CHAT] Your new API key is " in line:
               occurrences.append(line)
    
    
    api_key = occurrences[-1].split("[CHAT] Your new API key is ")[-1].replace("\n", "")
    print(api_key)
    return api_key


if CONFIG["apikey"] == "":
    CONFIG["apikey"] = get_api_key()

  
def get_players():
    occurrences = []
    if latest_logs is None:
        print("An error has occurred with reading the latest logs file.")
        quit(1)
    with open(latest_logs, 'r') as f:
        for line in f:
            if "[CHAT] ONLINE:" in line:
                occurrences.append(line)


    line = occurrences[-1].split(":")[-1].strip()
    players = line.split(", ")
    return players
    
    
def grab_users_data(name):
    if name in prev_players:
        return prev_players[name]
    api_key = CONFIG["apikey"]
    res = requests.get(f"https://api.hypixel.net/player?key={api_key}&name={name}")
    res = json.loads(res.text)
    if res["success"]:
        try:
            bw_stats = res['player']['stats']['Bedwars']
        except:
            return None
        user_bedwars_stats = {}
        #user_bedwars_stats["mcVrp"] = res['player']['mcVersionRp']
        user_bedwars_stats["played_games"] = bw_stats['games_played_bedwars']
        user_bedwars_stats["wins"] = bw_stats['wins_bedwars']
        user_bedwars_stats["losses"] = bw_stats['losses_bedwars']
        user_bedwars_stats["mvp_pp"] = False
        
        try:
            a = res['player']['monthlyPackageRank']
            if a == "SUPERSTAR":
                user_bedwars_stats["mvp_pp"] = True
        except:
            pass
        
        try:
            fdeaths = bw_stats['final_deaths_bedwars']
            fkills = bw_stats['final_kills_bedwars']

            user_bedwars_stats["fkdr"] = round(fkills/fdeaths, 1)
        except:
            user_bedwars_stats["fkdr"]
        
        user_bedwars_stats["lvl"] = res['player']['achievements']['bedwars_level']
        try:
            user_bedwars_stats["ws"] = bw_stats['winstreak']
        except KeyError:
            user_bedwars_stats["ws"] = 0
        try:
            rank = res['player']['newPackageRank'] 
        except:
            rank = None
        if rank is None:
            rank = "[NON]"
        else:
            if rank == "MVP_PLUS":
                if user_bedwars_stats["mvp_pp"]:
                    rank = Ranks.MVP_PLUS_PLUS
                else:
                    rank = Ranks.MVP_PLUS
            elif rank == "VIP_PLUS":
                rank = Ranks.VIP_PLUS
            elif rank == "VIP":
                rank = Ranks.VIP
            elif rank == "MVP":
                rank = Ranks.MVP
                
        user_bedwars_stats["name"] = Ranks.get_color_by_rank(name, rank)
        user_bedwars_stats['rank'] = rank
        prev_players[name] = user_bedwars_stats
        
        return user_bedwars_stats
        
    
    else:
        return res["cause"]

design_ln1 = "|    Name:                      Stars:    Wins:     Ttl. Games:      WS:    FKDR:  |"
design_ln2 = "|=============================|=========|========|=================|======|========|"
#             | [rank] [name]                 [stars]      [ttlwins]     [ttlgames]     [ws]      [fkdr]

def say_player(player_name):
    res = ""
    stats = grab_users_data(player_name)
    
    if isinstance(stats, str) or stats is None:
        return None

    all_indexes = find(design_ln2, "|")
    all_indexes[0] = all_indexes[0] - 2
    # [1, 31, 46, 60, 79, 105]
    a = ""
    for i in range(len(design_ln2)):
        res_2 = res.encode('utf-8')
        for item in replacements:
            res_2 = res_2.replace(item, b"")
        len_of_res = len(res_2)
        if len_of_res in all_indexes:
            if len_of_res == all_indexes[0]:
                res += f"| {stats['rank']} {stats['name']}"
            elif len_of_res == all_indexes[1]:
                res += str(stats['lvl'])
            elif len_of_res == all_indexes[2]:
                res += str(stats['wins'])
            elif len_of_res == all_indexes[3]:
                res += str(stats['played_games'])
            elif len_of_res == all_indexes[4]:
                res += str(stats['ws'])
            elif len_of_res == all_indexes[5]:
                res += str(stats['fkdr'])
            else:
                res += " "
        else:
            if len_of_res >= len(design_ln2):
                return res[:-1] + "|"
            res += " "
    return res + "|"



def main():
    print("""Make sure you have auto who mod enabled!
    -Kindest regards, Corger.
    (press any key to start and 'q' to exit)""")
    
    while True:
        key = msvcrt.getch()
        os.system("cls")
        if key == 'q'.encode('utf-8'):
            quit()
        players = get_players()
        print(design_ln1)
        print(design_ln2)
        for player in players:
            res = say_player(player)
            if res is not None:
                print(res)

if __name__ == '__main__':
    main()
