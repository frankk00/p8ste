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


import cgi
import difflib

import app
import app.model
import app.util
import app.web
import app.web.ui
import settings
import smoid.languages


class Diff (app.web.RequestHandler):
    """
    Shows a diff of two pastes (maybe more in the future ?)
    """

    def __init__ (self):
        app.web.RequestHandler.__init__(self)
        self.set_module(__name__ + ".__init__")
        self.use_style(app.url("style/code.css"))
        self.paste1_slug = ""
        self.paste1 = None
        self.paste2_slug = ""
        self.paste2 = None
        self.pastes = []
        self.paste_slugs = []

    def get (self, paste1_slug, paste2_slug):
        self.pastes = [self.get_paste (paste1_slug), self.get_paste (paste2_slug)]
        self.paste_slugs = [paste1_slug, paste2_slug]

        if None in self.pastes:
            self.get_404()
        else:
            unpublic_paste = None
            for paste in self.pastes:
                if not paste.is_public():
                    unpublic_paste = paste
                    break

            if unpublic_paste:
                self.content["paste_slug"] = unpublic_paste.slug
                self.content["u_paste"] = unpublic_paste.get_url()
                self.content["paste_is_private"] = unpublic_paste.is_private()
                self.content["paste_is_moderated"] = unpublic_paste.is_moderated()
                self.content["paste_is_awaiting_approval"] = unpublic_paste.is_waiting_for_approval()
                self.error(401)
                self.write_out("./not_public.html")
            else:
                self.get_200()

    def get_200 (self):
        """
        Shows the diff if all the pastes submitted are found.
        """

        self.content["u_list"] = app.url(self.paste_slugs[0] + "+" + self.paste_slugs[1])
        self.content["u_reverse"] = app.url(self.paste_slugs[1] + "/diff/" + self.paste_slugs[0])
        tpl_pastes = [self.get_template_info_for_paste(0), self.get_template_info_for_paste(1)]
        self.content["pastes"] = tpl_pastes
        self.content["diff"] = self.get_diff()

        self.write_out("./200.html")

    def get_404 (self):
        """
        Shows an 404 error page if one, or more, pastes were not found.
        """

        self.content["error"] = {}
        self.content["error"]["pastes_not_found"] = []
        self.content["error"]["pastes_found"] = []
        self.content["u_pastes"] = app.url("pastes/")
        i = 0
        for opaste in self.pastes:
           tpl_paste = {}
           tpl_paste["u"] = app.url("%s", self.paste_slugs[i])
           tpl_paste["slug"] = self.paste_slugs[i]
           if opaste == None:
               self.content["error"]["pastes_not_found"].append(tpl_paste)
           else:
               self.content["error"]["pastes_found"].append(tpl_paste)
           i = i + 1

        self.write_out("./404.html")

    def get_diff (self):
        """
        Computes a diff and annotate each line with a line number.
        """

        diff = []
        differ = difflib.Differ()

        lineno1 = 0
        lineno2 = 0

        for line in differ.compare(self.pastes[0].get_raw_code().splitlines(), self.pastes[1].get_raw_code().splitlines()):
            line_start = line[0:2]

            if line_start == "- ":
                lineno1 += 1
                diff.append([lineno1, "", line])

            elif line_start == "+ ":
                lineno2 += 1
                diff.append( ["", lineno2, line] )

            elif line_start == "? ":
                pass

            else:
                lineno1 += 1
                lineno2 += 1
                diff.append([lineno1, lineno2, line])

        return diff

    def get_paste (self, slug):
        """
        Retrieves a paste from the datastore given its slug.
        """

        qry_paste = app.model.Pasty.all()
        qry_paste.filter("slug =", slug)

        return qry_paste.get()

    def get_template_info_for_paste (self, paste_index):
        """
        Builds an info map about a paste for using in the template.
        """

        info = {}
        opaste = self.pastes[paste_index]

        if opaste:
            info["slug"] = opaste.slug
            info["posted_at"] = opaste.posted_at.strftime(settings.DATETIME_FORMAT)
            info["u"] = app.url("%s", opaste.slug)
            info["posted_by"] = opaste.posted_by_user_name

            info["language"] = opaste.get_language_name()
            info["u_language_icon"] = opaste.get_icon_url()

            if opaste.characters:
                info["size"] = app.util.make_filesize_readable(opaste.characters)

            if opaste.lines:
                info["loc"] = opaste.lines

        return info
