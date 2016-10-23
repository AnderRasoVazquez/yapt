#!/usr/bin/python3
"""
Handles configuration for yapt.
"""

import re
import sys
import subprocess
import argparse
import configparser
from pathlib import Path


FORECOLORS = {
    "black": '\x1b[30m',
    "red": '\x1b[31m',
    "green": '\x1b[32m',
    "yellow": '\x1b[33m',
    "blue": '\x1b[34m',
    "magenta": '\x1b[35m',
    "cyan": '\x1b[36m',
    "white": '\x1b[37m',
    "none": '\x1b[39m'
}

BACKCOLORS = {
    "black": '\x1b[40m',
    "red": '\x1b[41m',
    "green": '\x1b[42m',
    "yellow": '\x1b[43m',
    "blue": '\x1b[44m',
    "magenta": '\x1b[45m',
    "cyan": '\x1b[46m',
    "white": '\x1b[47m',
    "none": '\x1b[49m'
}

RESETSTYLE = '\x1b[0m'

PKGCOLOR = FORECOLORS['green'] + BACKCOLORS['none']
NUMBERCOLOR = FORECOLORS['red'] + BACKCOLORS['none']
INSTALLEDCOLOR = FORECOLORS['black'] + BACKCOLORS['yellow']
ARROWCOLOR = FORECOLORS['yellow'] + BACKCOLORS['none']


class ConfigHandler(object):
    """
    This class manages the configuration info of Yapt
    """

    def __init__(self, no_colored_output=False):
        self.color = {}
        if no_colored_output:
            self.color['pkg'] = RESETSTYLE
            self.color['num'] = RESETSTYLE
            self.color['ins'] = RESETSTYLE
            self.color['arr'] = RESETSTYLE
            self.color['reset'] = RESETSTYLE
        else:
            self.color = ConfigHandler.get_user_config()
            if not self.color:
                # if self.color empty it means that the user doesn't
                # have a configuration file, so self.color will
                # have default values
                self.color['pkg'] = PKGCOLOR
                self.color['num'] = NUMBERCOLOR
                self.color['ins'] = INSTALLEDCOLOR
                self.color['arr'] = ARROWCOLOR
                self.color['reset'] = RESETSTYLE

    @staticmethod
    def get_config_file_path():
        """
        Checks if '/home/user/.yaptrc' or '/home/user/.config/yaptrc' exist.
        If it does returns the path, if it does not returns an empyt string.
        """
        config_path = ""
        home = Path.home().as_posix()

        cfg_filename = ".yaptrc"
        path = Path(home + "/" + cfg_filename)
        if path.exists():
            config_path = path.as_posix()
        else:
            cfg_filename = "yaptrc"
            path = Path(home + "/.config/yapt/" + cfg_filename)
            if path.exists():
                config_path = path.as_posix()

        return config_path

    @staticmethod
    def is_valid(col, colortype="none"):
        """
        Cheks if the color provided is a valid color. If it is not a valid
        color raises a ValueError exception.
        """
        col = col.lower()
        colors = ["black", "red", "green", "yellow", "blue",
                  "magenta", "cyan", "white", "none"]
        if col not in colors:
            raise ValueError(col, "is not a Valid color")

        if colortype == "none":
            col = RESETSTYLE
        elif colortype == "fore":
            col = FORECOLORS[col]
        elif colortype == "back":
            col = BACKCOLORS[col]

        return col

    @staticmethod
    def get_user_config():
        """
        Returns a dictionary containing user's color config
        """
        usr_conf = {}
        path = ConfigHandler.get_config_file_path()
        if path:
            try:
                config = configparser.ConfigParser()
                config.read(path)
                aux_conf = {}
                section_colors = "Colors"
                aux_conf['pkgfore'] = ConfigHandler.is_valid(
                    config.get(section_colors, "pkgfore"), "fore")
                aux_conf['pkgback'] = ConfigHandler.is_valid(
                    config.get(section_colors, "pkgback"), "back")
                aux_conf['numfore'] = ConfigHandler.is_valid(
                    config.get(section_colors, "numfore"), "fore")
                aux_conf['numback'] = ConfigHandler.is_valid(
                    config.get(section_colors, "numback"), "back")
                aux_conf['insfore'] = ConfigHandler.is_valid(
                    config.get(section_colors, "insfore"), "fore")
                aux_conf['insback'] = ConfigHandler.is_valid(
                    config.get(section_colors, "insback"), "back")
                aux_conf['arrfore'] = ConfigHandler.is_valid(
                    config.get(section_colors, "arrfore"), "fore")
                aux_conf['arrback'] = ConfigHandler.is_valid(
                    config.get(section_colors, "arrback"), "back")

                usr_conf['pkg'] = aux_conf['pkgfore'] + aux_conf["pkgback"]
                usr_conf['num'] = aux_conf['numfore'] + aux_conf["numback"]
                usr_conf['ins'] = aux_conf['insfore'] + aux_conf["insback"]
                usr_conf['arr'] = aux_conf['arrfore'] + aux_conf["arrback"]
                usr_conf['reset'] = RESETSTYLE

            except configparser.NoOptionError as err:
                sys.exit("Configuration file error: {0}".format(err))

        return usr_conf


class Yapt(object):
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
                              str(cont) + RESETSTYLE + " " +
                              self._conf.color['pkg'] + r"\1" +
                              RESETSTYLE, line)
                line = re.sub(installed, self._conf.color['ins'] +
                              r"\1" + RESETSTYLE, line)
                cont += 1
            output += line + '\n' if (index < len(self._lines) - 1) else line
        return output

    def print_instructions(self):
        """Prints input intructions"""
        arrow = self._conf.color['arr'] + "==>" + RESETSTYLE
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


def main():
    """
    Takes command line arguments and executes searches and installations
    acording to them
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--noconfirm",
                        action="store_true",
                        help="don't ask for confirmation.")
    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="debug mode (don't execute command).")
    parser.add_argument("-n", "--nocolor",
                        action="store_true",
                        help="no colored output.")
    parser.add_argument("pkg", help="the package to search.", type=str)
    args = parser.parse_args()

    try:
        yapt = Yapt(args.pkg, args.noconfirm, args.nocolor, args.debug)
        print(yapt.get_output())
        yapt.print_instructions()
        yapt.install_packages(input())
    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == '__main__':
    main()
