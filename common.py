import json
import time
import re
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from Player import Player


class Common:
    def __init__(self):
        self.driver = None
        self.url = "https://www.espncricinfo.com/series/{}/{}/{}"
        self.expand_overs_table = "//i[contains(@class,'icon-fullscreen_exit-outlined')]"
        self.teams_title = "//div[contains(@class,'ci-team-score')]//a/span"
        self.match_additional_details_xpath = "//div[@class='ds-w-full']//p/span"
        self.balls_details_from_over_xpath = "//div[@class='ds-border ds-border-line']//table//tr[{}]//td[{}]//div[contains(@class,'ds-mb-1.5')]//span"
        self.batsmen_xpath = "//th[text()='Batters']/ancestor::table//tbody[1]//tr[{}]//td"
        self.bowler_xpath = "//th[text()='Batters']/ancestor::table//tbody[2]//tr[{}]//td"
        self.save_scorecard_endpoint = "https://api.cricketipl.in/updateScorecard"
        self.lambda_db_detailed_scorecard_put_request_url = "https://ablminqly0.execute-api.ap-south-1.amazonaws.com/Prod/save_detailed_score"

    def open_cricket_score_page(self, series, match):
        if self.driver is None:
            options = Options()
            #options.add_argument("--headless")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            self.driver = webdriver.Chrome(options)
            self.driver.maximize_window()

        self.driver.get(self.url.format(series, match, 'live-cricket-score'))
        time.sleep(2)
        return self.driver

    def get_score_from_page(self, team):
        xpath = f"//a[@title='{team}']/parent::div/following-sibling::div"
        try:
            score = self.driver.find_element(By.XPATH, xpath)
            match = re.search(r'\((\d+\.?\d*)/(\d+) ov.*\)', score.text)
            if match:
                overs_played = float(match.group(1))
            else:
                overs_played =  20  # Default overs if not present

            match = re.search(r'(\d+)/?(\d*)', score.text.split(')')[-1].strip())
            if match:
                runs = int(match.group(1))
                wickets = int(match.group(2)) if match.group(2) else 10  # Default wickets if not present
            else:
                runs, wickets = 0, 10  # Fallback case

            return int(runs), int(wickets), float(overs_played)
        except Exception as e:
            return 0, 0, None

    def get_teams_name(self):
        teams = self.driver.find_elements(By.XPATH, self.teams_title)
        if len(teams) == 2:
            return [teams[0].text, teams[1].text]
        else:
            return [None, None]

    def get_balls_from_over(self, innings, over):
        innings_last_over_details = []
        innings_overs = self.driver.find_elements(By.XPATH, self.balls_details_from_over_xpath.format(over, innings + 1))
        if len(innings_overs) > 0:
            for ball in innings_overs:
                innings_last_over_details.append(ball.text)

        return innings_last_over_details

    def get_match_additional_details(self):
        return [self.driver.find_element(By.XPATH, self.match_additional_details_xpath).text]

    def get_batsmen(self, num):
        batsmen = self.driver.find_elements(By.XPATH, self.batsmen_xpath.format(num))
        if len(batsmen) >= 5:
            return [batsmen[0].text.split('\n')[0].strip(), batsmen[1].text, batsmen[2].text, batsmen[3].text, batsmen[4].text]
        else:
            return [None, None, None, None, None]

    def get_bowler(self, num):
        bowler = self.driver.find_elements(By.XPATH, self.bowler_xpath.format(num))
        if len(bowler) >= 5:
            return [bowler[0].text.split('\n')[0].strip(), bowler[1].text, bowler[2].text, bowler[3].text, bowler[4].text]
        else:
            return [None, None, None, None, None]

    def get_payload_data(self, series, match, over_id, teams, innings, over, match_status, additional_details,
                         team1_score, team2_score, batsmen, bowler, partnership, last_batsman, last_wicket_at,
                         this_over):
        return {'id': series + "&&" + match + "&&" + 'secondary',
                'source': "score_bot",
                'series_id': series, 'match_id': match, 'over_id': over_id,
                'teams': teams, "is_live": match_status != 'completed',
                'innings': innings, 'over': over,
                'match_details': match_status, 'match_additional_details': additional_details,
                'team1_score': team1_score,
                'team2_score': team2_score,
                'batsmen': batsmen, 'bowler': bowler,
                'this_over': this_over, 'partnership': partnership,
                'last_batsman' : last_batsman,
                'last_wicket_at': last_wicket_at}

    def get_primary_payload_data(self, series, match, innings, teams, over, match_status, additional_details,
                         team1_score, team2_score):
        return {'id': series + "&&" + match + "&&" + 'primary',
                'source': "score_bot",
                'teams': teams,
                "is_live": match_status == 'live',
                'innings': innings,
                'over': over,
                'match_details': match_status, 'match_additional_details': additional_details,
                'team1_score': team1_score,
                'team2_score': team2_score,
            }

    def get_secondary_payload_data(self, series, match, partnership, last_batsman, last_wicket_at, last_over, bowler, batsmen1, batsmen2):
        return {'id': series + "&&" + match + "&&" + 'secondary',
                'source': "score_bot",
                'partnership': partnership,
                'last_batsman': last_batsman,
                'last_wicket_at': last_wicket_at,
                'this_over': last_over,
                'bowler': bowler,
                "batsmen": {
                    "batsman1": batsmen1,
                    "batsman2": batsmen2
                }
            }

    def save_score_to_db(self, payload):
            return requests.post(self.save_scorecard_endpoint, json=payload)

    def get_partnership(self):
        try:
            return self.driver.find_element(By.XPATH, "//strong[contains(text(),\"P'SHIP\")]/parent::span/span").text
        except Exception:
            try:
                time.sleep(1)
                try:
                    self.driver.find_element(By.ID, "wzrk-cancel").click()
                except Exception:
                    pass
                time.sleep(1)
                return self.driver.find_element(By.XPATH, "//strong[contains(text(),'Partnership')]/parent::span/span").text
            except Exception as e:
                return " "

    def get_last_batsman(self):
        try:
            return self.driver.find_element(By.XPATH, "//span[contains(text(),'Last Bat')]/parent::strong/parent::span/span").text
        except Exception:
            try:
                time.sleep(1)
                try:
                    self.driver.find_element(By.ID, "wzrk-cancel").click()
                except Exception:
                    pass
                time.sleep(1)
                return self.driver.find_element(By.XPATH, "//span[contains(text(),'Last Bat')]/parent::strong/parent::span/span").text
            except Exception:
                return " "

    def get_last_wicket_at(self):
        try:
            return self.driver.find_element(By.XPATH, "//div[contains(@class,'ds-py-2 ds-border-line')]/span[3]").text.split(':')[1].strip()
        except Exception:
            try:
                time.sleep(1)
                try:
                    self.driver.find_element(By.ID, "wzrk-cancel").click()
                except Exception:
                    pass
                time.sleep(1)
                return self.driver.find_element(By.XPATH, "//div[contains(@class, 'ds-py-2 ds-border-line')]/span[3]").text.split(':')[1].strip()
            except Exception:
                return " "

    def open_overs_page(self, series, match):
        self.driver.get(self.url.format(series, match, 'match-overs-comparison'))
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        try:
            self.driver.find_element(By.XPATH, self.expand_overs_table).click()
        except Exception:
            pass
        time.sleep(1)

    def get_detailed_scorecard(self, series, match):
        self.driver.get(self.url.format(series, match, 'full-scorecard'))

        team2_batsmen = self.get_batsmen_player_details("//div[@class='ds-rounded-lg ds-mt-2'][2]//table[1]//tr[@class='']")
        team2_bowlers = self.get_bowler_player_details("//div[@class='ds-rounded-lg ds-mt-2'][2]//table[2]//tbody//tr[@class='']")
        team1_batsmen = self.get_batsmen_player_details("//div[@class='ds-rounded-lg ds-mt-2'][1]//table[1]//tr[@class='']")
        team1_bowlers = self.get_bowler_player_details("//div[@class='ds-rounded-lg ds-mt-2'][1]//table[2]//tbody//tr[@class='']")

        scorecard = {
            'id':  series + "&&" + match,
            'team1_batsmen': [player.to_dict() for player in team1_batsmen],
            'team1_bowlers': [player.to_dict() for player in team1_bowlers],
            'team2_batsmen': [player.to_dict() for player in team2_batsmen],
            'team2_bowlers': [player.to_dict() for player in team2_bowlers]
        }
        return scorecard;

    def save_detailed_scorecard(self, scorecard):
        return requests.put(self.lambda_db_detailed_scorecard_put_request_url, json=scorecard, headers={'ref_id': "Score_BOT_2"})

    def get_batsmen_player_details(self, xpath):
        players = []
        for row in self.driver.find_elements(By.XPATH, xpath):
            cols = row.find_elements(By.XPATH, "./td")
            if len(cols) < 6:
                break
            player_details = ""
            for col in cols:
                text = col.text.strip().replace("\n", "")
                player_details += text + "$$"
            if 'total' in player_details.lower():
                break
            player = Player(player_details.strip(), isBatsman=True)
            players.append(player)
        return players

    def get_bowler_player_details(self, xpath):
        players = []
        for row in self.driver.find_elements(By.XPATH, xpath):
            cols = row.find_elements(By.XPATH, "./td")
            player_details = ""
            for col in cols:
                text = col.text.strip().replace("\n", "")
                player_details += text + "$$"
            player = Player(player_details.strip(),  isBatsman=False)
            players.append(player)
        return players

    def get_last_balls(self):
        balls_container = self.driver.find_elements(By.CSS_SELECTOR, "div.ds-bg-fill-content-prime div.ds-mx-4 div.ds-overflow-x-auto span")
        balls = []
        for ballDiv in balls_container:
            if 'st' in ballDiv.text or 'nd' in ballDiv.text or 'rd' in ballDiv.text or 'th' in ballDiv.text or len(ballDiv.text) == 0:
                pass
            else:
                balls.append(ballDiv.text)

            if len(balls) == 12:
                break

        return balls

