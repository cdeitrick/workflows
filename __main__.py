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

main.main_shelly()