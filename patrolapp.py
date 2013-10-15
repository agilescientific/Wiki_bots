import webapp2

class Handler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello webapp2!')
        
app = webapp2.WSGIApplication([
    ('/', Handler),
    ], debug = True)
    
def main():
    from paste import httpserver
    httpserver.serve(app, host = '127.0.0.1', port = '8081')

if __name__ == '__main__':
    main()