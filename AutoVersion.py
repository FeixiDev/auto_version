#coding:utf-8

import commands,re,os,datetime

## update version file
Filename = "Main.py"


def auto_version():
    AutoVersion()

def auto_cut_version(cut_type='test'):
    AutoCutVersion(cut_type)


class Source(object):
    def __init__(self):
        pass

    def get_last_tag(self):
        result = (commands.getoutput('git tag')).split()
        if result:
            return result[-1]

    #修改Main.py中的version变量
    def change_file_version(self,last_tag):
        replace_version = "Version = '%s'" % last_tag
        old_str = r"Version = [a-zA-Z0-9_.']*"
        with open(Filename, 'r') as f1, open('ReplaceFile.py', 'w') as f2:
            for line in f1:
                f2.write(re.sub(old_str, replace_version, line, 1))
        os.remove(Filename)
        os.rename('ReplaceFile.py', Filename)

    def change_version_commit(self,last_tag):
        commands.getoutput('git add %s' % Filename)
        commands.getoutput('git commit -m "change version info ,add new tag %s" ' % last_tag)

    def create_tag_cut(self,last_tag):
        commands.getoutput('git tag %s' % last_tag)

    def time_now_tag(self):
        return datetime.datetime.now().strftime('%Y%m%d')  #/%H:%M:%S


class AutoVersion(Source):
    def __init__(self):
        self.new_tag=self.get_last_tag()
        self.auto_version()

    def auto_version(self):
        if self.new_tag:
            self.change_file_version(self.new_tag)
            self.change_version_commit(self.new_tag)
        else:
            print('Failed to get tag')


class AutoCutVersion(Source):
    def __init__(self,cut_type):
        self.cut_type=cut_type
        self.new_tag = self.get_last_tag()
        self.auto_cut_version()

    def auto_cut_version(self):
        if self.new_tag:
            self.cut_tag = self.get_cut_tag()
            self.change_file_version(self.cut_tag)
            self.change_version_commit(self.cut_tag)
            self.create_tag_cut(self.cut_tag)
        else:
            print('Failed to get tag')

    def get_cut_type_tag(self,last_tag,cut_type):
        result = last_tag + '_%s%s' % (cut_type, self.time_now_tag())
        return result

    def get_cut_tag(self):
        if '_' in self.new_tag:
            list_new_tag = self.new_tag.split('_')
            result = self.get_cut_type_tag(list_new_tag[0],self.cut_type)
        else:
            result = self.get_cut_type_tag(self.new_tag,self.cut_type)
        return result



if __name__ == '__main__':
    pass
    #auto_version()
    auto_cut_version()