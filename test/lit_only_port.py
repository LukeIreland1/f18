#!/usr/bin/env python3
""" lit_only_port.py

    Ports ctest style F18 tests to be compatible with lit

    Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
    See https://llvm.org/LICENSE.txt for license information.
    SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

"""

import argparse
import os
import re
import shlex
import sys
import subprocess
from pathlib import Path
from git import Repo

from test_splitter import TestSplitter

F18_BIN = "~/f18/build/install/bin"
F18_TEST = "~/f18/build-f18/test-lit"

ROOT = Path.cwd()
while ROOT.name != "f18":
    ROOT = ROOT.parent
ERROR_TEMPLATE = "!RUN: %S/test_errors.sh %s %flang\n"
SYMBOL_TEMPLATE = "!RUN: %S/test_symbols.sh %s %flang\n"
MODFILE_TEMPLATE = "!RUN: %S/test_modfile.sh %s %f18\n"
GENERIC_TEMPLATE = "!RUN: %S/test_any.sh %s %flang\n"
FOLDING_TEMPLATE = "!RUN: %S/test_folding.sh %s %flang\n"
PREPROCESS_TEMPLATE = "!RUN: %flang -E %s\n"
XFAIL_TEMPLATE = "!XFAIL: *\n"
FAILS = []
CLEAN_CMAKE = True
TS = TestSplitter()

repo = Repo(ROOT)
INDEX = repo.index


def make_test_dir(test):
    dirname = test.parent.name
    output = ROOT.joinpath("test-lit", dirname)
    if not output.exists():
        try:
            output.mkdir(parents=True)
        except PermissionError:
            print(
                "Invalid permission to create directory at given path {}".format(
                    output
                ),
                file=sys.stderr)
            exit(1)
    return dirname, output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input", nargs='+',
        help="Run the porter on (a) test(s) or test suite(s)")
    parser.add_argument(
        "--output", '-o',
        help="Save the ported file(s) in the specified directory. \
        If no directory is specifed, the program will try to find \
        an appropriate output directory.")
    parser.add_argument(
        "--clean", "-c", action='store_true',
        help="Remove old tests from output directory"
    )
    parser.add_argument(
        "--glob", "-g", action='store_true',
        help="Glob files. Default behaviour will only get files in the \
        immediate input path"
    )
    args = parser.parse_args()

    output = ""
    if args.output:
        output = Path(args.output)
        if output.exists():
            if not output.is_dir():
                print(
                    "Output path should be a directory or not set",
                    file=sys.stderr)
                exit(1)
        else:
            try:
                output.mkdir(parents=True)
            except PermissionError:
                print(
                    "Invalid permission to create directory at given path {}".format(
                        output
                    ),
                    file=sys.stderr)
                exit(1)

    tests = []
    for filename in args.input:
        path = Path(filename)
        if path.is_dir():
            if args.glob:
                tests += [f for f in path.glob('**/*') if f.is_file()]
            else:
                tests += [f for f in path.iterdir() if f.is_file()]
        elif path.is_file():
            tests.append(path)

    tests = [test for test in tests if test.name in TS.tests]
    if not tests:
        print("No tests found", file=sys.stderr)
        exit(1)
    else:
        dirname = ""
        outputs = []
        for test in tests:
            if not output or test.parent.name != dirname:
                dirname, output = make_test_dir(test)

            if args.clean:
                suffixes = ['.f', '.F']
                for suffix in suffixes:
                    if list(output.glob('**/*{}*'.format(suffix))) != 0:
                        for old_test in TS.tests:
                            path = output.joinpath(old_test)
                            if path.exists():
                                path.unlink()

            port_test(test, output)
            if output.exists():
                outputs.append(output)

        print("Adding new tests to git")
        INDEX.add([str(output.resolve().relative_to(ROOT)) for output in outputs])
    if CLEAN_CMAKE:
        tests = [test for test in tests if test not in FAILS]
        clean_up(tests)
    if FAILS:
        for fail in FAILS:
            print("Test {} failed".format(fail))
    else:
        print("No fails detected")


def get_template(test_type):
    template = ""
    if test_type == "ERROR":
        template = ERROR_TEMPLATE
    elif test_type == "SYMBOL":
        template = SYMBOL_TEMPLATE
    elif test_type == "MODFILE":
        template = MODFILE_TEMPLATE
    elif test_type == "GENERIC":
        template = GENERIC_TEMPLATE
    elif test_type == "FOLDING":
        template = FOLDING_TEMPLATE
    elif test_type == "PREPROCESS":
        template = PREPROCESS_TEMPLATE
    return template


def port_test(filename, output):
    test = filename.name
    savepath = output.joinpath(test)
    rel_path = output.resolve().relative_to(ROOT)
    print("Porting {} to {}".format(test, rel_path))
    test_type = TS.get_test_type(test)
    template = get_template(test_type)

    lines = []
    try:
        with filename.open(encoding="utf-8") as read_file:
            lines = read_file.readlines()
    except IOError as e:
        print(
            "Could not open {} because {}".format(
                filename, e.strerror), file=sys.stderr)
        FAILS.append(test)

    if test_type == "GENERIC":
        lines = [line.replace("RUN", "EXEC") for line in lines]

    if test in TS.xfail_tests:
        lines.insert(0, XFAIL_TEMPLATE)

    # Add lit run line to test
    lines.insert(0, template)

    try:
        with savepath.open('w', encoding="utf-8") as write_file:
            write_file.writelines(lines)
        print("{} completed".format(test))
    except IOError as e:
        print(
            "Could not write to {} because {}".format(
                savepath, e.strerror), file=sys.stderr)
        FAILS.append(test)


def clean_up(tests):
    sem_cmake = TS.semantics_cmake_path
    eval_cmake = TS.evaluate_cmake_path
    sem_lines = []
    eval_lines = []
    file_strings = [str(test.resolve().relative_to(ROOT)) for test in tests]
    INDEX.remove(file_strings, working_tree=True)
    with sem_cmake.open() as read_file:
        sem_lines = read_file.readlines()
    with eval_cmake.open() as read_file:
        eval_lines = read_file.readlines()
    for test in tests:
        test = test.name
        if test in TS.folding_tests:
            eval_lines = [line for line in eval_lines if test not in line]
        elif test in TS.semantics_tests:
            sem_lines = [line for line in sem_lines if test not in line]
    with sem_cmake.open('w') as write_file:
        write_file.writelines(sem_lines)
    with eval_cmake.open('w') as write_file:
        write_file.writelines(eval_lines)


main()
