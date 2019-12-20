#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# jbinstall - an unofficial installer for JetBrains products
# Copyright (C) 2019 Artur "suve" Iwicki
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License, as published
# by the Free Software Foundation; either version 2 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program (LICENCE.txt). If not, see <https://www.gnu.org/licenses/>.
#
import os
import sys
import tarfile


PROGRAM_VERSION = "1.0"

Settings = dict()


def print_help():
	print(f"""jbinstall - an unofficial installer for JetBrains products
Usage:
  jbinstall [OPTIONS] ARCHIVE.TAR.GZ
Supported options:
  --help
    Print this help message and exit.
  --verbose
    Print extra information while running.
  --version
    Print program version information and exit.
""", end="")


def parse_args():
	global PROGRAM_VERSION
	global Settings

	archive_name = None
	verbose = False

	argc = len(sys.argv)
	if argc < 2:
		print("Usage: jbinstall FILE.TAR.GZ\nAlternatively, run \"jbinstall --help\" for more info.", file=sys.stderr)
		exit(1)

	a = 1
	while a < argc:
		arg = sys.argv[a]

		if arg.startswith("--"):
			if arg == "--help":
				print_help()
				exit(0)
			elif arg == "--verbose":
				verbose = True
				a += 1
			elif arg == "--version":
				print(f"jbinstall v.{PROGRAM_VERSION} by suve")
				exit(0)
			else:
				print(f"jbinstall: Unknown option \"{arg}\"", file=sys.stderr)
				exit(1)
		elif archive_name is not None:
			print("jbinstall: Cannot provide more than one archive name at a time", file=sys.stderr)
			exit(1)
		else:
			archive_name = arg

	if archive_name is None:
		print("jbinstall: You must provide an archive to install", file=sys.stderr)
		exit(1)

	if not os.path.exists(archive_name):
		print(f"jbinstall: File \"{archive_name}\" does not exist", file=sys.stderr)
		exit(1)

	Settings["archive_name"] = archive_name
	Settings["verbose"] = verbose


def mkdir_p(full_path):
	components = full_path.split("/")
	components.pop(0)  # Don't check if "/" exists

	path = "/"
	for component in components:
		path = path + component
		if not os.path.exists(path):
			try:
				os.mkdir(path)
			except OSError as ex:
				print(f"jbinstall: Error while creating directory \"{path}\": {ex}", file=sys.stderr)
				exit(1)


def generate_desktop_file(name, executable, icon):
	return f"""[Desktop Entry]
Type=Application
Version=1.0
Name={name}
Exec={executable} %F
Icon={icon}
Terminal=false
Categories=Development;IDE;
StartupNotify=true
"""


def write_desktop_file(root_dir, pretty_name, version):
	name = pretty_name.lower()
	exepath = "/opt/" + root_dir + "/bin/" + name

	content = generate_desktop_file(
		executable=exepath + ".sh",
		icon=exepath + ".png",
		name=pretty_name + " " + version)

	mkdir_p("/usr/local/share/applications")

	path = "/usr/local/share/applications/" + name + ".desktop"
	try:
		file = open(path, "w")
		file.write(content)
		file.close()
	except OSError as ex:
		print(f"jbinstall: Error while writing file \"{path}\": {ex}", file=sys.stderr)
		exit(1)


def create_symlink(root_dir, pretty_name):
	name = pretty_name.lower()
	exepath = "/opt/" + root_dir + "/bin/" + name + ".sh"

	mkdir_p("/usr/local/bin")
	linkpath = "/usr/local/bin/" + name

	try:
		os.symlink(exepath, linkpath)
	except OSError as ex:
		print(f"jbinstall: Failed to create symbolic link \"{linkpath}\": {ex}", file=sys.stderr)
		exit(1)


def archive_extract_info(tar):
	names = tar.getnames()

	root_dir = names[0].split("/")[0]
	program_name, program_version = root_dir.split("-")

	bin_path = root_dir + "/bin/" + program_name.lower() + ".sh"
	if bin_path not in names:
		print(
			f"jbinstall: Expected a \"{bin_path}\" member in the archive, but it's not present\n" +
			"jbinstall: Archive does not seem to contain a JetBrains product, exiting", file=sys.stderr)
		exit(1)

	for name in names:
		if "../" in name:
			print(f"jbinstall: Archive contains a dangerous path \"{name}\", refusing to continue", file=sys.stderr)
			exit(1)

	return root_dir, program_name, program_version


def archive_extract_contents(archive_name, archive_object, dest_path):
	for member in archive_object:
		try:
			archive_object.extract(member, dest_path)
		except (tarfile.TarError, OSError) as ex:
			member = member.name
			print(f"jbinstall: Error while extracting file \"{member}\" from archive \"{archive_name}\": {ex}", file=sys.stderr)
			exit(1)


def main():
	parse_args()

	archive_name = Settings["archive_name"]
	try:
		archive_obj = tarfile.open(archive_name, 'r:gz')
	except tarfile.TarError as ex:
		print(f"jbinstall: Error while opening archive \"{archive_name}\": {ex}", file=sys.stderr)
		exit(1)

	root_dir, program_name, program_version = archive_extract_info(archive_obj)
	archive_extract_contents(archive_name, archive_obj, "/opt")

	write_desktop_file(root_dir, program_name, program_version)
	create_symlink(root_dir, program_name)


if __name__ == "__main__":
	main()
