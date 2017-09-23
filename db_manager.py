#!/usr/bin/env python3.6

import argparse
import logging
import sys

import colorlog

from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable
from bunnylol.database import Base

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
ch.setFormatter(formatter)
logger.addHandler(ch)


def parse_args():
    parser = argparse.ArgumentParser(usage='Create bunnylol database')
    parser.set_defaults(cmd=lambda _: parser.print_help())
    parser.add_argument(
        '--dialect',
        default='sqlite',
        help=(
            'DB dialect (one of sqlite, postgresql, mysql), '
            'default: %(default)s'
        ),
    )
    parser.add_argument('--user')
    parser.add_argument('--password')
    parser.add_argument('--host')
    parser.add_argument('--port')
    subparsers = parser.add_subparsers()

    db_parent = argparse.ArgumentParser(add_help=False)
    db_parent.add_argument(
        'database',
        help='Database name e.g for sqlite, bunnylol.db',
    )
    db_parent.add_argument(
        '--sql',
        help='Show SQL statements to be executed',
    )

    list_parser = subparsers.add_parser(
        'list',
        help='List tables needed in the application',
    )
    list_parser.set_defaults(cmd=cmd_list)
    list_parser.add_argument(
        '--sql',
        action='store_true',
        help='Show SQL statements to create tables',
    )

    create_parser = subparsers.add_parser(
        'create',
        parents=[db_parent],
        help='Create database',
    )
    create_parser.set_defaults(cmd=cmd_create)

    check_parser = subparsers.add_parser(
        'check',
        parents=[db_parent],
        help='Check database schema',
    )
    check_parser.set_defaults(cmd=cmd_check)

    migrate_parser = subparsers.add_parser(
        'migrate',
        parents=[db_parent],
        help='Migrate database schema',
    )
    migrate_parser.set_defaults(cmd=cmd_migrate)

    return parser.parse_args()


def get_engine(url):
    engine = create_engine(url)
    with engine.connect() as conn:
        conn


def cmd_list(args):
    for table in Base.metadata.sorted_tables:
        if args.sql and args.dialect:
            print(CreateTable(table))
        else:
            print(table.name)


def cmd_create(args):
    logger.info('Create')

    # TODO: format db url
    engine = get_engine()
    Base.metadata.create_all(engine)


def cmd_check(args):
    logger.info('Check')


def cmd_migrate(args):
    raise NotImplemented


if __name__ == '__main__':
    args = parse_args()
    if hasattr(args, 'cmd'):
        sys.exit(args.cmd(args))
