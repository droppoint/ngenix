import os
from unittest import mock

import pytest
from click.testing import CliRunner

from ngenix_demo_task.cli import main
from ngenix_demo_task.generator import GeneratorError
from ngenix_demo_task.parser import ParserError


class TestCLI:
    '''Интерфейс командной строки.'''

    @pytest.fixture
    def runner(self, request):
        '''Фикстура лаунчера консольных команд в изолированном окружении.'''
        return CliRunner()

    @mock.patch('ngenix_demo_task.cli.do_task_one')
    def test_generate(self, task_one_mock, runner):
        '''generate вызывает do_task_one с текущей папкой по умолчанию, если не
        было предоставлено аргументов.
        '''
        task_one_mock.return_value = None
        result = runner.invoke(main, ['generate', ])
        assert result.exit_code == 0
        assert task_one_mock.call_count == 1
        args, kwargs = task_one_mock.call_args
        assert os.getcwd() in args

    @mock.patch('ngenix_demo_task.cli.do_task_one')
    def test_generate_with_folder(self, task_one_mock, runner):
        '''generate вызывает do_task_one с папкой переданной из аргумента
        команды.
        '''
        task_one_mock.return_value = None
        result = runner.invoke(main, ['generate', '-o', '/tmp'])
        assert result.exit_code == 0
        assert task_one_mock.call_count == 1
        args, kwargs = task_one_mock.call_args
        assert '/tmp' in args

    @mock.patch('ngenix_demo_task.cli.do_task_one')
    def test_generate_fail(self, task_one_mock, runner):
        '''generate завершается с ошибкой, если ошибка произошла в do_task_one.
        '''
        task_one_mock.side_effect = GeneratorError('Test')
        result = runner.invoke(main, ['generate', ])
        assert result.exit_code == 1
        assert "Error" in result.output

    @mock.patch('ngenix_demo_task.cli.do_task_two')
    def test_parse(self, task_two_mock, runner):
        '''parse вызывает do_task_two с текущей папкой по умолчанию, если не
        было предоставлено аргументов.
        '''
        task_two_mock.return_value = None
        result = runner.invoke(main, ['parse', ])
        assert result.exit_code == 0
        assert task_two_mock.call_count == 1
        args, kwargs = task_two_mock.call_args
        assert os.getcwd() in args

    @mock.patch('ngenix_demo_task.cli.do_task_two')
    def test_parse_with_folder(self, task_two_mock, runner):
        '''parse вызывает do_task_two с папкой переданной из аргумента
        команды.
        '''
        task_two_mock.return_value = None
        result = runner.invoke(main, ['parse', '-o', '/tmp'])
        assert result.exit_code == 0
        assert task_two_mock.call_count == 1
        args, kwargs = task_two_mock.call_args
        assert '/tmp' in args

    @mock.patch('ngenix_demo_task.cli.do_task_one')
    def test_parse_fail(self, task_one_mock, runner):
        '''parse завершается с ошибкой, если ошибка произошла в do_task_two.
        '''
        task_one_mock.side_effect = ParserError('Test')
        result = runner.invoke(main, ['parse', ])
        assert result.exit_code == 1
        assert "Error" in result.output

    @mock.patch('ngenix_demo_task.cli.do_task_two')
    @mock.patch('ngenix_demo_task.cli.do_task_one')
    def test_cycle(self, task_one_mock, task_two_mock, runner):
        '''cycle вызывает do_task_two с текущей папкой по умолчанию, если не
        было предоставлено аргументов.
        '''
        task_one_mock.return_value = None
        task_two_mock.return_value = None
        result = runner.invoke(main, ['cycle', ])
        assert result.exit_code == 0
        assert task_one_mock.call_count == 1
        args, kwargs = task_one_mock.call_args
        assert os.getcwd() in args
        assert task_two_mock.call_count == 1
        args, kwargs = task_two_mock.call_args
        assert os.getcwd() in args

    @mock.patch('ngenix_demo_task.cli.do_task_two')
    @mock.patch('ngenix_demo_task.cli.do_task_one')
    def test_cycle_with_folder(self, task_one_mock, task_two_mock, runner):
        '''cycle вызывает do_task_two с папкой переданной из аргумента
        команды.
        '''
        task_one_mock.return_value = None
        task_two_mock.return_value = None
        result = runner.invoke(main, ['cycle', '-o', '/tmp'])
        assert result.exit_code == 0
        assert task_one_mock.call_count == 1
        args, kwargs = task_one_mock.call_args
        assert '/tmp' in args
        assert task_two_mock.call_count == 1
        args, kwargs = task_two_mock.call_args
        assert '/tmp' in args

    @mock.patch('ngenix_demo_task.cli.do_task_two')
    @mock.patch('ngenix_demo_task.cli.do_task_one')
    def test_cycle_fail(self, task_one_mock, task_two_mock, runner):
        '''cycle вызывает do_task_two с папкой переданной из аргумента
        команды.
        '''
        task_one_mock.side_effect = GeneratorError('Test')
        result = runner.invoke(main, ['cycle', ])
        assert result.exit_code == 1
        assert "Error" in result.output
