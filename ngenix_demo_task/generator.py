import os.path
from datetime import datetime
from random import randint
from uuid import uuid4
from zipfile import ZipFile

from lxml import etree


class GeneratorError(Exception):
    '''Ошибка работы генератора.'''
    pass


class XMLGeneratorError(GeneratorError):
    '''Ошибка работы генератора XML.'''
    pass


def generate_data():
    '''Сгенерировать набор данных для заполения xml документа.

    :returns: tuple с набором данных.

    '''
    id = uuid4().hex
    level = randint(1, 100)
    objects = tuple(uuid4().hex for _ in range(randint(1, 10)))
    return id, level, objects


def render_xml(id, level, objects):
    '''Сгенерировать содержимое xml документа по набору данных.

    Документ должен иметь содержимое вида:
    <root>
        <var name=’id’ value={id}/>
        <var name=’level’ value={level}/>
        <objects>
            <object name={object}/>
            <object name={object}/>
            ...
        </objects>
    </root>

    :param id: значение параметра id подставляемого в документ.
    :param level: значение параметра level подставляемого в документ.
    :param objects: iterable наименований объектов подставляемых в документ.

    '''
    if not objects:
        raise XMLGeneratorError('Document must have at least one object')
    xroot = etree.Element('root')
    # var элемент id
    xvar = etree.SubElement(xroot, 'var')
    xvar.attrib['name'] = 'id'
    xvar.attrib['value'] = str(id)
    # var элемент level
    xvar = etree.SubElement(xroot, 'var')
    xvar.attrib['name'] = 'level'
    xvar.attrib['value'] = str(level)
    # Коллекция элементов objects
    xobjects = etree.SubElement(xroot, 'objects')
    for item in objects:
        xobject = etree.SubElement(xobjects, 'object')
        xobject.attrib['name'] = str(item)
    return etree.tostring(xroot, encoding='unicode')


def generate_zip(path, xml_documents_quantity=100):
    '''Сгенерировать zip архив с xml документами.

    :param str path: путь до генерируемого архива.
    :param int xml_documents_quantity: количество xml документов в генерируемом
                                       архиве.
    '''
    try:
        with ZipFile(path, 'w') as archive:
            for xml_number in range(xml_documents_quantity):
                xml_filename = '{}.xml'.format(xml_number)
                content = render_xml(*generate_data())
                archive.writestr(xml_filename, content)
    except IOError as error:
        raise GeneratorError(str(error))


def do_task_one(path, quantity=50):
    '''Сгенерировать набор zip архивов согласно задания №1.

    :param str path: путь до папки в которой нужно сохранить архивы.
    :param int quantity: количество генерируемых архивов.
    '''
    for archive_number in range(quantity):
        timestamp = datetime.utcnow().isoformat()
        archive_name = '{}_{}.zip'.format(archive_number, timestamp)
        zip_path = os.path.join(path, archive_name)
        generate_zip(zip_path)
