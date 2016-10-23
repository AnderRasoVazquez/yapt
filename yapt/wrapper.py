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


class Wrapper(object):
    """Manages 'apt search' output and adds installation functionality"""

    def __init__(self, searchterm, noconfirm=False,
                 nocolor=False, debug=False):
        self._conf = ConfigHandler(nocolor)
        # install without asking for confirmation
        self._noconfirm = noconfirm
        # True install packages, False print command
        self._debug = debug
        # lines unprocessed
        self._lines = self._generate_lines(searchterm)
        # list of all available packages
        self._allpkg = self._extract_all_pkg()
        # lines processed
        self._output = self._build_output()

    @staticmethod
    def _generate_lines(searchterm):
        """Cleans 'apt search' output"""
        txt = subprocess.check_output(["apt", "search", searchterm])
        lines = txt.splitlines()
        if len(lines) <= 2:
            print("No results")
            sys.exit(0)

        del lines[:2]
        return lines

    def get_all_pkg(self):
        """Returns a list with all the packages available to install"""
        return self._allpkg

    def _extract_all_pkg(self):
        pkg_name = re.compile(r'(^[0-9a-z-]+)')

        allpkg = []

        for line in self._lines:
            line = line.decode(sys.stdout.encoding)
            search_pkg = pkg_name.search(line)
            if search_pkg is not None:
                allpkg.append(search_pkg.group(1))

        return allpkg

    def _build_output(self):
        """Creates a colored multiline string using 'apt search' output"""
        pkg_name = re.compile(r'(^[0-9a-z-]+)')
        installed = re.compile(r'(\[[a-zA-záéíóú\s,]+\])')

        cont = 1
        output = ""

        for index, line in enumerate(self._lines):
            line = line.decode(sys.stdout.encoding)
            search_pkg = pkg_name.search(line)
            if search_pkg is not None:
                line = re.sub(pkg_name, self._conf.color['num'] +
                              str(cont) + self._conf.color['reset'] + " " +
                              self._conf.color['pkg'] + r"\1" +
                              self._conf.color['reset'], line)
                line = re.sub(installed, self._conf.color['ins'] +
                              r"\1" + self._conf.color['reset'], line)
                cont += 1
            output += line + '\n' if (index < len(self._lines) - 1) else line
        return output

    def print_instructions(self):
        """Prints input intructions"""
        arrow = self._conf.color['arr'] + "==>" + self._conf.color['reset']
        print(arrow, "Enter # of packages to install (ex: 1 2 3 or 1-3)")
        print(arrow, "-------------------------------------------------")

    @staticmethod
    def _process_input(inp):
        """
        Takes a string as an argument with a format of "1 2 3" or "1-3"
        and returns a list [1,2,3]. If input is not in that format breaks.
        """
        if not inp or inp.isspace():  # if empty input or full of spaces
            sys.exit(1)
        else:
            inp = inp.split()

        pkgnumbers = []
        for item in inp:
            if len(item) > 1:
                try:
                    pkgnumbers.append(int(item))
                except ValueError:
                    ran = item.split("-")
                    if ran[0] > ran[1]:
                        sys.exit("Ranges must be in ascending order")
                    pkgnumbers += list(range(int(ran[0]), int(ran[1])+1))
            else:
                pkgnumbers.append(int(item))

        pkgnumbers.sort()
        pkgnumbers = list(set(pkgnumbers))

        return pkgnumbers

    def get_pkgs_to_install(self, inp):
        """
        Takes a string as an argument with a format of "1 2 3" or "1-3"
        and returns a list with the correspondent packages ["vim", "vim-gtk"]
        """
        pkgnumbers = self._process_input(inp)

        if pkgnumbers[-1] > len(self._allpkg):
            sys.exit("Invalid package number")

        pkg2install = []
        for item in pkgnumbers:
            pkg2install.append(self._allpkg[item-1])

        return pkg2install

    def install_packages(self, inp):
        """
        Takes a string as an argument with a format of "1 2 3" or "1-3"
        and install correspondents packages. If debug mode is activated
        shows the installation command but doesn't execute it
        """
        pkgs = self.get_pkgs_to_install(inp)
        command = ["sudo", "apt", "install"] + pkgs
        if self._noconfirm:
            command += ["-y"]
        if self._debug:
            print(" ".join(command))
        else:
            subprocess.call(command)

    def get_output(self):
        """
        Returns builded (cleaned and colored) output
        """
        return self._output
