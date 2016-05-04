import os.path
from unittest import mock
from zipfile import ZipFile

import pytest

from ngenix_demo_task.generator import (
    GeneratorError, XMLGeneratorError, do_task_one, generate_data,
    generate_zip, render_xml)

TESTS_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(TESTS_DIR, "data")


class TestGenerateData:
    '''generate_data'''

    def test_ok(self):
        '''возвращает произвольный набор данных для заполнения xml документа.
        '''
        result_a = generate_data()
        id, level, objects = result_a
        assert isinstance(id, str)
        assert isinstance(level, int)
        assert 1 <= level <= 100
        assert isinstance(objects, tuple)
        assert 1 <= len(objects) <= 10
        result_b = generate_data()
        assert result_a != result_b


class TestRenderXML:
    '''render_xml'''

    @pytest.fixture
    def data(self):
        '''Фикстура данных для генерации контрольного xml документа.'''
        objects = [
            "one",
            "two",
            "three"
        ]
        return ("helloworld", 42, objects)

    @pytest.fixture
    def document(self):
        '''Фикстура контрольного xml документа.'''
        document = (
            '<root><var name="id" value="helloworld"/>'
            '<var name="level" value="42"/><objects><object name="one"/>'
            '<object name="two"/><object name="three"/></objects></root>'
        )
        return document

    def test_ok(self, data, document):
        '''генерирует содержимое xml документа согласно переданным аргументам.
        '''
        render = render_xml(*data)
        assert render == document

    def test_empty_objects(self, data, document):
        '''возвращает ошибку ValueError в случае, если в качестве параметра
        objects передан пустой итерируемый объект.
        '''
        data = ("helloworld", 42, [])
        with pytest.raises(XMLGeneratorError) as excinfo:
            render_xml(*data)
        assert str(excinfo.value) == 'Document must have at least one object'


class TestGenerateZIP:
    '''generate_zip'''

    @pytest.fixture
    def data(self):
        '''Фикстура данных для генерации контрольного xml документа.'''
        objects = [
            "one",
            "two",
            "three"
        ]
        return ("helloworld", 42, objects)

    @pytest.fixture
    def document(self):
        '''Фикстура контрольного xml документа.'''
        document = (
            '<root><var name="id" value="helloworld"/>'
            '<var name="level" value="42"/><objects><object name="one"/>'
            '<object name="two"/><object name="three"/></objects></root>'
        )
        return document

    @mock.patch("ngenix_demo_task.generator.generate_data")
    def test_ok(self, data_mock, tmpdir, data, document):
        '''генерирует валидный zip архив с данными полученными из
        generate_data.
        '''
        data_mock.return_value = data
        path = str(tmpdir.mkdir('archives').join('test.zip'))
        generate_zip(path, xml_documents_quantity=2)
        control = os.path.join(DATA_DIR, 'test.zip')
        test_info, control_info = [], []
        with ZipFile(path, 'r') as test_zip:
            test_info = test_zip.infolist()
        with ZipFile(control, 'r') as control_zip:
            control_info = control_zip.infolist()
        for info_a, info_b in zip(test_info, control_info):
            assert info_a.CRC == info_b.CRC

    @mock.patch("ngenix_demo_task.generator.ZipFile")
    def test_system_error(self, zip_mock, tmpdir):
        '''возвращает ошибку GeneratorError, если при записи zip файла возникла
        системная ошибка.
        '''
        zip_mock.side_effect = IOError("Test")
        path = str(tmpdir.mkdir('archives').join('test.zip'))
        with pytest.raises(GeneratorError) as excinfo:
            generate_zip(path, xml_documents_quantity=2)
        assert 'Test' in str(excinfo.value)


class TestDoTaskOne:
    '''do_task_one'''

    @mock.patch("ngenix_demo_task.generator.generate_zip")
    def test_ok(self, zip_mock, tmpdir):
        '''вызывает generate_zip для генерации zip архивов в указанной локации.
        '''
        zip_mock.return_value = None
        path = str(tmpdir.mkdir('archives'))
        do_task_one(path, quantity=50)
        assert zip_mock.call_count == 50
        args, kwargs = zip_mock.call_args
        assert path in args[0]
        assert 'zip' in args[0]
