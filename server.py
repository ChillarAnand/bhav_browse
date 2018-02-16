"""
CheeryPy server script to query redis and return matched results.
"""

import os
import json

import cherrypy

from fetch_data import filter_bhav_data, dump_sample_data


dump_sample_data()

port = int(os.environ.get("PORT", 8000))

cherrypy.config.update({
    'server.socket_host': "0.0.0.0",
    'server.socket_port': port,
})


class BhavBrowser():
    @cherrypy.expose
    def index(self):
        return open('index.html')

    @cherrypy.expose
    def bhavdata(self, query=None, *args, **kwargs):
        if not query:
            query = 'A'
        else:
            query = query.upper()
        pattern = query + '*'
        results = filter_bhav_data(pattern)
        data = {'data': results}
        return json.dumps(data)


if __name__ == '__main__':
    cherrypy.quickstart(BhavBrowser())
