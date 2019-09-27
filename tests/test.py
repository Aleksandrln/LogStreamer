# coding=UTF-8
import random

import mock
import pytest

from faker import Faker
from mock_open import MockOpen

from settings import LOG_FILE_PATH
from tools.file_processing import get_part_of_log

LINE_FOR_TEST = b'{"level": "DEBUG", "message": "Blah blah blah"}\n' \
                b'{"level": "INFO", "message": "Everything is fine!"}\n' \
                b'{"level": "ERR", "message": "ERR"}'


@pytest.mark.parametrize(
    'offset,lines,json,valid',
    (
            (0, 1, LINE_FOR_TEST, [{"level": "DEBUG", "message": "Blah blah blah"}]),
            (2, 10, LINE_FOR_TEST,[{"level": "INFO", "message": "Everything is fine!"}, {"level": "ERR", "message": "ERR"}]),
            (2, 1, LINE_FOR_TEST, [{"level": "INFO", "message": "Everything is fine!"}]),
            (48, 1, LINE_FOR_TEST, [{"level": "INFO", "message": "Everything is fine!"}]),
            (49, 1, LINE_FOR_TEST, [{"level": "ERR", "message": "ERR"}]),
    ),
)
def test_get_part_of_log_read(offset, lines, json, valid):
    """
    Первые две цифры кортежа задают  offset и lines
    offset == 0 lines == 1 читаем первую строчку
    offset == 2 lines == 10 так как смещение указаывает не на первый байт в новой строке, возвращаем следующую строку.
    """
    m = MockOpen()
    m[LOG_FILE_PATH].read_data = json

    with mock.patch('__builtin__.open', new=m):
        assert get_part_of_log(offset, lines)['messages'] == valid


@pytest.mark.parametrize(
    'offset,json,valid',
    (
            (0, LINE_FOR_TEST, 48),
            (32, LINE_FOR_TEST, 100),
            (100, LINE_FOR_TEST, 134),
    ),
)
def test_get_part_of_log_next_line(offset, json, valid):
    m = MockOpen()
    m[LOG_FILE_PATH].read_data = json

    with mock.patch('__builtin__.open', new=m):
        assert get_part_of_log(offset, 1)['next_offset'] == valid
        assert get_part_of_log(offset, 1)['total_size'] == len(LINE_FOR_TEST)


def make_big_json_file(patch, size=8 * 1024 * 1024 * 1024):
    status = ['DEBUG', 'INFO', 'WARN', 'ERROR']
    fake = Faker()
    get_line = lambda: '{"level": "%s", "message": "%s"}' % (random.choice(status), fake.catch_phrase())

    with open(patch, 'wb') as f:
        while f.tell() < size:
            f.write('\n'.join(get_line() for i in xrange(1000)))
