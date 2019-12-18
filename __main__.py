from pipelines import main
import argparse


def create_parser()->argparse.Namespace:
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"which",
		help = "assembly or variants.",
		type = str,
		choices = ['assembly', 'variants']
	)

	args = parser.parse_args()

	return args
if __name__ == "__main__":

	main.main_shelly()