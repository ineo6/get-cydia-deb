#! /usr/bin/env python
#coding=utf-8
#python gzip module
import os
import gzip
import bz2

class decomper:
    
    #压缩包文件所在位置
    FILE_PATH = 'download/'
    #package文件存放位置
    PACK_FILE_PATH = 'pack/'

    def unbz2(self,bzfile,savename):
        print('reading bz2')
        if os.path.isfile(bzfile):
            if os.path.exists(savename):
                print('the packages [{}] is exist!'.format(savename))        
            with bz2.BZ2File(bzfile, 'r') as b:
                with open(savename, 'wb') as p:
                    #b=bz2.decompress(b.read())
                    p.writelines(b)
                    return savename
        
            
    def ungz(self,gzpath,savename):
        print ('reading gz')
        if os.path.isfile(gzpath):
            if os.path.exists(savename):
                print('the packages [{}] is exist!'.format(savename))        
            with gzip.open(gzpath, 'rb') as g:
                with open(savename, 'wb') as p:
                    p.writelines(g)
                    return savename
  

    def decomp(self,file,packname):
        ext=os.path.splitext(file)[1]
        if ext == '.gz':
            result=self.ungz(self.FILE_PATH+file,self.PACK_FILE_PATH+packname)
        elif ext == '.bz2':
            result=self.unbz2(self.FILE_PATH+file,self.PACK_FILE_PATH+packname)
        return result