import filecmp
import os.path
from unittest import mock

import pytest

from ngenix_demo_task.parser import (
    ParserError, XMLParserError, ZIPParserError, do_task_two, parse_archive,
    parse_xml_file, render_objects_csv, render_vars_csv)

TESTS_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(TESTS_DIR, 'data')


class TestParseXMLFile:
    '''parse_xml_file'''

    def test_ok(self):
        '''возвращает словарь с данными разбора, если xml файл валиден.'''
        path = os.path.join(DATA_DIR, 'good.xml')
        result = {}
        with open(path, 'r') as xml_file:
            result = parse_xml_file(xml_file)
        expected = {
            'vars': [('helloworld', '42'), ],
            'objects': [
                ('helloworld', 'one'),
                ('helloworld', 'two'),
                ('helloworld', 'three')
            ]
        }
        assert result == expected

    @pytest.mark.parametrize('filename, message', [
        ('bad_syntax.xml', 'is corrupted'),
        ('no_var_id.xml', 'no var element of type id'),
        ('multiple_var_id.xml', 'multiple var elements of type id'),
        ('no_var_level.xml', 'no var element of type level'),
        ('multiple_var_level.xml', 'multiple var elements of type level'),
        ('no_objects.xml', 'no elements of type object'),
        ('too_many_objects.xml', 'more than ten elements of type object'),
    ])
    def test_bad_xml(self, filename, message):
        '''возвращает ошибку XMLParserError с соответствующим сообщением, если
        файл не соответствует формату.
        '''
        path = os.path.join(DATA_DIR, filename)
        with pytest.raises(XMLParserError) as excinfo:
            with open(path, 'r') as xml_file:
                parse_xml_file(xml_file)
        assert message in str(excinfo.value)


class TestParseArchive:
    '''parse_archive'''

    def test_ok(self):
        '''возвращает словарь с данными разбора, если zip архив валиден и
        соответствует формату.
        '''
        path = os.path.join(DATA_DIR, 'test.zip')
        result = parse_archive(path)
        expected = {
            'vars': [('helloworld', '42'), ('helloworld', '42')],
            'objects': [
                ('helloworld', 'one'),
                ('helloworld', 'two'),
                ('helloworld', 'three'),
                ('helloworld', 'one'),
                ('helloworld', 'two'),
                ('helloworld', 'three')
            ]
        }
        assert result == expected

    def test_empty(self):
        '''возвращает словарь с данными разбора, если zip пуст.'''
        path = os.path.join(DATA_DIR, 'empty.zip')
        result = parse_archive(path)
        expected = {
            'vars': [],
            'objects': []
        }
        assert result == expected

    @pytest.mark.parametrize('filename', [
        'corrupted.zip',
        'not_only_xml.zip'
    ])
    def test_bad_zip(self, filename):
        '''возвращает ошибку XMLParserError с соответствующим сообщением, если
        файл не соответствует формату.
        '''
        path = os.path.join(DATA_DIR, filename)
        with pytest.raises(ZIPParserError) as excinfo:
            parse_archive(path)
        assert 'is corrupted' in str(excinfo.value)


class TestRenderVarsCSV:
    '''render_vars_csv'''

    def test_ok(self, tmpdir):
        '''сохраняет csv файл с данными, если входные данные корректны.'''
        path = str(tmpdir.mkdir('csv'))
        vars = [('hello', '42'), ('world', '42')]
        render_vars_csv(path, vars)
        test_csv = os.path.join(path, 'vars.csv')
        control = os.path.join(DATA_DIR, 'vars.csv')
        assert filecmp.cmp(test_csv, control)

    @mock.patch('ngenix_demo_task.parser.open')
    def test_system_error(self, open_mock, tmpdir):
        '''возвращает ошибку ParserError, если при записи csv файла возникла
        системная ошибка.
        '''
        open_mock.side_effect = IOError('Test')
        path = str(tmpdir.mkdir('csv'))
        vars = [('hello', '42'), ('world', '42')]
        with pytest.raises(ParserError) as excinfo:
            render_vars_csv(path, vars)
        assert 'Test' in str(excinfo.value)


class TestRenderObjectsCSV:
    '''render_objects_csv'''

    def test_ok(self, tmpdir):
        '''сохраняет csv файл с данными, если входные данные корректны.'''
        path = str(tmpdir.mkdir('csv'))
        objects = [('helloworld', 'one'), ('helloworld', 'two')]
        render_objects_csv(path, objects)
        test_csv = os.path.join(path, 'objects.csv')
        control = os.path.join(DATA_DIR, 'objects.csv')
        assert filecmp.cmp(test_csv, control)

    @mock.patch('ngenix_demo_task.parser.open')
    def test_system_error(self, open_mock, tmpdir):
        '''возвращает ошибку ParserError, если при записи csv файла возникла
        системная ошибка.
        '''
        open_mock.side_effect = IOError('Test')
        path = str(tmpdir.mkdir('csv'))
        objects = [('hello', '42'), ('world', '42')]
        with pytest.raises(ParserError) as excinfo:
            render_objects_csv(path, objects)
        assert 'Test' in str(excinfo.value)


class TestDoTaskTwo:
    '''do_task_two'''

    @mock.patch('ngenix_demo_task.parser.render_vars_csv')
    @mock.patch('ngenix_demo_task.parser.render_objects_csv')
    def test_ok(self, objects_mock, vars_mock):
        '''обрабатывает содержимое папки с zip архивами согласно заданию №2.'''
        path = os.path.join(DATA_DIR, 'good')
        objects_mock.return_value = None
        vars_mock.return_value = None
        do_task_two(path)
        vars = [
            ('helloworld', '42'), ('helloworld', '42'), ('helloworld', '42'),
            ('helloworld', '42')
        ]
        assert vars_mock.call_count == 1
        args, kwargs = vars_mock.call_args
        assert path in args
        assert vars in args
        objects = [
            ('helloworld', 'one'), ('helloworld', 'two'),
            ('helloworld', 'three'), ('helloworld', 'one'),
            ('helloworld', 'two'), ('helloworld', 'three'),
            ('helloworld', 'one'), ('helloworld', 'two'),
            ('helloworld', 'three'), ('helloworld', 'one'),
            ('helloworld', 'two'), ('helloworld', 'three')
        ]
        assert objects_mock.call_count == 1
        args, kwargs = objects_mock.call_args
        assert path in args
        assert objects in args

    def test_empty(self):
        '''вызывает ошибку ParserError, если в папке нет zip файлов.'''
        path = os.path.join(DATA_DIR, 'empty')
        with pytest.raises(ParserError) as excinfo:
            do_task_two(path)
        assert 'No zip files found' in str(excinfo.value)
