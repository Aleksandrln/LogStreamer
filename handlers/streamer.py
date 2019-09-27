# coding=UTF-8
import tornado.web
import tornado.gen
import tornado.ioloop

import json

from tools import get_part_of_log


class BaseRequestHandler(tornado.web.RequestHandler):
    def json_result(self, result, ensure_ascii=True):
        self.set_header('Content-Type', 'application/json; charset=utf-8')
        self.finish(json.dumps(result, ensure_ascii=ensure_ascii))
        raise tornado.web.Finish()

    @staticmethod
    def run_in_executor(func, *args):
        return tornado.ioloop.IOLoop.current().run_in_executor(None, func, *args)


class LogStreamerHandler(BaseRequestHandler):
    @tornado.gen.coroutine
    def post(self):
        try:
            offset = int(self.get_argument('offset'))
        except tornado.web.MissingArgumentError:
            self.json_result(self._get_answer_error('argument "offset" not found'))
        except ValueError:
            self.json_result(self._get_answer_error('argument "offset" must be a number'))

        try:
            result = yield self.run_in_executor(self._post, offset)
        except IOError:
            self.json_result(self._get_answer_error('No such file or directory'))

        self.json_result(result)

    def _post(self, offset):
        result = self._get_answer_data(get_part_of_log(offset))
        return result

    @staticmethod
    def _get_answer_error(reason):
        return {"ok": False, "reason": reason}

    @staticmethod
    def _get_answer_data(data):
        result = dict({"ok": True,
                  "next_offset": 0,
                  "total_size": 0,
                  "messages": []
                  }, **data)
        return result
