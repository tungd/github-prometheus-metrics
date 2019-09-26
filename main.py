import logging
import os
from types import SimpleNamespace

from prometheus_client import Counter, Summary, make_wsgi_app
from tornado import ioloop, options, web, wsgi
from tornado.escape import json_decode, json_encode

options.define('debug', default=os.getenv('ENV') == 'development')
options.define('port', default=os.getenv('PORT', '8888'), type=int)

metrics = SimpleNamespace(
    request_time=Summary('request_processing_seconds', 'Time spent processing request'),
    commit_count=Counter('git_commit_count', 'Commit count', ['repository'])
)


class JsonMixin(web.RequestHandler):
    def prepare(self):
        super().prepare()
        if self.request.headers.get('Content-Type') == 'application/json':
            self.request.json = json_decode(self.request.body)

    def respond(self, data):
        self.set_header('Content-Type', 'application/json')
        self.write(json_encode(data))

    def get_argument(self, name, default=None, strip=True):
        if hasattr(self.request, 'json'):
            return self.request.json.get(name, default)
        return super().get_argument(name, default, strip)


class GithubWebhookHandler(JsonMixin, web.RequestHandler):
    @metrics.request_time.time()
    def post(self):
        logging.debug(self.request.json)
        event = self.request.headers['X-GitHub-Event']
        if event == 'push':
            repository = self.get_argument('repository')['full_name']
            commit_count = len(self.get_argument('commits'))
            metrics.commit_count.labels(repository).inc(commit_count)
        self.respond({'success': True})


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
