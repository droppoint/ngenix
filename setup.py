'''
ngenix-demo-task
----------------

Реализация тестового задания для компании Ngenix.

'''
from setuptools import find_packages, setup

install_requires = [
    'click==6.6',
    'lxml==3.6.0',
]


setup(
    name='ngenix-demo-task',
    version='1.0.0',

    description='Реализация тестового задания для компании Ngenix',
    long_description=__doc__,

    url='https://github.com/droppoint/ngenix-demo-task',

    author='Alexei Partilov',
    author_email='partilov@gmail.com',

    entry_points={
        'console_scripts': [
            'ndt = ngenix_demo_task.cli:main',
        ]
    },

    classifiers=[
        'Programming Language :: Python :: 3.4',
        'Environment :: Console',
        'Private :: Do Not Upload'
    ],

    keywords='Ngenix',
    packages=find_packages(exclude=('tests', 'tests.*')),

    install_requires=install_requires
)
