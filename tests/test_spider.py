from click.testing import CliRunner
from open_budget.spider.jszwfw_spider import run, JszwfwSpider


def test_cli():
    runner = CliRunner()
    result = runner.invoke(run, ['../pdf_files/jszwfw', '--start', '1', '--stop', '5'])
    assert result.exit_code == 0


def test_run():
    spider = JszwfwSpider(local_dir='../pdf_files/jszwfw')
    spider.run(start=1, stop=5)
    spider.quit()
    if spider.error_msg:
        print(spider.error_msg)
