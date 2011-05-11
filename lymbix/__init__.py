import urllib2
import urllib
import json

__ALL__ = ['Client']

__VERSION__ = '0.1'
__USER_AGENT__ = 'Python Lymbix Client %s' % __VERSION__

class TransportError(Exception): pass

class ResponseError(Exception):
    def __init__(self, message, data):
        Exception.__init__(self, message)
        self.data = data

class Client(object):
    def __init__(self, auth_key, host = 'api.lymbix.com', api_version = 2.1, timeout = None, transport = "http", format = "application/json", return_fields = []):
        """
        @param auth_key authentication key provided from Lymbix.com
        @param api_version api version to use for RPC
        """
        self.auth_key = auth_key
        self.api_version = api_version
        self.host = host
        self.transport = transport
        self.format = format
        self.return_fields = return_fields
        self.timeout = timeout


    # Tonalizes text using version 2.1,2.2 of ToneAPI
    def tonalize(self, article, article_reference_id = None):
        article_reference_id = "" if article_reference_id == None else article_reference_id
        return self._request('tonalize',
                             {'article': article, 'return_fields': json.dumps(self.return_fields), 'reference_id': str(article_reference_id)})
    
    
    # Tonalizes text using version 2.0 of ToneAPI
    def tonalize_article(self, article):
        return self._request('tonalize_article',
                             {'article': article},
                             api_version = '2.0')
        
    # Tonalizes mutliple articles using version 2.1 of ToneAPI. With the return_fields param you can now specify which field to get back from the API.
    def tonalize_multiple(self, ref_article_map):
        articles = []
        refs = []
        for ref, article in ref_article_map.items():
            articles.append(article)
            refs.append(ref)
            
        return self._request('tonalize_multiple',
                             {'articles': json.dumps(articles), 
                              'return_fields': json.dumps(self.return_fields), 
                              'article_reference_ids': json.dumps(refs)})

    # Tonalizes article using version 2.1 of ToneAPI. With the return_fields param you can now specify which field to get back from the API.
    # The detailed response includes the tonalization data for the article and all sentences found in the article
    def tonalize_detailed(self, article, article_reference_id = None):
        article_reference_id = "" if article_reference_id == None else article_reference_id
        return self._request('tonalize_detailed',
                             {'article': article, 
                              'return_fields': json.dumps(self.return_fields), 
                              'article_reference_id': article_reference_id})
    
    def flag_response(self, reference_id, phrase, api_method_requested, api_version = None, callback_url = None):
        api_version = self.api_version if not api_version else api_version
        return self._request('flag_response', 
                             {'reference_id': reference_id, 
                              'phrase': phrase, 
                              'api_method_requested': api_method_requested, 
                              'api_version': api_version, 
                              'callback_url': callback_url})


    def _request(self, action, data, extra_headers = None, http_method = 'POST', api_version = None):
        
        headers = {'Authentication': self.auth_key, 
                   'Version': self.api_version if not api_version else api_version, 
                   'Accept': self.format,
                   'User-Agent': __USER_AGENT__}
        
        if extra_headers:
            headers.update(extra_headers)
        
        return Request("%s://%s/%s" % (self.transport, self.host, action), 
                       headers,
                       timeout = self.timeout,
                       data = data,
                       http_method = http_method,
                       format = self.format).execute()

class Request(object):
    def __init__(self, url, header_hash, timeout, data = None, http_method = 'POST', format = 'application/json'):
        self.url = url 
        self.http_method = http_method
        self.data = data
        self.headers = header_hash
        self.timeout = timeout
        self.format = format

    def execute(self):
        if self.http_method != 'POST':
            raise NotImplemented
        
        if type(self.data) == str:
            data = self.data
        elif type(self.data) in (list, dict):
            data = urllib.urlencode(self.data)
        elif self.data is None:
            data = ''
        else:
            raise ValueError("Unable to format data type for transmission: %s" % type(self.data))
            
        req = urllib2.Request(self.url, data, self.headers)
        
        try:
            response = urllib2.urlopen(req, timeout=self.timeout)
        except IOError, e:
            if hasattr(e, 'reason'):
                raise TransportError("Connection error: %s" % e.reason)
            elif hasattr(e, 'code'):
                raise TransportError("HTTP status error: %s" % e.code)
            else:
                raise
        
        if self.format != 'application/json':
            return data
        return self._handle_json_response(response.read())
    
    def _handle_json_response(self, data):
        
        if data == 'null':
            raise ResponseError("Service returned 'null'", data)

        try:
            data = json.loads(data)
        except ValueError, e:
            raise ResponseError("Server returned bad JSON: %s" % str(e), data)        
        
        if type(data) == dict:
            if data.get('success', True) == False:
                raise ResponseError("Server response indicates a failure", data)
        
        return data

def test_main():
    import sys
    import os
    import pprint
    sys.argv.pop(0)
    
    api_key = os.environ.pop('LYMBIX_API_KEY', None)
    
    if not api_key:
        api_key = sys.argv.pop(0)
    
    print "Using API key: %s..." % api_key
    
    data = " ".join(sys.argv)
    print "Querying '%s'..." % data
    
    c = Client(api_key)
    pprint.pprint(c.tonalize(data))

if __name__ == '__main__':
    test_main()