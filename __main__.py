from pipelines import main
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
	"which",
	help = "assembly or variants.",
	type = str,
	choices = ['assembly', 'variants']
)

args = parser.parse_args()

if args.which == 'variants':
	main.main_workshop()
else:
	message = f" Not a vaid value: '{args.which}': {'variants', 'assembly'}"
	print("Not a possible value")