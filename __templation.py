#!/usr/bin/env python3

"""
Rather simple templating tool. The template file must follow jinja2 syntax
while the data source is either a file (in json, yaml or shell kv format) or
the environment.

"""

# bugs and hints: lrsklemstein@gmail.com


import argparse
import logging
import logging.config
import os.path
import sys

from typing import Any, Dict  # , List, Tuple, Callable

from jinja2 import Template

__LOG_LEVEL_DEFAULT = logging.INFO


def main() -> None:
    setup = get_prog_setup_or_exit_with_usage()

    init_logging(setup)
    logger = logging.getLogger(__name__)

    try:
        sys.exit(run(setup))
    except Exception:
        logger.critical("Abort, rc=3", exc_info=True)
        sys.exit(3)


def get_prog_setup_or_exit_with_usage() -> Dict[str, Any]:
    prog = os.path.basename(sys.argv[0])

    if prog.startswith('__'):
        prog = prog[2:]
        prog = os.path.splitext(prog)[0]

    parser = argparse.ArgumentParser(
                description=get_prog_doc(), prog=prog,
                formatter_class=argparse.RawTextHelpFormatter,
            )

    log_group = parser.add_mutually_exclusive_group()

    parser.add_argument(
        'TEMPLATE', help='the template file using jinja2 syntax',
    )

    parser.add_argument(
        'DATA', nargs='?',
        help='the data file using json, yaml or shell env format',
    )

    parser.add_argument(
        '--outfile', help='write rendered output to (default: stdout)',
    )

    parser.add_argument(
        '--lazy', action='store_true', help='ignore undefined values',
    )

    log_group.add_argument(
        '--debug', action='store_true',
        help='enable debug log level',
    )

    log_group.add_argument(
        '--log_cfg', dest='log_cfg',
        help='optional logging cfg in ini format',
    )

    args = vars(parser.parse_args())
    args = {k: '' if v is None else v for k, v in args.items()}

    return args


def get_prog_doc() -> str:
    doc_str = sys.modules['__main__'].__doc__

    if doc_str is not None:
        return doc_str.strip()
    else:
        return '<???>'


def init_logging(setup: Dict[str, Any]) -> None:
    """Creates either a logger by cfg file or a default instance
    with given log level by arg --log_level (otherwise irgnored)

    """
    if setup['log_cfg'] == '':
        if setup['debug']:
            level = logging.DEBUG
            format = '%(levelname)s - %(message)s'
        else:
            level = __LOG_LEVEL_DEFAULT
            format = '%(message)s'

        logging.basicConfig(level=level, format=format)
    else:
        logging.config.fileConfig(setup['log_cfg'])


def run(setup: Dict[str, Any]) -> int:
    logger = logging.getLogger(__name__)

    template = get_template(setup)
    logger.debug('Got template...')

    data = get_data(setup)
    logger.debug('Got data...')

    rendered = get_rendered_text(setup)
    logger.debug('Rendered...')

    output_result(rendered)

    return 0


def get_template(setup: Dict[str, Any]) -> str:
    with open(setup['TEMPLATE']) as f:
        template = f.read()

    return template


def get_data(setup: Dict[str, Any]) -> Dict[str, Any]:
    if not setup['DATA']:
        return dict(os.environ)

    with open(setup['DATA']) as f:
        if any(setup['DATA'].endswith(ext) for ext in ('.yaml', 'yml')):
            import yaml

            data = yaml.safe_load(f)
        elif setup['DATA'].endswith('.json'):
            import json

            data = json.loadf(f)
        else:
            from dotenv import dotenv_values

            data = dotenv_values(setup['DATA'])

    return data


def get_rendered_text(setup: Dict[str, Any],
        template: str, data: Dict[str, Any]) -> str:
    if setup['lazy']:
        return Template(template).render(**data)
    else:
        return Template(template,
                undefined=jinja2.StrictUndefined).render(**data)


def output_result(setup: Dict[str, Any], rendered: str) -> None:
    if setup['outfile']:
        with open(setup['outfile'], 'wt') as f:
            print(rendered, file=f)
    else:
        print(rendered)


if __name__ == '__main__':
    main()
