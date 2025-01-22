#!/usr/bin/env python3

"""
Simple templating tool

"""

# bugs and hints: lrsklemstein@gmail.com

import argparse
import logging
import logging.config
import sys

from typing import Any, Dict  # , List, Tuple, Callable

from jinja2 import Template
import yaml

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
    parser = argparse.ArgumentParser(
                description=get_prog_doc(),
                formatter_class=argparse.RawTextHelpFormatter,
            )

    log_group = parser.add_mutually_exclusive_group()

    parser.add_argument(
        'TEMPLATE', help='the template file using jinja2 syntax',
    )

    parser.add_argument(
        'DATA', help='the data file using yaml syntax',
    )

    parser.add_argument(
        '--outfile', help='write rendered output to (default: stdout)',
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

    with open(setup['TEMPLATE']) as f:
        template = f.read()

    with open(setup['DATA']) as f:
        data = yaml.safe_load(f)

    rendered = Template(template).render(**data)

    if setup['outfile']:
        with open(setup['outfile'], 'wt') as f:
            print(rendered, file=f)
    else:
        print(rendered)

    return 0


if __name__ == '__main__':
    main()
