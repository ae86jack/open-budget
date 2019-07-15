
# Open budget: 政府预算公开

财政预算公开是构建阳光政府的需要。政府最近这几年开始把财政预算文件公开，放到网站上去。但是文件相对很散，数据方面的可读性也不好。所以我想做爬虫，然后解析，可视化。  
爬虫用的是[selenium](https://github.com/SeleniumHQ/selenium)。     
政府网站上的预算公开文件，通常是pdf文件，数据在表格内，解析用的是[camelot](https://github.com/atlanhq/camelot)。  
可视化用的是[Dash](https://github.com/plotly/dash)。


## 爬虫模块 
![Example](./docs/spider_demo.svg)
上面录屏做了以下操作：
1. 启动selenium docker服务
2. 启动pipenv shell环境
3. 进入爬虫目录，运行`python jszwfw_spider.py --start 1 --stop 5`, 脚本默认是爬取所有部门，耗时很久，这里演示只爬取第1到第5部门。
4. 进入pdf文件目录，用tree命令查看下载的pdf文件。

## 文件目录说明
open-budget  
├── jupyter -- jupyter镜像     
├── open_budget  
├    └── parser -- 解析下载文件模块    
├    └── spider -- 爬虫模块  
├    └── viewer -- 可视化模块  
├── docker-compose.yml -- docker compose启动脚本  
├── Pipfile  -- Pipenv的包文件

## Installation 安装

**Note:** 版本要求：Python3.6+，代码用到Python 3.6的新特性，比如类型提示，f-string。 

### 安装Camelot

camelot需要安装一些系统依赖, tk和ghostscript, [依赖安装链接](https://camelot-py.readthedocs.io/en/master/user/install-deps.html)

### Using pip

<pre>
$ pip install -r requirements.txt
</pre>

### Using pipenv

建议用[Pipenv](https://github.com/pypa/pipenv)安装，Pipenv是个非常好用的好用的python虚拟环境和包管理工具，集成了pip，virtualenv两者的功能。

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