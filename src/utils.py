from werkzeug.routing import BaseConverter

#This code was imported entirely from PWP exercise 4
class RegexConverter(BaseConverter):
    '''
    This class is used to allow regex expressions as converters in the url
    '''
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]