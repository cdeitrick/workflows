from pathlib import Path

from pipelines import systemio


def test_get_srun_command():
	assert systemio.get_srun_command() == ["srun", "--mem-per-cpu", "27000"]
	assert systemio.get_srun_command(8) == ["srun", "--cpus", 8, "--mem-per-cpu", "27000"]


def test_format_command():
	command = ["prokka", Path(__file__), "--threads", 8]
	expected = ["prokka", __file__, "--threads", "8"]
	assert systemio.format_command(command) == expected


def test_get_anaconda_install():
	expected = "/home/cld100/anaconda3/bin"
	assert systemio.get_anaconda_install() == Path(expected)


def test_check_output():
	assert systemio.check_output(["echo", "abc"]) == "abc\n"


def test_run_command_with_no_logfile_or_output_folder(command_runner):
	command = ["echo", "abcdefHIJ123"]

	command_runner.run(command, srun = False)


def test_run_command_with_no_output_folder(command_runner, tmp_path):
	logfile = tmp_path / "commandlog.sh"

	command = ["echo", "abcdefghIJKLM12345"]
	command_runner.command_log = logfile
	command_runner.run(command, srun = False)

	assert logfile.exists()
	# Only care about the command line for now.
	assert logfile.read_text().split('\n')[0] == "echo abcdefghIJKLM12345"


def test_run_command_with_output_folder(command_runner, tmp_path):
	output_folder = tmp_path / "output"
	output_folder.mkdir()

	command_runner.run(["echo", "abcdefghIJKLM12345"], output_folder, srun = False)

	assert (output_folder / "command.txt").exists()
	assert (output_folder / "stdout.txt").exists()
	assert (output_folder / "stderr.txt").exists()
