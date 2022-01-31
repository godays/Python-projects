#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A working py file to use inverted index"""
from __future__ import annotations
import os
import sys
from io import TextIOWrapper

import struct
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType, ArgumentTypeError
from typing import Dict, List
import re
import json
import codecs
from collections import defaultdict
import pytest


DEFAULT_DATASET_PATH = "wikipedia_sample"
DEFAULT_INVERTED_INDEX_STORE_PATH = "inverted.index"


class EncodedFileType(FileType):
    '''custom FileType for usage'''
    def __call__(self, string):
        if string == '-':
            if 'r' in self._mode:
                stdin = TextIOWrapper(sys.stdin.buffer, encoding=self._encoding)
                return stdin
            elif 'w' in self._mode:
                stdout = TextIOWrapper(sys.stdout.buffer, encoding=self._encoding)
                return stdout
            else:
                msg = 'argument "-" with mode %r' % self._mode
                raise ValueError(msg)

        try:
            return open(string, self._mode, self._bufsize, self._encoding,
                        self._errors)
        except OSError as e:
            args = {'filename': string, 'error': e}
            message = "can't open '%(filename)s': %(error)s"
            raise ArgumentTypeError(message % args)


class InvertedIndex:
    """A class to create inverted index to query use"""

    def __init__(self, inverted_index):
        self.inverted_index = inverted_index

    def __eq__(self, rhs: InvertedIndex) -> bool:
        return self.inverted_index == rhs.inverted_index

    def query(self, words: List[str]) -> List[int]:
        """Return the list of relevant documents for the given query"""
        if not isinstance(words, list):
            raise TypeError

        if len(words) == 0:
            return list()

        lowered_words = list()
        for word in words:
            if not isinstance(word, str):
                raise TypeError

            word = word.lower()
            lowered_words.append(word)
            if word not in self.inverted_index.keys():
                return list()

        set_of_index = set(sorted(self.inverted_index[lowered_words[0]]))
        for word in lowered_words:
            set_of_index.intersection_update(set(sorted(self.inverted_index[word])))

        return sorted(list(set_of_index))

    def dump(self, filepath: str, strategy) -> None:
        """saves inverted index to file in given strategy"""
        if strategy == 'json':
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(self.inverted_index, file)
        elif strategy == 'struct':
            with open(filepath, 'wb') as file:
                array_of_docs_id = []
                file.write(struct.pack('I', len(self.inverted_index)))
                for word, doc_ids in self.inverted_index.items():
                    file.write(struct.pack('H', len(word.encode())))
                    file.write(struct.pack(str(len(word.encode())) + 's', word.encode()))
                    file.write(struct.pack('H', len(doc_ids)))
                    array_of_docs_id += doc_ids

                file.write(struct.pack('H' * len(array_of_docs_id), *array_of_docs_id))
        else:
            pytest.raises(TypeError)

    @classmethod
    def load(cls, filepath: str, strategy) -> InvertedIndex:
        """load inverted_index from json file to InvertedIndex class"""
        if not os.path.isfile(filepath):
            raise FileNotFoundError("File doesn't exist")

        if strategy == 'json':
            with open(filepath, "r") as file:
                file_content = file.read()
                dictionary = json.loads(file_content)
                inverted_index = cls(dictionary)
                return inverted_index
        elif strategy == 'struct':
            print("load inverted index", file=sys.stderr)
            with open(filepath, 'rb') as file:
                tmp_dict = defaultdict(int)
                dict_size = struct.unpack('I', file.read(struct.calcsize('I')))[0]
                for i in range(dict_size):
                    word_len = struct.unpack('H', file.read(struct.calcsize('H')))[0]
                    word = struct.unpack(str(word_len) + 's',
                                         file.read(word_len))[0].decode('utf-8')
                    cnt_ids = struct.unpack('H', file.read(struct.calcsize('H')))[0]
                    tmp_dict[word] = cnt_ids

                dictionary = defaultdict(list)
                for word, cnt_ids in tmp_dict.items():
                    ids_list = list(struct.unpack('H' * cnt_ids,
                                                  file.read(struct.calcsize('H') * cnt_ids)))
                    dictionary[word] = ids_list

                inverted_index = cls(dictionary)
                return inverted_index


