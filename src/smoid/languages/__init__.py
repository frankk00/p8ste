# Copyright 2008 Thomas Quemard
#
# Paste-It is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 3.0, or (at your option)
# any later version.
#
# Paste-It is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.


import re


languages = {}

languages["php"] = {
    "lexer": "php",
    "name": "PHP",
    "home_url": "http://php.net",
    "u_icon": "images/languages/php.png"
}

languages["perl"] = {
    "lexer": "perl",
    "name": "Perl",
    "home_url": "http://www.perl.org",
    "u_icon": "images/languages/perl.png"
}

languages["python"] = {
    "lexer": "python",
    "name": "Python",
    "home_url": "http://python.org",
    "u_icon": "images/languages/python.png"
}

languages["ruby"] = {
    "lexer": "ruby",
    "name": "Ruby",
    "home_url": "http://www.ruby-lang.org",
    "u_icon": "images/languages/ruby.png"
}

languages["xml"] = {
    "lexer": "xml",
    "name": "XML",
    "home_url": "http://www.w3.org/TR/2006/REC-xml11-20060816/",
    "u_icon": "images/languages/xml.png"
}

class Check:

    def __init__(self):
        self.content = ""
        self.example = ""
        self.languages = {}
        self.multiple_matches = []
        self.name = ""
        self.one_time_matches = []
        self.probability = 0

    def add_language (self, language_name):
        self.languages[language_name] = CheckLanguage(name=language_name)

    def add_multiple_matches (self, regex, probability):
        self.multiple_matches.append((regex, probability))

    def add_one_time_match (self, regex, probability):
        self.one_time_matches.append((regex, probability))

    def check (self, content):
        self.probability = 0
        self.content = content

        for match in self.one_time_matches:
            if self.is_re_matched(match[0]):
                for lang in self.languages:
                    self.languages[lang].probability += match[1]

        for match_info in self.multiple_matches:
            all_matched = re.findall(match_info[0], content)
            for matched in all_matched:
                for lang in self.languages:
                    self.languages[lang].probability += match[1]

        self._test()

    def check_verbose (self, content):
        print "Checking <", self.name, ">",
        if self.example:
            print ", ex: <" + self.example + ">",

        self.check(content)

        print "... ",

        did_languages_passed = False
        languages = ""
        if len(self.languages) > 0:
            for language_name in self.languages:
                prob = self.languages[language_name].probability
                if prob > 0:
                    languages += language_name + " +" + str(prob) + ", "
                    did_languages_passed = True

        if did_languages_passed:
            print "[" + languages[:-2] + "]"
        else:
            print ""


    def incr_language_probability (self, name, prob_diff):
        if name in self.languages:
            self.languages[name].probability += prob_diff

    def incr_probability (self, prob_diff):
        for language_name in self.languages:
            self.languages[language_name].probability += prob_diff

    def is_re_found (self, regex, start_at = 0):
        return re.compile(regex).search(self.content, start_at)

    def is_re_matched (self, regex, start_at = 0):
        return re.compile(regex).match(self.content, start_at)

    def set_languages (self, languages):
        self.languages = languages

    def _test (self):
        pass

class CheckLanguage:
    def __init__ (self, name="", probability=0):
        self.name = name
        self.probability = probability

class CheckCollection (list):
    pass
