#!/usr/bin/env python

from pathlib import Path
from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter

from chris_plugin import chris_plugin, PathMapper
import pypx
import json

__version__ = '1.0.0'

DISPLAY_TITLE = r"""
       _                                 _       _                                   
      | |                               | |     | |                                  
 _ __ | |______ _ __   __ _  ___ ___  __| | __ _| |_ ___  __ _ _   _  ___ _ __ _   _ 
| '_ \| |______| '_ \ / _` |/ __/ __|/ _` |/ _` | __/ _ \/ _` | | | |/ _ \ '__| | | |
| |_) | |      | |_) | (_| | (__\__ \ (_| | (_| | ||  __/ (_| | |_| |  __/ |  | |_| |
| .__/|_|      | .__/ \__,_|\___|___/\__,_|\__,_|\__\___|\__, |\__,_|\___|_|   \__, |
| |            | |                                          | |                 __/ |
|_|            |_|                                          |_|                |___/ 
"""


parser = ArgumentParser(description= '''
    A ChRIS plugin that connects to a PACS and saves the results
    of queries.
''', formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('-p', '--pattern', default='**/*.txt', type=str,
                    help='input file filter glob')
parser.add_argument('-V', '--version', action='version',
                    version=f'%(prog)s {__version__}')


def date_get(inputfile: str) -> str:
    file_name = str(inputfile).strip('/')[-1]
    date = str(file_name).split('.')[0]
    raw_date = str(date).replace('-','')
    return str(raw_date)

# The main function of this *ChRIS* plugin is denoted by this ``@chris_plugin`` "decorator."
# Some metadata about the plugin is specified here. There is more metadata specified in setup.py.
#
# documentation: https://fnndsc.github.io/chris_plugin/chris_plugin.html#chris_plugin
@chris_plugin(
    parser=parser,
    title='A ChRIS PACS Query Plugin',
    category='',                 # ref. https://chrisstore.co/plugins
    min_memory_limit='100Mi',    # supported units: Mi, Gi
    min_cpu_limit='1000m',       # millicores, e.g. "1000m" = 1 CPU core
    min_gpu_limit=0              # set min_gpu_limit=1 to enable GPU
)
def main(options: Namespace, inputdir: Path, outputdir: Path):
    """
    *ChRIS* plugins usually have two positional arguments: an **input directory** containing
    input files and an **output directory** where to write output files. Command-line arguments
    are passed to this main method implicitly when ``main()`` is called below without parameters.

    :param options: non-positional arguments parsed by the parser given to @chris_plugin
    :param inputdir: directory containing (read-only) input files
    :param outputdir: directory where to write output files
    """

    print(DISPLAY_TITLE)

    # Typically it's easier to think of programs as operating on individual files
    # rather than directories. The helper functions provided by a ``PathMapper``
    # object make it easy to discover input files and write to output files inside
    # the given paths.
    #
    # Refer to the documentation for more options, examples, and advanced uses e.g.
    # adding a progress bar and parallelism.
    mapper = PathMapper.file_mapper(inputdir, outputdir, glob=options.pattern, suffix='.json')
    for input_file, output_file in mapper:
        # The code block below is a small and easy example of how to use a ``PathMapper``.
        # It is recommended that you put your functionality in a helper function, so that
        # it is more legible and can be unit tested.
        date = date_get(str(input_file))

        pacs_settings = {
            'executable': '/usr/bin/findscu',
            'aec': 'ORTHANC',
            'aet': 'CHIPS',
            'serverIP': '127.0.0.1',
            'serverPort': '4242',
        }

        # query parameters
        query_settings = {
            'StudyDate': date
        }

        # output parameters
        output_settings = {
            'printReport': 'json',
            'colorize': 'dark'
        }

        # python 3.5 ** syntax
        results = pypx.find({
            **pacs_settings,
            **query_settings,
            **output_settings})
        results_json = json.dumps(results, indent=4)

        output_file.write_text(results_json)


if __name__ == '__main__':
    main()
