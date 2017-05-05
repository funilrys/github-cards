#!/bin/env python
from os import errno, makedirs, path
from re import split as sp
from subprocess import Popen, PIPE


class GenerateTemplate(object):
    """docstring for GenerateTemplate."""

    def __init__(self, theme):
        self.theme = theme

        self.DIRECTORY_SEPARATOR = '/'
        self.SRC_DIR = 'src' + self.DIRECTORY_SEPARATOR
        self.SRC_THEME_DIR = self.SRC_DIR + 'theme' + self.DIRECTORY_SEPARATOR
        self.SRC_JS_DIR = self.SRC_DIR + 'js' + self.DIRECTORY_SEPARATOR

        self.CARDS_FN = 'card.js'
        self.WIDGET_FN = 'widget.js'
        self.THEME_HTML = self.SRC_THEME_DIR + '%s.html' % self.theme
        self.THEME_CSS = self.SRC_THEME_DIR + '%s.css' % self.theme

        self.SRC_CARD = self.SRC_JS_DIR + self.CARDS_FN
        self.SRC_WIDGET = self.SRC_JS_DIR + self.WIDGET_FN

        self.NODE_DIR = 'node_modules' + self.DIRECTORY_SEPARATOR + \
            '.bin' + self.DIRECTORY_SEPARATOR
        self.CLEANCSS = self.NODE_DIR + 'cleancss'
        self.UGLIFYJS = self.NODE_DIR + 'uglifyjs'

        self.JS_OUT = 'js' + self.DIRECTORY_SEPARATOR
        self.CARDS_OUT = 'cards' + self.DIRECTORY_SEPARATOR + '%s.html' % self.theme
        self.WIDGET_OUT = self.JS_OUT + self.WIDGET_FN

        self.SASS_CMD = 'sass'
        self.SASS_DIR = self.SRC_THEME_DIR + '_scss' + \
            self.DIRECTORY_SEPARATOR + self.theme + self.DIRECTORY_SEPARATOR
        self.SASS_BUILD_FILE = self.SASS_DIR + 'c' + self.theme + '.scss'
        self.SASS_OUTPUT = self.SRC_THEME_DIR + self.theme + '.css'

        self.HTML = (
            '<!doctype html><html><body>'
            '<style type="text/css">%s</style>%s'
            '<script>%s</script>'
            '</body></html>'
        )

        self.new_dirs = ['cards', self.JS_OUT]

        if not path.isdir(self.NODE_DIR) or not path.isfile(self.CLEANCSS) or not path.isfile(self.UGLIFYJS):
            self.execute_command(['npm', 'install'])

        for dir in self.new_dirs:
            if not path.isdir(dir):
                makedirs(dir)

        self.create_widget()
        self.create_card()

    def execute_command(self, command, data=None):
        p = Popen(command, stdin=PIPE, stdout=PIPE,
                  stderr=PIPE)
        r = p.communicate(input=data)
        if p.returncode != 0:
            raise r[1]
        return r[0]

    def minify_html(self, text):
        lines = sp('(<[^>]+>)', text)
        rv = []

        for line in lines:
            line = line.strip()
            rv.append(line)
        return ''.join(rv)

    def build_sass(self):
        try:
            self.execute_command(
                [self.SASS_CMD, self.SASS_BUILD_FILE, self.SASS_OUTPUT])
        except OSError as e:
            if e.errno == errno.ENOENT:
                print("Please install sass.")
                exit()

    def create_card(self):
        self.build_sass()

        with open(self.THEME_HTML) as file:
            template = file.read()

        css = self.execute_command([self.CLEANCSS, self.THEME_CSS])

        with open(self.SRC_CARD, 'rb') as file:
            content = file.read()

        js = self.execute_command([self.UGLIFYJS, '-m'], content)
        output = self.HTML % (css, self.minify_html(template), js)

        with open(self.CARDS_OUT, 'w') as file:
            file.write(output)
        print(self.CARDS_OUT + ' generated')

    def create_widget(self):
        with open(self.SRC_WIDGET, 'rb') as file:
            content = file.read()

        js = self.execute_command([self.UGLIFYJS, '-m'], content)

        with open(self.WIDGET_OUT, 'wb') as file:
            file.write(js)
GenerateTemplate('default')
GenerateTemplate('medium')
