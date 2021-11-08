"""

The main module of CodART

-changelog
-- Add C++ backend support

"""

__version__ = '0.2.0'
__author__ = 'Morteza'

import os
import shutil
import argparse
from antlr4 import *
from antlr4.TokenStreamRewriter import TokenStreamRewriter

from gen.javaLabeled.JavaLexer import JavaLexer
from gen.javaLabeled.JavaParserLabeled import JavaParserLabeled
from refactorings.pull_field import PullFieldRefactoringInsertListener, PullFieldRefactoringRemoveListener
from refactorings.pull_method import PullMethodRefactoringRemoveListener, PullMethodRefactoringInsertListener
from refactorings.remove_method import RemoveMethodRefactoringListener
from refactorings.rename_package import RenamePackageRefactoringListener


def main(args):
    # Step 0: Find all java files in project Directory
    input_project_folder_name = args.indir.split('\\')[-1]
    output_project_folder_name = args.outdir.split('\\')[-1]

    if os.path.exists(args.outdir):
        shutil.rmtree(args.outdir)

    input_files = []
    output_files = []
    for root, dirs, files in os.walk(args.indir, topdown=True):
        out_root = root.replace(input_project_folder_name, output_project_folder_name)
        os.mkdir(out_root)

        for name in files:
            source = os.path.join(root, name)
            destination = os.path.join(out_root, name)
            shutil.copy(source, destination)

            tokens = name.split('.')
            if 1 < len(tokens) and 'java' == tokens[1]:
                input_files.append(source)
                output_files.append(destination)

    # Initialize streams and parsers for all java files in directory
    stream = []
    lexer = []
    token_stream_rewriter = []
    parse_tree = []
    for index in range(0, len(input_files)):
        # Step 1: Load input source into stream
        stream.append(FileStream(input_files[index], encoding='utf8'))
        # input_stream = StdinStream()

        # Step 2: Create an instance of AssignmentStLexer
        lexer.append(JavaLexer(stream[index]))

        # Step 3: Convert the input source into a list of tokens
        token_stream = CommonTokenStream(lexer[index])
        token_stream_rewriter.append(TokenStreamRewriter(token_stream))

        # Step 4: Create an instance of the AssignmentStParser
        parser = JavaParserLabeled(token_stream)
        # parser.getTokenStream()

        # Step 5: Create parse tree
        # 1. Python backend --> Low speed
        parse_tree.append(parser.compilationUnit())

        # 2. C++ backend --> high speed
        # parse_tree.append(parser.parse(stream, 'compilationUnit', None))

    # Read refactoring type from args
    # pull method refactoring
    if 'pull' in args.type and 'method' in args.type:
        # Read pull direction from args and convert it to boolean (True assigned to up direction and vice versa)
        direction = True
        if 'down' in args.type:
            direction = False

        # Step 6: Walk through the parse tree and refactor codes
        walker = ParseTreeWalker()

        code = None
        # First Iterate trough the directory (Find and remove codes)
        for index in range(0, len(input_files)):
            remove_listener = PullMethodRefactoringRemoveListener(
                common_token_stream_rewriter=token_stream_rewriter[index],
                parent_class_identifier=args.parent,
                child_class_identifier=args.child,
                method_identifier=args.method,
                pull_direction=direction)

            walker.walk(t=parse_tree[index], listener=remove_listener)

            if code is None and remove_listener.method_code is not None:
                code = remove_listener.method_code

        # Second Iterate trough the directory (Insert codes)
        for index in range(0, len(input_files)):
            insert_listener = PullMethodRefactoringInsertListener(
                common_token_stream_rewriter=token_stream_rewriter[index],
                parent_class_identifier=args.parent,
                child_class_identifier=args.child,
                method_identifier=args.method,
                method_code=code,
                pull_direction=direction)
            walker.walk(t=parse_tree[index], listener=insert_listener)

            # Step 7: Write refactored codes on output files
            with open(output_files[index], mode='w', newline='') as file:
                file.write(token_stream_rewriter[index].getDefaultText())

    # pull field refactoring
    if 'pull' in args.type and 'field' in args.type:
        # Read pull direction from args and convert it to boolean (True assigned to up direction and vice versa)
        direction = True
        if 'down' in args.type:
            direction = False

        # Step 6: Walk through the parse tree and refactor codes
        walker = ParseTreeWalker()

        code = None
        # First Iterate trough the directory (Find and remove codes)
        for index in range(0, len(input_files)):
            remove_listener = PullFieldRefactoringRemoveListener(
                common_token_stream_rewriter=token_stream_rewriter[index],
                parent_class_identifier=args.parent,
                child_class_identifier=args.child,
                filed_identifier=args.field,
                pull_direction=direction)

            walker.walk(t=parse_tree[index], listener=remove_listener)

            if code is None and remove_listener.field_code is not None:
                code = remove_listener.field_code

        # Second Iterate trough the directory (Insert codes)
        for index in range(0, len(input_files)):
            insert_listener = PullFieldRefactoringInsertListener(
                common_token_stream_rewriter=token_stream_rewriter[index],
                parent_class_identifier=args.parent,
                child_class_identifier=args.child,
                field_identifier=args.field,
                field_code=code,
                pull_direction=direction)
            walker.walk(t=parse_tree[index], listener=insert_listener)

            # Step 7: Write refactored codes on output files
            with open(output_files[index], mode='w', newline='') as file:
                file.write(token_stream_rewriter[index].getDefaultText())

    # rename package refactoring
    if 'rename package' == args.type:
        # Step 6: Walk through the parse tree and refactor codes
        walker = ParseTreeWalker()

        # First Iterate trough the directory (Find and remove codes)
        for index in range(0, len(input_files)):
            rename_listener = RenamePackageRefactoringListener(
                common_token_stream_rewriter=token_stream_rewriter[index],
                package_name=args.package,
                new_package_name=args.newpackage)

            walker.walk(t=parse_tree[index], listener=rename_listener)

            # Step 7: Write refactored codes on output files
            with open(output_files[index], mode='w', newline='') as file:
                file.write(token_stream_rewriter[index].getDefaultText())

    # remove method refactoring
    if 'remove method' == args.type:
        # Step 6: Walk through the parse tree and refactor codes
        walker = ParseTreeWalker()

        # First Iterate trough the directory (Find and remove codes)
        for index in range(0, len(input_files)):
            remove_listener = RemoveMethodRefactoringListener(common_token_stream_rewriter=token_stream_rewriter[index],
                                                              method_identifier=args.method)

            walker.walk(t=parse_tree[index], listener=remove_listener)

            # Step 7: Write refactored codes on output files
            with open(output_files[index], mode='w', newline='') as file:
                file.write(token_stream_rewriter[index].getDefaultText())


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', '--indir', help='Input directory',
                            default=r'C:\Users\Sahand\Desktop\Java Projects\pull down method')

    arg_parser.add_argument('-o', '--outdir', help='Output directory',
                            default=r'C:\Users\Sahand\Desktop\Java Projects\refactored project')

    arg_parser.add_argument('-t', '--type',
                            help='Recaftoring type (options: \'pull up method\', \'pull down method\', \'pull up field\', \'pull down field\', \'remove method\', \'rename package\'',
                            default=r'pull down method')

    arg_parser.add_argument('-p', '--parent', help='Parent class', default='Parent')
    arg_parser.add_argument('-c', '--child', help='Child class', default='Child')
    arg_parser.add_argument('-m', '--method', help='Method identifier', default='Method')
    arg_parser.add_argument('-f', '--field', help='Field identifier', default='Field')
    arg_parser.add_argument('-pk', '--package', help='Package name', default='pack')
    arg_parser.add_argument('-npk', '--newpackage', help='New package name', default='newPack')

    args = arg_parser.parse_args()
    main(args)
