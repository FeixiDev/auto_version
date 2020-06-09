# coding:utf-8

from __future__ import print_function
import subprocess
import re
import os
import datetime
import argparse


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
        subprocess.check_output(['git','tag',tag_name] )
    except subprocess.CalledProcessError as e:
        print('Error:', e)


def git_commit(file_name, version):
    try:
        subprocess.check_output(['git','add', file_name ] )
    except subprocess.CalledProcessError as e:
        print('Error:', e)
    try:
        subprocess.check_output(['git','commit','-m','change version info, add new tag %s' % version] )
    except subprocess.CalledProcessError as e:
        print('Error:', e)


def change_version_in_code(file_name, new_version):
    version = "VERSION = '%s'" % new_version
    old_str = r"VERSION = [a-zA-Z0-9_.']*"
    with open(file_name, 'r') as f1, open('ReplaceFile.py', 'w') as f2:
        for line in f1:
            f2.write(re.sub(old_str, version, line, 1))
    os.remove(file_name)
    os.rename('ReplaceFile.py', file_name)


def time_now_tag():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

# 自动生成版本号
def auto_version(tag_name, file_name):
    create_tag(tag_name)
    change_version_in_code(file_name, tag_name)
    git_commit(file_name, tag_name)


class CutTestVersion():
    def __init__(self, file_name):
        self.current_tag = get_current_tag()
        self.file_name = file_name
        self.cut_test_version()

    def create_version(self, current_tag):
        self.test_version_tag = current_tag + '_test%s' % time_now_tag()

    def judge_test_version(self):
        if "_" in self.current_tag:
            list_tag = self.current_tag.split("_")
            self.create_version(list_tag[0])
        else:
            self.create_version(self.current_tag)

    def cut_test_version(self):
        self.judge_test_version()
        change_version_in_code(self.file_name, self.test_version_tag)
        git_commit(self.file_name, self.test_version_tag)
        create_tag(self.test_version_tag)


class ParseVersion():
    def __init__(self):
        self.argparse_init()
        self.parser_version()

    def argparse_init(self):
        self.parser = argparse.ArgumentParser(prog='myprogram',
                                              description='Choose funciton')
        self.parser.add_argument(
            '-a',
            '--auto_version',
            action="store",
            dest="auto_version",
            nargs=2,
            help="Please enter a file name and label name")
        self.parser.add_argument(
            '-t',
            '--cut_test_version',
            action="store",
            dest="cut_test_version",
            help="Please enter a file name")

    def parser_version(self):
        args = self.parser.parse_args()
        if args.cut_test_version:
            CutTestVersion(args.cut_test_version) if os.path.isfile(
                args.cut_test_version) else print("File path does not exist")
        elif args.auto_version:
            auto_version(args.auto_version[1], args.auto_version[0]) if os.path.isfile(
                args.auto_version[0]) else print("File path does not exist")
        else:
            self.parser.print_help()


if __name__ == '__main__':
    ParseVersion()
