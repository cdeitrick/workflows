import pytest
from workflows import common


def test_get_srun_command():
	expected = ["srun", '--threads', '16'"--mail-user=cld100@pitt.edu", "--mail-type=end,fail"]
	command = common.get_srun_command('16')

	assert expected == command


def test_get_output_folder():
	pass
