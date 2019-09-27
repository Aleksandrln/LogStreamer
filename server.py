import signal
import sys

import tornado.ioloop
import tornado.web

from handlers import LogStreamerHandler


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/read_log", LogStreamerHandler),
        ]

        super(Application, self).__init__(handlers)


def stop_tornado(signo, stack_frame):
    tornado.ioloop.IOLoop.instance().stop()
    sys.exit(0)


if __name__ == "__main__":
    app = Application()
    app.listen(8888)


    signal.signal(signal.SIGINT, stop_tornado)
    signal.signal(signal.SIGTERM, stop_tornado)

    tornado.ioloop.IOLoop.current().start()
