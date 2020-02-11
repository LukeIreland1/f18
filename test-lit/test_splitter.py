#!/usr/bin/env python3
""" test_splitter.py

    Aids lit_port.py in finding tests from the CMakeLists.txt specifying tests.

    Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
    See https://llvm.org/LICENSE.txt for license information.
    SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
"""

import argparse
import re
from pathlib import Path


class TestSplitter:
    def __init__(self):
        self.error_tests = []
        self.modfile_tests = []
        self.symbol_tests = []
        self.generic_tests = []
        self.folding_tests = []
        self.preprocess_tests = []
        self.xfail_tests = []
        root = Path(__file__).resolve()
        while root.name != "f18":
            root = root.parent
        self.root = root
        self.test_path = root.joinpath("test")
        self.semantics_path = self.test_path.joinpath("Semantics")
        self.semantics_cmake_path = self.semantics_path.joinpath(
            "CMakeLists.txt")
        self.evaluate_path = self.test_path.joinpath("Evaluate")
        self.evaluate_cmake_path = self.evaluate_path.joinpath(
            "CMakeLists.txt")
        self.preprocess_path = self.test_path.joinpath("Preprocessing")
        self.get_semantics_tests()
        self.get_folding_tests()
        self.get_preprocess_tests()
        self.semantics_tests = (self.error_tests + self.modfile_tests +
                                self.symbol_tests + self.generic_tests)
        self.tests = (self.semantics_tests +
                      self.folding_tests + self.preprocess_tests)

    def get_test_type(self, test):
        if test in self.error_tests:
            return "ERROR"
        elif test in self.symbol_tests:
            return "SYMBOL"
        elif test in self.modfile_tests:
            return "MODFILE"
        elif test in self.generic_tests:
            return "GENERIC"
        elif test in self.folding_tests:
            return "FOLDING"
        elif test in self.preprocess_tests:
            return "PREPROCESS"

    def get_semantics_tests(self):
        with self.semantics_cmake_path.open() as read_file:
            current_test_set = None
            for line in read_file.readlines():
                match = re.match(r"^set\((.*)$", line)
                if match:
                    if match.group(1) == "ERROR_TESTS":
                        current_test_set = self.error_tests
                    elif match.group(1) == "MODFILE_TESTS":
                        current_test_set = self.modfile_tests
                    elif match.group(1) == "SYMBOL_TESTS":
                        current_test_set = self.symbol_tests
                    else:
                        current_test_set = self.generic_tests
                elif re.match(r".*\..*f[90|\]| \n]", line):
                    if current_test_set is None:
                        continue
                    if line.strip().startswith("#"):
                        match = re.match(r".*#\s*(.*\.f.*)", line.lower())
                        if match:
                            self.xfail_tests.append(match.group(1))
                            current_test_set.append(match.group(1))
                            continue
                    if "*" in line:
                        path = Path(self.semantics_path)
                        pattern = line.strip().split("*")[0] + "*"
                        for test in list(path.glob(pattern)):
                            current_test_set.append(test.name)
                    else:
                        current_test_set.append(line.strip())

    def get_folding_tests(self):
        with self.evaluate_cmake_path.open() as read_file:
            for line in read_file.readlines():
                if line.strip().endswith(".f90"):
                    self.folding_tests.append(line.strip())

    def get_preprocess_tests(self):
        if self.preprocess_path.exists():
            self.preprocess_tests = [t.name for t in self.preprocess_path.iterdir() if t.is_file()]


def main():
    ts = TestSplitter()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--error", "-e", help="Display error tests", action="store_true")
    parser.add_argument(
        "--symbol", "-s", help="Display symbol tests", action="store_true")
    parser.add_argument(
        "--modfile", "-m", help="Display modfile tests", action="store_true")
    parser.add_argument(
        "--generic", "-g", help="Display generic tests", action="store_true")
    parser.add_argument(
        "--folding", "-f", help="Display folding tests", action="store_true")
    parser.add_argument(
        "--preprocess", "-p", help="Display preprocessing tests", action="store_true")
    parser.add_argument(
        "--xfail", "-u", help="Display xfail tests", action="store_true")
    parser.add_argument(
        "--all", "-a", help="Display all tests", action="store_true")
    parser.add_argument(
        "--info", "-i", help="Display info about tests", action="store_true")
    args = parser.parse_args()
    if args.info:
        print(
            """
Semantics has:
{} Error Tests
{} Symbol Tests
{} Modfile Tests
{} Generic Tests

Evaluate has:
{} Folding Tests

Preprocessing has:
{} tests
""".format(
                len(ts.error_tests), len(ts.symbol_tests),
                len(ts.modfile_tests), len(ts.generic_tests),
                len(ts.folding_tests), len(ts.preprocess_tests)
            )
        )
    if args.error:
        for test in ts.error_tests:
            print(test)
    if args.symbol:
        for test in ts.symbol_tests:
            print(test)
    if args.modfile:
        for test in ts.modfile_tests:
            print(test)
    if args.generic:
        for test in ts.generic_tests:
            print(test)
    if args.folding:
        for test in ts.folding_tests:
            print(test)
    if args.preprocess:
        for test in ts.preprocess_tests:
            print(test)
    if args.xfail:
        for test in ts.xfail_tests:
            print(test)
    elif args.all:
        for test in ts.error_tests:
            print(str(test) + " (ERROR)")
        for test in ts.symbol_tests:
            print(str(test) + " (SYMBOL)")
        for test in ts.modfile_tests:
            print(str(test) + " (MODFILE)")
        for test in ts.generic_tests:
            print(str(test) + " (GENERIC)")
        for test in ts.folding_tests:
            print(str(test) + " (FOLDING)")
        for test in ts.preprocess_tests:
            print(str(test) + " (PREPROCESS)")
        for test in ts.xfail_tests:
            print(str(test) + " (UNSUPPORTED)")


if __name__ == '__main__':
    main()
