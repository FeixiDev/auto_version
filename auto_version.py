# coding:utf-8

from __future__ import print_function
import subprocess
import re
import os
import datetime
import argparse
import sys


def check_tag_name(string):
    re_tag_name = re.compile(
        r'^v\d+\.\d+\.\d+(-(Alpha|Beta|RC|Release|R))?$')
    result = re_tag_name.match(string)
    if result:
        return True
    else:
        print("Incorrect version name format, please enter again!")
        sys.exit()


def checkout_position(position):
    try:
        subprocess.check_output(['git', 'checkout', position])
    except subprocess.CalledProcessError as e:
        print('Error:', e)


def get_current_tag():
    try:
        output = subprocess.getoutput('git tag').strip()
    except Exception as e:
        output = subprocess.check_output(['git', 'tag']).strip()
    result = str(output).split('\n')
    if result:
        return result[-1]


def create_tag(tag_name):
    try:
        subprocess.check_output(['git', 'tag', tag_name])
    except subprocess.CalledProcessError as e:
        print('Error:', e)


def git_commit(file_name, version):
    try:
        subprocess.check_output(['git', 'add', file_name])
    except subprocess.CalledProcessError as e:
        print('Error:', e)
    try:
        subprocess.check_output(
            ['git', 'commit', '-m', 'change version info, add new tag %s' % version])
    except subprocess.CalledProcessError as e:
        print('Error:', e)


def change_version_in_code(file_name, new_version):
    version = "VERSION = '%s'" % new_version
    old_str = r"VERSION\s*=\s*[\'\"]+[a-zA-Z0-9_.\- ]*[\'\"]+"
    with open(file_name, 'r') as f1, open('ReplaceFile.py', 'w') as f2:
        for line in f1:
            f2.write(re.sub(old_str, version, line, 1))
    os.remove(file_name)
    os.rename('ReplaceFile.py', file_name)


def time_now_tag():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')


# 自动生成版本号


def auto_version(tag_name, id=None):
    if id:
        checkout_position(id)
    file_name = 'consts.py'
    change_version_in_code(file_name, tag_name)
    git_commit(file_name, tag_name)
    create_tag(tag_name)


class CutTestVersion():
    def __init__(self, tag_name=None):
        self.tag_name = tag_name
        self.file_name = 'consts.py'
        self.cut_test_version()

    def create_version(self, tag_name):
        self.test_version_tag = tag_name + '_test%s' % time_now_tag()

    def get_test_version(self):
        if self.tag_name:
            self.create_version(self.tag_name)
        else:
            self.tag_name = get_current_tag()
            if "_" in self.tag_name:
                list_tag = self.tag_name.split("_")
                self.create_version(list_tag[0])
            else:
                self.create_version(self.tag_name)

    def cut_test_version(self):
        if self.tag_name:
            checkout_position(self.tag_name)
        self.get_test_version()
        change_version_in_code(self.file_name, self.test_version_tag)
        git_commit(self.file_name, self.test_version_tag)
        create_tag(self.test_version_tag)


class ParseVersion():
    def __init__(self):
        self.argparse_init()
        # self.auto_version()

    def argparse_init(self):
        self.parser = argparse.ArgumentParser(prog='auto_version',
                                              description='This tool is used to assist in version release')
        # self.parser.add_argument(
        #     '-a',
        #     '--auto_version',
        #     action="store",
        #     dest="auto_version",
        #     help="Please enter a Tag name")
        # self.parser.add_argument(
        #     '-t',
        #     '--cut_test_version',
        #     action="store_true",
        #     dest="cut_test_version",
        #     help="Generate the latest test version number")

        self.subparser = self.parser.add_subparsers(metavar='', dest='subargs')

        self.par_version = self.subparser.add_parser(
            'auto',
            help="Generate an official version.")

        self.par_version.add_argument(
            '-id',
            '--commit_id',
            action="store",
            dest="commit_id",
            nargs='?',
            help="Commit ID. Generate a version on this commit.")

        self.par_version.add_argument(
            'version',
            action="store",
            help="Version name.")

        self.par_test_version = self.subparser.add_parser(
            'test',
            help="Generate a test version.")

        self.par_test_version.add_argument(
            '-tag',
            action="store",
            dest="tag_name",
            help="Tag name. Generate a test version with this Tag.")

        self.par_version.set_defaults(func=self.get_auto_version)
        self.par_test_version.set_defaults(func=self.get_test_version)
        self.parser.set_defaults(func=self.print_help_massage)

    def print_help_massage(self, args):
        self.parser.print_help()

    def print_version_help(self):
        self.par_version.print_help()

    def print_test_version_help(self):
        self.par_test_version.print_help()

    def get_auto_version(self, args):
        check_tag_name(args.version)
        if args.commit_id:
            auto_version(args.version, args.commit_id)
        else:
            auto_version(args.version)

    def get_test_version(self, args):
        if args.tag_name:
            check_tag_name(args.tag_name)
            CutTestVersion(args.tag_name)
        else:
            CutTestVersion()

    def parse(self):  # 调用入口
        args = self.parser.parse_args()
        args.func(args)


def main():
    cmd = ParseVersion()
    cmd.parse()


if __name__ == '__main__':
    main()
    # ParseVersion()
