import os

import click
from click.exceptions import ClickException

from ngenix_demo_task.generator import GeneratorError, do_task_one
from ngenix_demo_task.parser import ParserError, do_task_two


@click.group()
@click.help_option(
    help='Отобразить эту справочную информацию и завершить работу'
)
def main(**kwargs):
    '''Тестовое задание для компании Ngenix.'''
    pass


@main.command()
@click.option('-o', '--output', default=os.getcwd(),
              help='Папка для создания файлов (По умолчанию: текущая папка')
def generate(**kwargs):
    '''Сгенерировать набор zip архивов.'''
    try:
        do_task_one(kwargs['output'])
    except GeneratorError as error:
        raise ClickException(error)


@main.command()
@click.option('-o', '--output', default=os.getcwd(),
              help='Папка для чтения и создания файлов (По умолчанию:'
                   'текущая папка')
def parse(**kwargs):
    '''Сгенерировать csv файлы из zip архивов.'''
    try:
        do_task_two(kwargs['output'])
    except ParserError as error:
        raise ClickException(error)


@main.command()
@click.option('-o', '--output', default=os.getcwd(),
              help='Папка для чтения и создания файлов (По умолчанию:'
                   'текущая папка')
def cycle(**kwargs):
    '''Сгенерировать zip архивы и csv файлы.'''
    try:
        do_task_one(kwargs['output'])
        do_task_two(kwargs['output'])
    except (GeneratorError, ParserError) as error:
        raise ClickException(error)
