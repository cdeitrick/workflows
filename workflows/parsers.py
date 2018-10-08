import argparse

try:
	from . import read_assembly
	from . import annotation
	from . import read_quality
	from . import variant_callers
except:
	import read_assembly
	import annotation
	import read_quality
	import variant_callers


def define_parser():
	main_parser = argparse.ArgumentParser()

	subparsers = main_parser.add_subparsers(help = 'sub-command help')

	annotation_parser = annotation.get_commandline_parser(subparsers)
	assembly_parser = read_assembly.get_commandline_parser(subparsers)
	read_quality_parser = read_quality.get_commandline_parser(subparsers)
	caller_parser = variant_callers.get_commandline_parser(subparsers)

	return main_parser


if __name__ == "__main__":
	parser = define_parser()

	args = parser.parse_args()

	print(args)
