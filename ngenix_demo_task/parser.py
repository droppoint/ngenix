import csv
import multiprocessing as mp
import os
from zipfile import BadZipFile, ZipFile

from lxml import etree


class ParserError(Exception):
    '''Ошибка работы парсера.'''
    pass


class ZIPParserError(ParserError):
    '''Ошибка работы парсера zip файлов.'''
    pass


class XMLParserError(ParserError):
    '''Ошибка работы парсера XML.'''
    pass


def parse_xml_file(xml_file):
    '''Получить значения id, level элементов var и name элементов object из
    xml файла.

    :param file xml_file: file-like объект.

    :returns: dict c результатами разбора xml файла.
    :raises: XMLParserError.
    '''
    result = {
        "vars": [],
        "objects": []
    }
    try:
        tree = etree.parse(xml_file)
    except etree.XMLSyntaxError:
        raise XMLParserError("XML file {} is corrupted".format(xml_file.name))
    var_id_list = tree.xpath('/root/var[@name="id"]')
    if len(var_id_list) == 0:
        raise XMLParserError("XML document has no var element of type id")
    if len(var_id_list) > 1:
        message = "XML document has multiple var elements of type id"
        raise XMLParserError(message)
    var_level_list = tree.xpath('/root/var[@name="level"]')
    if len(var_level_list) == 0:
        raise XMLParserError("XML document has no var element of type level")
    if len(var_level_list) > 1:
        message = "XML document has multiple var elements of type level"
        raise XMLParserError(message)
    var_id, var_level = var_id_list[0], var_level_list[0]
    id, level = var_id.attrib["value"], var_level.attrib["value"]
    result["vars"].append((id, level))
    xobjects = tree.xpath('/root/objects/object')
    if len(xobjects) == 0:
        message = "XML document has no elements of type object"
        raise XMLParserError(message)
    if len(xobjects) > 10:
        message = "XML document has more than ten elements of type object"
        raise XMLParserError(message)
    for xobject in xobjects:
        name = xobject.attrib["name"]
        result["objects"].append((id, name))
    return result


def parse_archive(path):
    '''Обработать содержимое zip архива согласно заданию №2.

    :param str path: путь до zip архива.
    :raises: ZIPParserError.
    '''
    result = {
        "vars": [],
        "objects": []
    }
    try:
        with ZipFile(path, 'r') as archive:
            files = archive.namelist()
            for file in files:
                assert '.xml' in file, 'archive must contain only xml files'
                with archive.open(file, "r") as xml_file:
                    diff = parse_xml_file(xml_file)
                    result['vars'] += diff['vars']
                    result['objects'] += diff['objects']
    except (BadZipFile, AssertionError):
        raise ZIPParserError("ZIP file {} is corrupted".format(path))
    return result


def render_vars_csv(path, vars):
    '''Сохранить информацию об элементах var в csv файл.

    :param str path: путь до папки в которую нужно сохранить CSV файл.
    :param list vars: массив с данными элементов var.

    '''
    try:
        vars_path = os.path.join(path, "vars.csv")
        with open(vars_path, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(("id", "level"))
            for line in vars:
                csvwriter.writerow(line)
    except IOError as error:
        raise ParserError(str(error))


def render_objects_csv(path, objects):
    '''Сохранить информацию об элементах object в csv файл.

    :param str path: путь до папки в которую нужно сохранить CSV файл.
    :param list objects: массив с данными элементов object.

    '''
    try:
        objects_path = os.path.join(path, "objects.csv")
        with open(objects_path, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(("id", "object_name"))
            for line in objects:
                csvwriter.writerow(line)
    except IOError as error:
        raise ParserError(str(error))


def do_task_two(path):
    '''Обработать содержимое папки с zip архивами согласно заданию №2.

    :param str path: путь до папки с архивами.

    :raises: ParserError.
    '''
    archive_paths = []
    for filename in os.listdir(path):
        if filename.endswith(".zip"):
            archive_paths.append(os.path.join(path, filename))
    if len(archive_paths) == 0:
        raise ParserError('No zip files found in folder {}'.format(path))
    results = []
    with mp.Pool() as pool:
        results = pool.map(parse_archive, archive_paths)
    vars = []
    objects = []
    for result in results:
        vars += result['vars']
        objects += result['objects']
    render_vars_csv(path, vars)
    render_objects_csv(path, objects)
