from __future__ import annotations
import argparse
from dataclasses import dataclass
import os
import sys

from .core.meta import MetaDirectory, MetaUtil
from .core.error import CLIError

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog='jpdict')
    subparsers = parser.add_subparsers(dest='command')

    # Init Command
    initCmd = subparsers.add_parser(
        'init',
        help="""
        In order to start working with the CLI, we need to initialize
        the directory where metadata will be stored.
        This will create a .jpdict directory under your current working directory.
        """
    )
    initCmd.add_argument(
        '--global',
        action='store_true',
        default=False,
        help="""
        For initializing a global .jpdict directory, use this parameter.
        When looking for .jpdict, if a .jpdict directory cannot be found in your
        current working directory, jpdict will look for a global .jpdict directory
        under your home directory instead. Using a global .jpdict directory would
        make it so that you can execute jpdict commands from any directory.
        Note that a local .jpdict will take precedence over a global .jpdict.
        """
    )

    # History Command
    historyCmd = subparsers.add_parser(
        'history',
        help="""
        Browser history is the starting point of our workflow.
        Use the history command for working with browser history.
        """
    )
    historySubparsers = historyCmd.add_subparsers(dest='subcommand')
    historySourceCmd = historySubparsers.add_parser(
        'source',
        help="Get/set the source directory where all of your browser histories are saved."
    )
    historySourceCmd.add_argument(
        '--update',
        type=str,
        default=None,
        help="Update the source history directory where all of your browser histories are saved."
    )
    historyListCmd = historySubparsers.add_parser(
        'list',
        help='List all of the history paths under your history directory.'
    )
    historyCountPathsCmd = historySubparsers.add_parser(
        'count-paths',
        help='Count the number of history paths under your history directory.'
    )
    historyCombineCmd = historySubparsers.add_parser(
        'combine',
        help='Combine all of the histories contained in your history directory.'
    )

    def entries_get_arg(cmd: argparse.ArgumentParser):
        cmd.add_argument(
            '--get',
            type=str,
            default=None,
            action="append",
            help="""
            Get function of type Callable[[dict], bool] for getting specific history entries.
            Must adhere to lambda function format.
            """
        )
    def entries_value_arg(cmd: argparse.ArgumentParser):
        cmd.add_argument(
            '--value',
            type=str,
            default=None,
            help="""
            Function for getting a specific value within a history entry.
            Must adhere to lambda function format.
            """
        )
    def entries_sort_arg(cmd: argparse.ArgumentParser):
        cmd.add_argument(
            '--sort',
            type=str,
            default=None,
            help="""
            Function for sorting the history entries.
            Must adhere to lambda function format.
            """
        )
    def entries_reverse_arg(cmd: argparse.ArgumentParser):
        cmd.add_argument(
            '--reverse',
            action='store_true',
            default=False,
            help="When sorting, using this option reverses the order of the history entries."
        )
    def entries_head_arg(cmd: argparse.ArgumentParser):
        cmd.add_argument(
            '--head',
            type=int,
            default=None,
            help="For getting the first N history entries."
        )
    def entries_tail_arg(cmd: argparse.ArgumentParser):
        cmd.add_argument(
            '--tail',
            type=int,
            default=None,
            help="For getting the last N history entries."
        )

    historyCountEntriesCmd = historySubparsers.add_parser(
        'count-entries',
        help="Count the number of entries in your combined history."
    )
    entries_get_arg(historyCountEntriesCmd)
    historyPrintEntriesCmd = historySubparsers.add_parser(
        'print-entries',
        help="Tool used for viewing the contents of the combined history."
    )
    entries_value_arg(historyPrintEntriesCmd)
    entries_get_arg(historyPrintEntriesCmd)
    entries_sort_arg(historyPrintEntriesCmd)
    entries_reverse_arg(historyPrintEntriesCmd)
    entries_head_arg(historyPrintEntriesCmd)
    entries_tail_arg(historyPrintEntriesCmd)

    return parser.parse_args()

def main():
    args = parse_args()
    try:
        if args.command == 'init':
            globalFlag: bool = getattr(args, 'global')
            metaDirPath = MetaUtil.get_global_meta_dir() \
                if globalFlag else MetaUtil.get_local_meta_dir()
            if os.path.isdir(metaDirPath):
                raise CLIError('.jpdict is already initialized')
            MetaUtil.init_meta_dir(globalFlag)
            print("Initialized .jpdict directory.")
        elif args.command == 'history':
            metaDir = MetaDirectory.load()
            if args.subcommand == 'source':
                if args.update is not None:
                    metaDir.history.set_loadHistoryDir_cmd(args.update)
                else:
                    metaDir.history.get_loadHistoryDir_cmd()
            elif args.subcommand == 'list':
                metaDir.history.list_history_paths_cmd()
            elif args.subcommand == 'count-paths':
                metaDir.history.count_history_paths_cmd()
            elif args.subcommand == 'combine':
                metaDir.history.combine_history_cmd()
            elif args.subcommand == 'count-entries':
                metaDir.history.count_entries_cmd(getFn=args.get)
            elif args.subcommand == 'print-entries':
                metaDir.history.print_entries_cmd(
                    valueFn=args.value, getFn=args.get,
                    sortFn=args.sort, reverse=args.reverse,
                    head=args.head, tail=args.tail
                )
            else:
                raise NotImplementedError(f'{args.subcommand=}')
        else:
            raise NotImplementedError
    except CLIError as e:
        print(e)

if __name__ == '__main__':
    sys.exit(main())