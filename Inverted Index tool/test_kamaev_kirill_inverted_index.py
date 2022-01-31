"""tests for inverted index"""
import argparse
from unittest.mock import patch

import task_kamaev_kirill_inverted_index
from task_kamaev_kirill_inverted_index import *

DEFAULT_DATASET_TEST_PATH = "wikipedia_sample_test"


def test_can_dump_in_json():
    arguments = argparse.Namespace()
    arguments.dataset = "wikipedia_sample_test"
    arguments.output = DEFAULT_INVERTED_INDEX_STORE_PATH
    arguments.strategy = 'json'
    callback_build(arguments)


def test_for_wrong_strategy():
    arguments = argparse.Namespace()
    arguments.dataset = "wikipedia_sample_test"
    arguments.output = DEFAULT_INVERTED_INDEX_STORE_PATH
    arguments.strategy = 'abfds'
    callback_build(arguments)


def test_eq_indexes():
    docs = load_documents(DEFAULT_DATASET_TEST_PATH)
    inv_ind_left = build_inverted_index(docs)
    inv_ind_right = build_inverted_index(docs)
    assert inv_ind_left == inv_ind_right


def test_can_build_inverted_index():
    arguments = argparse.Namespace()
    arguments.dataset = "wikipedia_sample_test"
    arguments.output = DEFAULT_INVERTED_INDEX_STORE_PATH
    arguments.strategy = 'struct'
    callback_build(arguments)


def test_can_print_help():
    with patch.object(sys, "argv",
                      ["dir", "task_kamaev_kirill_inverted_index.py", "> alloutput.log 2>&1", "--help"]):
        with pytest.raises(SystemExit) as wrapped_exit:
            main()


def test_can_cmd_build():
    command_line = ["task_kamaev_kirill_inverted_index.py",
                    "build", "--strategy",
                    "struct", "--dataset",
                    DEFAULT_DATASET_TEST_PATH, "--output", DEFAULT_INVERTED_INDEX_STORE_PATH]
    with patch.object(sys, "argv", command_line):
        main()


def test_can_cmd_query_correctly(capsys):
    command_line = ["task_kamaev_kirill_inverted_index.py",
                    "query",
                    "--query", "Autism"]
    with patch.object(sys, "argv", command_line):
        main()
        captured = capsys.readouterr()
        assert '25' in captured.out


def test_can_cmd_query_file():
    command_line = ["task_kamaev_kirill_inverted_index.py",
                    "query", "--index",
                    DEFAULT_INVERTED_INDEX_STORE_PATH,  # "--strategy", "struct",
                    "--query-file-utf8", "queries.txt"]

    with patch.object(sys, "argv", command_line):
        main()


def test_can_process_all_queries_from_correct_file_correctly(capsys):
    with open("queries.txt", 'r') as queries_fin:
        process_queries(inverted_index_filepath=DEFAULT_INVERTED_INDEX_STORE_PATH,
                        query_file=queries_fin,
                        strategy="struct",
                        )
        captured = capsys.readouterr()
        assert "load inverted index" not in captured.out
        assert "load inverted index" in captured.err
        assert '25' in captured.out and '39' in captured.out


@pytest.fixture(scope="session")
def inverted_index():
    """create a class beforehand to speed up tests"""
    path = 'wikipedia_sample_test'
    documents = task_kamaev_kirill_inverted_index.load_documents(path)
    inverted_index = task_kamaev_kirill_inverted_index.build_inverted_index(documents)
    inverted_index.dump('pytest_invertedindex', 'struct')
    return inverted_index


def test_wrong_filepath_to_load(inverted_index):
    """tests empty or wrong filepath"""
    with pytest.raises(FileNotFoundError):
        inverted_index.load('', 'struct')


def test_for_non_existent_word(inverted_index):
    """test for non existent word to query"""
    result = inverted_index.query(['avcmmmmmone'])
    expected = list()
    assert result == expected


def test_for_empty_word(inverted_index):
    """test for empty to query"""
    result = inverted_index.query(['', ' '])
    expected = list()
    assert result == expected


def test_for_uppercase(inverted_index):
    """test uppercase to query"""
    result = inverted_index.query(['abracadabra'])
    expected = inverted_index.query(['Abracadabra'])
    assert expected == result


def test_for_same_words(inverted_index):
    """test many the same words to query"""
    result = inverted_index.query(['many', 'mAny', 'manY'])
    expected = inverted_index.query(['many'])
    assert expected == result


def test_for_empty_query(inverted_index):
    """test for empty list to query"""
    result = inverted_index.query([])
    expected = list()
    assert result == expected


def test_for_type_error(inverted_index):
    """test for wrong types to load"""
    with pytest.raises(TypeError):
        inverted_index.query([1, [2, 3], '4,5'])


def test_wrong_filepath_to_load_documents():
    """tests empty or wrong filepath"""
    with pytest.raises(FileNotFoundError):
        task_kamaev_kirill_inverted_index.load_documents("fdskdownfilepath")
