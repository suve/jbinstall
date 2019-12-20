# jbinstall
A tool for Linux users that installs a selected JetBrains product inside `/opt`, adds a symlink inside `/usr/local/bin`
and sets up `.desktop` files (Start Menu entries) inside `/usr/local/share/applications`.


## But why?
- A single, system-wide installation saves space compared to multiple users each having their own copy.
- `/opt` is (usually) writable only by root - less risk of some malignant software (or user) corrupting the files.
- Having a symlink inside `/usr/local/bin` allows to start a program from a launcher or terminal.


## Usage
```
jbinstall FILE.TAR.GZ
```
Since **jbinstall** wants to put files inside `/opt` and `/usr`, you will need to run it as root.


## Licensing
This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License,
as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

For the full text of the licence, see `LICENCE.txt`.
