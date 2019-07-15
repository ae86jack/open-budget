import click
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from tqdm import tqdm
from urllib3.exceptions import MaxRetryError
import os
import time
import sys
from typing import List


@click.command()
@click.argument('local_dir',
                default='../../pdf_files/jszwfw', type=click.Path(exists=True))
@click.option('--url',
              default='http://127.0.0.1:4444/wd/hub',
              help="URL of the remote server. Defaults to 'http://127.0.0.1:4444/wd/hub'")
@click.option('--remote_dir',
              default='/home/seluser/Downloads/jszwfw',
              help="Remote download directory. Defaults to '/home/seluser/Downloads/jszwfw'")
@click.option('--start',
              default=1, type=int,
              help="The index of departments to start download. Index starts with 1, defaults to 1")
@click.option('--stop',
              default=None, type=int,
              help="The index of departments to stop download. Defaults to the last one index")
def run(local_dir, url, remote_dir, start, stop):
    """ 爬取江苏省预决算公开统一平台，下载部门预算公开PDF文件. 网址是http://www.jszwfw.gov.cn/yjsgk/list.do
    Examples:
    $python jszwfw_spider.py --start 1 --stop 5
    $python jszwfw_spider.py ../../pdf_files/jszwfw --start 1 --stop 5
"""
    if start < 1:
        click.secho('Invalid start. Index starts with 1', err=True, fg='red')
        return
    try:
        spider = JszwfwSpider(local_dir, url, remote_dir)
    except MaxRetryError:
        click.secho('selenium远程服务器的url配置出错, 连接不上.', err=True, fg='red')
        return
    spider.run(start=start, stop=stop)
    spider.quit()
    if spider.error_msg:
        click.secho(spider.error_msg, fg='red')


class JszwfwSpider:
    """ jszwfw 取名自域名www.jszwfw.gov.cn """
    def __init__(self, local_dir, url='http://127.0.0.1:4444/wd/hub', remote_dir='/home/seluser/Downloads/jszwfw'):
        self.local_dir = local_dir
        options = webdriver.ChromeOptions()
        options.add_experimental_option('prefs', {
            'download.default_directory': remote_dir,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True
        })
        self.driver = webdriver.Remote(
            command_executor=url,
            desired_capabilities=options.to_capabilities()
        )
        self.error_msg = ''

    def quit(self):
        self.driver.quit()

    def run(self, start=1, stop=None):
        title = '江苏省预决算公开统一平台首页'
        self.driver.get('http://www.jszwfw.gov.cn/yjsgk/list.do')
        WebDriverWait(self.driver, 5).until(EC.title_is(title))
        # print('window=', self.driver.current_window_handle, 'title=', title)

        ActionChains(self.driver).\
            move_to_element(self.driver.find_element_by_xpath('//div[text()="部门预决算公开"]')).perform()
        self.driver.find_element_by_xpath('//a[text()="部门预算公开"]').click()
        self._switch_to_new_window()

        WebDriverWait(self.driver, 15).until(
            EC.text_to_be_present_in_element((By.ID, 'mainTitle'), '部门预算公开'))
        # print('window=', self.driver.current_window_handle, 'title=', '部门预算公开')
        dept_page_handle = self.driver.current_window_handle
        dept_pages: List[WebElement] = self.driver.find_elements_by_xpath('//*[@id="department"]/li')

        i = start
        last = stop if stop and stop < len(dept_pages) else len(dept_pages)
        with tqdm(total=last - start + 1) as p_bar:
            while i <= last:
                dept_li = self.driver.find_element_by_xpath(f'//*[@id="department"]/li[{i}]')
                dept_a = dept_li.find_element_by_xpath('a')
                dept_name = dept_li.text
                click.echo(f'\n第{i}部门: ' + dept_name)
                if dept_a.size.get('width') <= dept_li.size.get('width'):
                    dept_a.click()
                else:
                    # 由于页面元素dept_a宽度会大于dept_li，而selenium点击的坐标是元素的中间，所以这种情况下点击dept_li
                    dept_li.click()
                self._get_dept_page(dept_name)
                p_bar.update(1)
                self.driver.back()
                self.driver.switch_to.window(dept_page_handle)
                i += 1

    def _switch_to_new_window(self):
        """  跳到新页面  """
        if self.driver.current_window_handle != self.driver.window_handles[-1]:
            self.driver.switch_to.window(self.driver.window_handles[-1])

    def _get_dept_page(self, dept_name: str):
        main_title = '·部门预算公开'
        try:
            WebDriverWait(self.driver, 15).until(
                EC.text_to_be_present_in_element((By.ID, 'mainTitle'), main_title))
        except TimeoutException:
            self.error_msg += '\n' + dept_name + '·部门预算公开, 解析页面出错. 可能是链接失效.'
            return
        page_handle = self.driver.current_window_handle
        # print('window=', self.driver.current_window_handle, 'title=', dept_name + main_title)
        pdf_pages = self.driver.find_elements_by_xpath('//*[@id="contentTitle"]/li')
        for file_page in pdf_pages:
            file_a = file_page.find_element_by_xpath('a')
            # pdf_page_name = file_a.text
            file_a.click()
            self._download_pdf_page(dept_name)
            self.driver.close()
            self.driver.switch_to.window(page_handle)

    @staticmethod
    def _get_filename(file_title: str):
        """ 附件1：xxx.pdf -> xxx.pdf """
        if '：' in file_title:
            return file_title[file_title.index('：') + 1:]
        return file_title

    def _download_pdf_page(self, dept_name):
        self._switch_to_new_window()
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, 'filespreview')))
        head_text = self.driver.find_element_by_xpath('//*[@id="headText"]').text
        # print('pdf page window=', self.driver.current_window_handle, 'title=', head_text)

        dept_dir = f'{self.local_dir}/{dept_name}'
        if not os.path.exists(dept_dir):
            os.mkdir(dept_dir)

        files_preview = self.driver.find_elements_by_xpath('//*[@id="filespreview"]/li')
        for file_preview in files_preview:
            file_title = file_preview.find_element_by_xpath('a').text
            filename = self._get_filename(file_title)
            file_preview.find_element_by_xpath('div[@id="download"]').click()

            is_downloaded = self._rename_file(filename, dept_dir)
            if is_downloaded:
                click.echo(' ' * 6 + filename)
            else:
                click.secho(' ' * 6 + f'下载{filename}失败或超时', fg='red')

    def _rename_file(self, filename, dept_dir, wait_for_seconds=300):
        for i in range(0, wait_for_seconds):
            try:
                if filename in os.listdir(self.local_dir):
                    os.rename(f'{self.local_dir}/{filename}', f'{dept_dir}/{filename}')
                    return True
                time.sleep(1)
            except FileNotFoundError:
                click.echo('文件目录不对. 请检查文件目录设置', err=True, fg='red')
                sys.exit(1)
        return False


if __name__ == '__main__':
    run()
