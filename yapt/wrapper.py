#!/usr/bin/python3
"""
extends 'apt search' functionality
adding a selection menu to the search that allows to install
selected packages
"""

import re
import sys
import subprocess
from yapt.confighandler import ConfigHandler

PKG_NAME = re.compile(r'(^[^/^\s]+)')
# Package names consist of any char except blankspaces from the start of the line until a '/'
#
# Example off 'apt search firefox':
# "firefox/xenial-updates,xenial-security,now 50.0.2+build1-0ubuntu0.16.04.1 amd64"
# "  Safe and easy web browser from Mozilla"
#
# It will only match 'firefox'

INSTALLED = re.compile(r'(\[[^0-9].*\]$)')
# Installed packages will contain a string at the end like: [installed]
# I added [^0-9] to don't match colors like "black": '\x1b[30m'


class Wrapper(object):
    """Manages 'apt search' output and adds installation functionality"""

    def __init__(self, search_term, no_confirm=False,
                 nocolor=False, debug=False):
        self._conf = ConfigHandler(nocolor)  # color configuration
        self._no_confirm = no_confirm  # install without asking for confirmation
        self._debug = debug  # True install packages, False print builded command
        self._search_term = search_term
        self._all_packages = []  # list of all available packages for a search
        self._pkg_counter = 1  # counter to prepend on package name
        self._output = self._build_output()  # lines processed

    @staticmethod
    def _process_apt_search(search_term):
        """Cleans 'apt search' output"""
        txt = subprocess.check_output(["apt", "search", search_term])
        txt = txt.decode(sys.stdout.encoding)  # from byte to string
        lines = txt.splitlines()
        if len(lines) <= 2:
            print("No results")
            sys.exit(0)

        del lines[:2]
        return lines

    def _add_pkg_number_and_colorize_line(self, line):
        """
        Colorizes line if has a package name and prepends a number
        :param line:
        :return: same line with colored package name and installed string if exists
        """
        line = re.sub(PKG_NAME, self._conf.color['num'] +
                      str(self._pkg_counter) + self._conf.color['reset'] + " " +
                      self._conf.color['pkg'] + r"\1" +
                      self._conf.color['reset'], line)
        line = re.sub(INSTALLED, self._conf.color['ins'] +
                      r"\1" + self._conf.color['reset'], line)

        return line

    def _process_line(self, line):
        """
        Extracts package names and processes line (number and color) for the final menu
        :param line:
        :return:
        """
        search_pkg = PKG_NAME.search(line)
        if search_pkg is not None:  # if this line has a package name, colorize output
            self._all_packages.append(search_pkg.group(1))  # add package
            line = self._add_pkg_number_and_colorize_line(line)
            self._pkg_counter += 1

        return line

    def _build_output(self):
        """Creates a colored output using 'apt search' output"""
        output = [self._process_line(line) for line in self._process_apt_search(self._search_term)]
        return output

    def print_instructions(self):
        """Prints input instructions"""
        arrow = self._conf.color['arr'] + "==>" + self._conf.color['reset']
        print(arrow, "Enter # of packages to install (ex: 1 2 3 or 1-3)")
        print(arrow, "-------------------------------------------------")

    @staticmethod
    def _process_input(inp):
        """
        Takes a string as an argument with a format of "1 2 3 7 9" or "1-3 7 9"
        and returns a list [1,2,3,7,9]. If input is not in that format breaks.
        """
        if not inp or inp.isspace():  # if empty input or full of spaces
            sys.exit(1)
        else:
            inp = inp.split()

        pkg_numbers = []
        for item in inp:
            if len(item) > 1:
                try:
                    pkg_numbers.append(int(item))
                except ValueError:
                    ran = item.split("-")
                    if ran[0] > ran[1]:
                        sys.exit("Ranges must be in ascending order")
                    pkg_numbers += list(range(int(ran[0]), int(ran[1]) + 1))
            else:
                pkg_numbers.append(int(item))

        pkg_numbers.sort()
        pkg_numbers = list(set(pkg_numbers))

        return pkg_numbers

    def get_packages_to_install(self, inp):
        """
        Takes a string as an argument with a format of "1 2 3" or "1-3"
        and returns a list with the correspondent packages ["vim", "vim-gtk"]
        """
        pkg_numbers = self._process_input(inp)

        if pkg_numbers[-1] > len(self._all_packages):
            # pkg_numbers is a sorted list so if the highest value is higher than max number of packages available
            # input is not valid
            sys.exit("Invalid package number")

        pkg2install = [self._all_packages[item - 1] for item in pkg_numbers]
        return pkg2install

    def install_packages(self, inp):
        """
        Takes a string as an argument with a format of "1 2 3" or "1-3"
        and install correspondents packages. If debug mode is activated
        shows the installation command but doesn't execute it
        """
        packages = self.get_packages_to_install(inp)
        command = ["sudo", "apt", "install"] + packages
        if self._no_confirm:
            command += ["-y"]
        if self._debug:
            print(" ".join(command))
        else:
            subprocess.call(command)

    def print_output(self):
        """Prints output line by line"""
        for line in self._output:
            print(line)
