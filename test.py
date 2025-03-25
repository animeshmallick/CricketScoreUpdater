import argparse

parser = argparse.ArgumentParser(description="SeriesID and MatchID from Command Line")
parser.add_argument("--series", type=str, help="Enter Series ID")
parser.add_argument("--match", type=str, help="Enter Match ID")
args = parser.parse_args()

# Use arguments
print(f"Hello {args.name}, you are {args.age} years old!")
