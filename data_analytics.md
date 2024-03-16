## Data Analytics in Finance
### Git
* Download for Windows: https://git-scm.com/download/win
* 安装Git: https://www.liaoxuefeng.com/wiki/896043488029600/896067074338496 
* 在Pycharm中使用Git: https://www.jianshu.com/p/f00064b4b947 
* 使用GitHub: https://github.com/fudansswebfundamental/Docs/blob/master/%E5%86%99%E7%BB%99%E6%96%B0%E6%89%8B%E7%9A%84%20Github%20%E6%8C%87%E5%8D%97.md 


### Python 
#### Reference
* PR1: https://docs.anaconda.com/free/anaconda/install/windows/ , https://www.jetbrains.com/pycharm/download/?section=windows 
* PR2: Python for Finance Cookbook Second Edition, Lewinson.  代码：https://github.com/erykml/Python-for-Finance-Cookbook-2E
#### 内容
* Session 1, 具体内容见python文件夹, 02-26 09:00AM
  * installation of Python (Anaconda and Jupyter notebook, pycharm, colab); PR1
  * data acquisition, manipulation, and visualisation. PR2-Ch01-05
  * regression analysis (CAPM, Fama & French 1993)  PR2-Ch08 
* Session 2, 03-03 09:00AM
  * Collaboration on GitHub
    * 参考 https://gist.github.com/belm/6989341 ，目前使用第三种合作者的方式。详细流程见 https://juejin.cn/post/6844904177139712013 
  * PCA and its application，见python文件夹 
  * System design and architecture 
    * 【一张图说明软件架构设计-核心关键点和底层逻辑-哔哩哔哩】 https://b23.tv/H5lY7Fz
    * 【python中如何组织项目代码-哔哩哔哩】 https://b23.tv/nlyVGFQ 
  * modelling volatility; PR2-Ch09， 见python文件夹 
  * Monte Carlo simulation; PR2-Ch10， 见python文件夹  
* Session 3, 03-17 09:00AM
  * python工程架构,一共两个工程，一个正经的，一个很随意的。见python文件夹 [python工程模板](python/python_project.md) 。  
  * 特征向量、PCA具体应用。
    * 特征值和特征向量：https://vincere.fun/posts/fc532062/# 推导第一个主成分的方向，对于相关矩阵来说的话，特征向量的方向是最大化方差的方向。我们想找一个能够解释相关性的办法。
    * PCA： 构建因子，做因子投资。经典模型需要明确指定因子结构，PCA方法认为人们并不知道真实的定价因子是什么，将真实的因子视为隐性因子latent factors, 通过提取资产收益协方差矩阵的主成份来估计因子暴露和因子的风险溢价，之后可以做资产配置，详见 [主成分分析和因子选择](pca_factor.pdf) 以及  https://finance.sina.cn/2020-07-23/detail-iivhvpwx7107494.d.html。
  * 我想问一下GARCH模型的原理是什么，解决什么问题。Barra 模型怎么用？ 收益模型和风险模型怎么能同时用于资产分配上？比如最小方差、最大多样化、风险平价、等权重分别是什么意思？
  * asset allocation; PR2-Ch11，代码见python文件夹，需要先更新requirements.txt里的依赖 
  * backtesting; PR2-Ch12, quantstats的比较那里有点问题，先注释掉了。 代码见python文件夹，需要先更新requirements.txt里的依赖 


### SQL
#### Reference 
SR1： https://zhuanlan.zhihu.com/p/347709270
#### 内容
操作的时候可以在 https://www.mycompiler.io/ 上做，由指数表和股票行情表计算每支股票的beta值。已经建好了，位于 https://www.mycompiler.io/view/ES0BIYAhpoT

数据分析常用的命令
* SELECT, DISTINCT, WHERE, IN, LIKE, ORDER BY
* JOIN
* 聚合函数,COUNT、MAX、MIN、SUM、AVG,  GROUP BY, HAVING
* 嵌套子查询

数据操作命令
可以忽略： 建库、建表、添加、删除、更新记录

### R
#### Reference 
RR1：https://bookdown.org/xiangyun/data-analysis-in-action/
#### 内容
可能相关的几个章节：
统计分析 03-24 09:00AM
数据建模-时序数据分析 03-31 09:00AM 

