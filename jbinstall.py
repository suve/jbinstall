#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# jbinstall - an installer for JetBrains products
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


def print_help():
	print(f"""jbinstall - an unofficial installer for JetBrains products
Usage:
  jbinstall [OPTIONS] ARCHIVE.TAR.GZ
Supported options:
  --help
    Print this help message and exit.
  --version
    Print program version information and exit.
""", end="")


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

	path = ""
	try:
		for dir in ["/usr", "/local", "/share", "/applications"]:
			path = path + dir
			if not os.path.exists(path):
				os.mkdir(path)
	except OSError as ex:
		print(f"jbinstall: Error while creating directory \"{path}\": {ex}", file=sys.stderr)
		exit(1)

	path = path + "/" + name + ".desktop"
	try:
		file = open(path, "w")
		file.write(content)
		file.close()
	except OSError as ex:
		print(f"jbinstall: Error while writing file \"{path}\": {ex}", file=sys.stderr)
		exit(1)


def parse_args():
	global PROGRAM_VERSION

	argc = len(sys.argv)
	if argc < 2:
		print("Usage: jbinstall FILE.TAR.GZ\nAlternatively, run \"jbinstall --help\" for more info.", file=sys.stderr)
		exit(1)

	if sys.argv[1] == "--help":
		print_help()
		exit(0)

	if sys.argv[1] == "--version":
		print(f"jbinstall v.{PROGRAM_VERSION} by suve")
		exit(0)

	archive_name = sys.argv[1]
	if not os.path.exists(archive_name):
		print(f"jbinstall: File \"{archive_name}\" does not exist", file=sys.stderr)
		exit(1)

	return archive_name


def main():
	archive_name = parse_args()
	try:
		tar = tarfile.open(archive_name, 'r:gz')
	except tarfile.TarError as ex:
		print(f"jbinstall: Error while opening archive \"{archive_name}\": {ex}", file=sys.stderr)
		exit(1)

	member = tar.next()
	rootdir = member.name.split("/")[0]
	program_name, program_version = rootdir.split("-")

	while member is not None:
		try:
			tar.extract(member, "/opt/")
			member = tar.next()
		except (tarfile.TarError, OSError) as ex:
			member = member.name
			print(f"jbinstall: Error while extracting file \"{member}\" from archive \"{archive_name}\": {ex}", file=sys.stderr)
			exit(1)

	write_desktop_file(rootdir, program_name, program_version)


if __name__ == "__main__":
	main()
