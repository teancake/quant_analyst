## 说明
* python我测试过能用的版包含：3.8, 3.9, 3.10

* 使用本文件夹下的 requirements.txt 创建虚拟环境，命令为
```
conda create --name fin python=3.8
conda activate fin 
pip install -r requirements.txt 
```
* TA-Lib 除了在python中安装之外 ，需要在操作系统中也安装库 https://github.com/TA-Lib/ta-lib-python?tab=readme-ov-file#windows 

* 使用jupyterlab运行所有的notebook, 命令为
```
jupyter-lab
```
会自动打开一个浏览器窗口。

* 几个notebook文件均修改过，只保留了能运行的部分。
* 有一少部分数据需要从Nasdaq Data Link https://data.nasdaq.com 下载，可以先注册个账号，之后拿到API key即可。

