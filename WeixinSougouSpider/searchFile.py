import os

newdir = ""


class searchFile(object):

    def search(rootdir, searchdirname):
        if os.path.isdir(rootdir):
            # 分离路径和文件夹
            split1 = os.path.split(rootdir)

            # 判断是否为指定的文件夹
            if split1[1] == searchdirname:
                print('找到文件夹：%s' % (rootdir))
        else:
            # print '不是文件夹：%s' % (rootdir)
            return