def load_documents(filepath: str) -> Dict[int, str]:
    """loads documents to dict[int, str] type"""
    print("loading documents to build inverted index....", file=sys.stderr)
    if not os.path.isfile(filepath):
        raise FileNotFoundError("File doesn't exist")

    documents = defaultdict(str)

    with codecs.open(filepath, "r", "utf-8") as list_of_documents:
        for doc in list_of_documents:
            doc_id, content = doc.replace("\n", "").lower().split("\t", 1)
            doc_id = int(doc_id)
            documents[doc_id] = content

    return documents


def build_inverted_index(documents: Dict[int, str]) -> InvertedIndex:
    """builds inverted index from Dict[int, str] of documents"""
    print("building inverted index for provided documents...", file=sys.stderr)
    inverted_index = defaultdict(list)
    for doc_id, content in documents.items():
        unique_words = set(re.split(r"\W+", content))

        for word in unique_words:
            if word:
                inverted_index[word].append(doc_id)

    return InvertedIndex(inverted_index)


def callback_build(arguments):
    """parse build args to build and dump inverted index"""
    documents = load_documents(arguments.dataset)
    inverted_index = build_inverted_index(documents)
    inverted_index.dump(arguments.output, arguments.strategy)


def callback_query(arguments):
    """processing args to query from cmd or file"""
    if isinstance(arguments.query_file, list):
        inverted_index = InvertedIndex.load(arguments.inverted_index, arguments.strategy)
        for query in arguments.query_file:
            document_ids = inverted_index.query(query)
            print(*document_ids, sep=",", file=sys.stdout)

    else:
        return process_queries(arguments.inverted_index, arguments.query_file, arguments.strategy)


def process_queries(inverted_index_filepath, query_file, strategy):
    """parse query args to print query"""
    inverted_index = InvertedIndex.load(inverted_index_filepath, strategy)

    while query_file:
        line = query_file.readline().rstrip('\n')
        if line == "":
            break
        document_ids = inverted_index.query(line.split())
        print(*document_ids, sep=",", file=sys.stdout)


def setup_parser(parser):
    """args for cmd use"""
    subparsers = parser.add_subparsers(help="choose command")

    build_parser = subparsers.add_parser(
        "build",
        help="build inverted index and save in binary format into hard drive",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    build_parser.add_argument(
        "-d", "--dataset",
        default=DEFAULT_DATASET_PATH,
        help="path to dataset to load, default path is %(default)s",
    )
    build_parser.add_argument(
        "-o", "--output", default=DEFAULT_INVERTED_INDEX_STORE_PATH,
        help="path to store inverted index in a binary format",
    )

    build_parser.add_argument(
        "-s", "--strategy",
        choices=['json', 'struct'],
        default='struct',
        help="set storage policy, default is %(default)s",
    )
    build_parser.set_defaults(callback=callback_build)

    query_parser = subparsers.add_parser(
        "query",
        help="query inverted index",
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    query_parser.add_argument(
        "--index",
        dest="inverted_index",
        default=DEFAULT_INVERTED_INDEX_STORE_PATH,
        help="path to read inverted index in a binary form",
    )
    query_parser.add_argument(
        "--strategy",
        dest="strategy",
        choices=['json', 'struct'],
        default='struct',
        help="set storage policy, default is %(default)s",
    )
    query_file_group = query_parser.add_mutually_exclusive_group(required=True)
    query_file_group.add_argument(
        "-q", "--query", nargs="+",
        dest="query_file",
        metavar='WORD',
        action='append',
        help="query to run against inverted index",
    )
    query_file_group.add_argument(
        "--query-file-utf8", dest="query_file", type=EncodedFileType("r", encoding="utf-8"),
        help="query file in utf8 to get queries for inverted index",
    )
    query_file_group.add_argument(
        "--query-file-cp1251", dest="query_file", type=EncodedFileType("r", encoding="cp1251"),
        help="query file in cp1251 to get queries for inverted index",
    )
    query_parser.set_defaults(callback=callback_query)


def main():
    """main function to work with cmd interface"""
    parser = ArgumentParser(
        prog="Inverted Index CLI",
        description="Inverted Index CLI tool to build, dump, load and query inverted index",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    setup_parser(parser)
    arguments = parser.parse_args()
    arguments.callback(arguments)


if __name__ == "__main__":
    main()
