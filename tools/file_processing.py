# coding=UTF-8
import os
from collections import OrderedDict
from itertools import islice
import json

from settings import LOG_FILE_PATH


def get_part_of_log(offset=0, lines=10):
    result = {'total_size': 0, 'next_offset': 0, 'messages': []}

    with open(LOG_FILE_PATH, "rb", ) as f:
        f.seek(0, os.SEEK_END)
        result['total_size'] = f.tell()

        if offset <= result['total_size']:
            f.seek(offset)
            if f.read(1) == b'{':
                f.seek(-1, os.SEEK_CUR)
            else:  # Если смещение указаывает не на первый байт в строке, пропускаем строку
                f.readline()

            result['messages'].extend(json.loads(line.encode('utf-8'), object_pairs_hook=OrderedDict)
                                      for line in islice(iter(f.readline, b''), lines))
            result['next_offset'] = f.tell()
        else:
            result['next_offset'] = result['total_size']
        return result
