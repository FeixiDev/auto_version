# coding:utf-8

import commands
import re
import os
import datetime
import argparse


def get_current_tag():
    result = (commands.getoutput('git tag')).split()
    if result:
        return result[-1]

def create_tag(tag_name):
    commands.getoutput('git tag %s' % tag_name)

def git_commit(file_name, comment):
    commands.getoutput('git add %s' % file_name)
    commands.getoutput('git commit -m "change version info ,add new tag %s" ' % comment)

def change_version_in_code(file_name, strVersion):
    replace_version = "Version = '%s'" % strVersion
    old_str = r"Version = [a-zA-Z0-9_.']*"
    with open(file_name, 'r') as f1, open('ReplaceFile.py', 'w') as f2:
        for line in f1:
            f2.write(re.sub(old_str, replace_version, line, 1))
    os.remove(file_name)
    os.rename('ReplaceFile.py', file_name)

def time_now_tag():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # /%H:%M:%S

# 自动生成版本号
def auto_version(tag_name, file_name):
    create_tag(tag_name)
    change_version_in_code(file_name, tag_name)
    git_commit(file_name, tag_name)


class AutoCutVersion():
    def __init__(self, Filename):
        self.current_tag = get_current_tag()
        self.file_name = Filename
        self.auto_cut_version()

    def create_version(self, current_tag):
        self.test_version_tag = current_tag + '_test%s' % time_now_tag()

    def judge_test_version(self):
        if "_" in self.current_tag:
            list_tag = self.current_tag.split("_")
            self.create_version(list_tag[0])
        else:
            self.create_version(self.current_tag)

    def auto_cut_version(self):
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
        self.parser.add_argument('-a',
                                 '--auto_version',
                                 action="store",
                                 dest="auto_version",
                                 nargs=2,
                                 help="Please enter a file name and label name")
        self.parser.add_argument('-t',
                                 '--cut_test_version',
                                 action="store",
                                 dest="cut_test_version",
                                 help="Please enter a file name")

    def parser_version(self):
        # 需要判断用户输入的文件路径是否存在
        args = self.parser.parse_args()
        if args.cut_test_version:
            if os.path.isfile(args.cut_test_version):
                AutoCutVersion(args.cut_test_version)
            else:
                print("File path does not exist")
        elif args.auto_version:
            if os.path.isfile(args.auto_version[0]):
                auto_version(args.auto_version[1], args.auto_version[0])
            else:
                print("File path does not exist")
        else:
            self.parser.print_help()


if __name__ == '__main__':
    ParseVersion()
