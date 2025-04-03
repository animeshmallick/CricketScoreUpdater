import time
import sys
import argparse
import math

from common import Common
common = Common()

parser = argparse.ArgumentParser(description="SeriesID and MatchID from Command Line")
parser.add_argument("--series", type=str, default="ipl-2025-1449924", help="Enter Series ID")
parser.add_argument("--match", type=str, help="Enter Match ID")
args = parser.parse_args()

if not args.match or len(args.match) == 0:
    print("Please provide Match ID.")
    sys.exit()

series= args.series
match = args.match

driver = common.open_cricket_score_page(series, match)
attempt = 1
while True:
    try:
        if attempt % 10 == 0:
            print("Refreshing Browser")
            x = time.time()
            driver = common.open_cricket_score_page(series, match)
            print(f"Time taken to refresh browser : {(time.time() - x):.2f}sec\n")
        else:
            time.sleep(2)
        start_time = time.time()
        print(f"Attempt : {attempt}")
        teams = common.get_teams_name()
        team1_runs, team1_wickets, team1_over = common.get_score_from_page(teams[0])
        team2_runs, team2_wickets, team2_over = common.get_score_from_page(teams[1])
        innings = 1 if team2_over is None else 2
        over = team1_over if innings == 1 else team2_over
        match_status = "Not Yet Started" if team1_over is None else "live"
        match_additional_details = common.get_match_additional_details()
        team1_score = {'runs' : team1_runs, 'wickets' : team1_wickets, 'over' : team1_over}
        team2_score = {'runs' : team2_runs, 'wickets' : team2_wickets, 'over' : team2_over}

        payload = common.get_primary_payload_data(series, match, innings, teams, over, match_status,
                                          match_additional_details, team1_score, team2_score)
        response = common.save_score_to_db(payload)
        print(f"Main Scorecard Saved in {(time.time() - start_time):.2f}sec with status : " + ("Success" if response.status_code == 201 else "Failed"))
    except Exception as e:
        print("=====================================================================\n")
        if driver is not None:
            driver.close()
    attempt += 1
