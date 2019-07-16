
# Open budget: 政府预算公开

财政预算公开是构建阳光政府的需要。政府最近这几年开始把财政预算文件公开，放到网站上去。但是文件相对很散，数据方面的可读性也不好。所以我想做爬虫，然后解析，可视化。  
爬虫框架[selenium](https://github.com/SeleniumHQ/selenium)，可视化框架[Dash](https://github.com/plotly/dash)。 
政府网站上的预算公开文件，通常是pdf文件，数据在表格内，解析表格数据用的是[camelot](https://github.com/atlanhq/camelot)。  



## 爬虫模块 

![Example](docs/svg/demo_spider.svg)

上面录屏做了以下操作：
1. 启动selenium服务 `docker-compose up -d selenium-chrome-debug`
2. 启动pipenv shell环境 `pipenv shell`
3. 进入爬虫目录`cd open_budget/spider`，运行`python jszwfw_spider.py --start 1 --stop 5`, 脚本默认是爬取所有部门，耗时很久，这里演示只爬取第1到第5部门。
4. 进入pdf文件目录`cd ../../pdf_files`，用`tree`命令查看下载的pdf文件。

## 解析表格数据模块

![Example](docs/svg/demo_parser.svg)

上面录屏做了以下操作：
1. 启动pipenv shell环境 `pipenv shell`
2. 进入解析模块目录`cd open_budget/parser`， 运行`python ../../pdf_files/jszwfw/江苏省人大办公厅`，把pdf里的表格数据解析为csv。目前暂时只解析收支预算总表。

由于pdf文件里面的表格大多不规范，解析需要做些参数调整。项目里的[camelot.ipynb](./camelot.ipynb)里面写了参数，同时写了可视化结果，方便调试参数。  
docker-compose.yml里的jupyter-budget服务，登录密码是`passwd`。

如果在解析pdf时候，camelot报错，可能是pdf文件有问题。可以用`mutool clean xxx.pdf`修复pdf文件。[Mupdf官网](https://mupdf.com/), [deb安装文件链接。](http://ppa.launchpad.net/ubuntuhandbook1/apps/ubuntu/pool/main/m/mupdf)

## 可视化模块

  用Pandas读取csv文件，然后在Dash中展示。该功能尚在完善中，TODO.

## 文件目录说明
<pre>
open-budget  
├── jupyter -- jupyter镜像     
├── open_budget  
├    └── parser -- 解析表格数据模块    
├    └── spider -- 爬虫模块  
├    └── viewer -- 可视化模块  
├── camelot.ipynb -- camelot调试参数  
├── docker-compose.yml -- docker compose启动脚本  
├── Pipfile  -- Pipenv的包文件
</pre>

## Installation 安装

**Note:** 版本要求：Python3.6+，代码用到Python 3.6的新特性，比如类型提示，f-string。 

### 安装Camelot

camelot需要安装一些系统依赖, tk和ghostscript, [依赖安装链接](https://camelot-py.readthedocs.io/en/master/user/install-deps.html)

### Using pip

<pre>
$ pip install -r requirements.txt
</pre>

### Using pipenv

建议用[Pipenv](https://github.com/pypa/pipenv)安装，Pipenv是个非常好用的python虚拟环境和包管理工具，集成了pip，virtualenv两者的功能，很方便实现一个项目一个虚拟环境，跟其他环境独立开来。`pipenv install`会使用当前目录下的Pipfile。

<pre>
$ pipenv install
</pre>

### 安装Selenium Docker环境

[Selenium Docker官方镜像链接](https://github.com/SeleniumHQ/docker-selenium)  
在本项目的`docker-compose.yml`中提供了`selenium-chrome-debug`服务。

<pre>
$ docker-compose up -d selenium-chrome-debug
</pre>

端口4444是服务提供接口， 端口5900是远程桌面VNC server的端口，密码是`secret`，用于可视化调试。VNC Viewer[下载链接](https://www.realvnc.com/en/connect/download/viewer/)