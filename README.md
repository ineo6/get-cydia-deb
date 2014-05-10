get-cydia-deb
=============

Python抓取cydia威锋源和178源的deb插件，并提供web访问端。代码写的不好，功能也很垃圾，仅供参考。

代码基于web.py框架编写,学习自[simplecd](https://code.google.com/p/simplecd/)

数据库是sqlite3,code.py是网站主程序,fetchvc.py是抓取脚本.

本来设想是程序能够每天自动抓取deb数据,但是经过尝试之后发现cydia源文件中新增的deb信息的位置似乎无法确定的,只能遍历整个文件来判断.

代码中没有定时抓取的设计,我也不想加了.

这样弄的也心烦了,都好几个月没搞了.想着就这样把,今天是心血来潮把代码上传到GitHub了.
