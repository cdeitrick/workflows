from pipelines import main
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
	"which",
	help = "assembly or variants.",
	type = str
)

args = parser.parse_args()

if args.which == 'variants':
	main.main_workshop()
else:
	print("Not a possible value")