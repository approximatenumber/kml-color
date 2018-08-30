#!/usr/bin/env python3
import tornado.httpserver, tornado.ioloop, tornado.options, tornado.web, os.path, random, string
from tornado.options import define, options
import os
import subprocess

define("port", default=8888, help="run on the given port", type=int)

style = """
        <link rel="stylesheet" type="text/css" href="css/main.css">
        <link rel="stylesheet" type="text/css" href="css/font-awesome.min.css">
        """
template = '<html><head>%s</head><body><p align=\'center\'>{}</p></body></html>' % style
upload_dir = 'uploads'


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/upload", UploadHandler),
            (r"/download", DownloadHandler),
            (r'/(.*)', tornado.web.StaticFileHandler, {'path': 'static'})
        ]
        tornado.web.Application.__init__(self, handlers)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        file1 = self.request.files['file1'][0]
        original_fname = file1['filename']
        filename, extension = os.path.splitext(original_fname)
        fname = ''.join([''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6)),
                        '_',
                        filename])
        final_filename = fname + extension
        output_file = open(upload_dir + os.sep + final_filename, 'wb')
        output_file.write(file1['body'])
        converted = subprocess.Popen(['python3', 'kml_color.py', '%s/%s' % (upload_dir,
                                                                            final_filename)])
        converted.communicate()
        if converted.returncode:
            answer = template.format('Error occured while processing your file.')
            self.finish(answer)
            return
        answer = template.format('Hooray! Import this file to your MAPS.me app. <br />\
                                  <a href=\"/download?file=%s\">Download</a>' % final_filename)
        self.finish(answer)


class DownloadHandler(tornado.web.RequestHandler):

    def get(self):

        _file_dir = os.path.abspath("") + "/%s" % upload_dir
        file_name = self.get_argument('file', None)
        _file_path = "%s/%s" % (_file_dir, file_name)
        if not file_name or not os.path.exists(_file_path):
            self.set_status(400)
            self.finish(template.format('Not Found.'))
        self.set_header('Content-Type', 'application/force-download')
        self.set_header('Content-Disposition', 'attachment; filename=%s' % file_name)
        with open(_file_path, "rb") as f:
            try:
                while True:
                    _buffer = f.read(4096)
                    if _buffer:
                        self.write(_buffer)
                    else:
                        f.close()
                        self.finish()
                        return
            except:
                self.set_status(400)
                self.finish(template.format('Not Found.'))
        self.set_status(500)
        self.finish(template.format('Error occured.'))


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
