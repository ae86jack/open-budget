from open_budget.parser.pdf_parser import run, BaseParser
from click.testing import CliRunner


def test_parse():
    runner = CliRunner()
    result = runner.invoke(run, ['../pdf_files/jszwfw'])
    assert result.exit_code == 0


def test_base_parser():
    parser = BaseParser()
    assert parser.strip('1.一般公共预算') == '一般公共预算'
    assert parser.strip('2. 政 府 性基金预算') == '政府性基金预算'
    assert parser.strip('二、财政专户管理资金') == '财政专户管理资金'
    assert parser.strip('十七、国土海洋气象等支出') == '国土海洋气象等支出'
    assert parser.strip('13,649.07') == '13,649.07'
    r1, t1 = parser.split_merge_cell('24,458.43二、财政专户管理资金')
    assert r1 is True
    assert t1 == ('24,458.43', '二、财政专户管理资金')
    r2, t2 = parser.split_merge_cell('二、财政专户管理资金')
    assert r2 is False
    assert t2 is None
    assert parser.split_merge_cell('24,458.43十二、财政专户管理资金')[1] == ('24,458.43', '十二、财政专户管理资金')
