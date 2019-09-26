import os

from prometheus_client import make_wsgi_app
from tornado import ioloop, options, web, wsgi

options.define('debug', default=os.getenv('ENV') == 'development')
options.define('port', default=8888, type=int)


class GithubWebhookHandler(web.RequestHandler):
    async def post(self):
        pass


class Application(web.Application):
    def __init__(self, settings):
        metrics_handler = wsgi.WSGIContainer(make_wsgi_app())

        handlers = [
            (r'/webhooks/github', GithubWebhookHandler),
            (r'/metrics', metrics_handler)
        ]
        settings.update(dict(

        ))
        super().__init__(handlers, **settings)


if __name__ == '__main__':
    options.parse_command_line()
    Application(options.options.as_dict()).listen(options.options.port)
    try:
        ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        ioloop.IOLoop.current().stop()
