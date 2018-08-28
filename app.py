import tornado.httpserver, tornado.ioloop, tornado.options, tornado.web, os.path, random, string
from tornado.options import define, options
import time
import subprocess

define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/upload", UploadHandler),
            (r"/download", DownloadHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        file1 = self.request.files['file1'][0]
        original_fname = file1['filename']
        extension = os.path.splitext(original_fname)[1]
        fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6))
        final_filename = fname + extension
        output_file = open("uploads/" + final_filename, 'wb')
        output_file.write(file1['body'])
        converted = subprocess.Popen(['python3', 'kml_color.py', 'uploads/%s' % final_filename])
        converted.communicate()
        if converted.returncode:
            self.finish("Invalid file!")
            return
        self.finish("<center><p>Hooray! Import this file to your MAPS.me app.</p><a href=\"/download?file=%s\">Download</a></center>" % final_filename)


class DownloadHandler(tornado.web.RequestHandler):

    def get(self):
        _file_dir = os.path.abspath("")+"/uploads"
        file_name = self.get_argument('file', None)
        _file_path = "%s/%s" % (_file_dir, file_name)
        if not file_name or not os.path.exists(_file_path):
            self.set_status(400)
            self.finish("<html><body>not found</body></html>")
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
                self.finish("<html><body>not found</body></html>")
        self.set_status(500)
        self.finish("<html><body>gotcha error</body></html>")


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
