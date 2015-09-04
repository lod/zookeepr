from routes import url_for
from HTMLParser import HTMLParser

def do_login(app, person_or_email_address, password=None):
    # Overload the function to allow just throwing a person object
    if password is None:
        email_address = person_or_email_address.email_address
        password = person_or_email_address.raw_password
    else:
        email_address = person_or_email_address

    # Disabling cookies makes login function reentrant
    resp = app.get(url_for(controller='person', action='signin'), headers={'Cookie':''})

    f = resp.forms['signin-form']
    f['person.email_address'] = email_address
    f['person.password'] = password
    return f.submit(extra_environ=dict(REMOTE_ADDR='0.0.0.0'))

def isSignedIn(app):
    return 'authkit' in app.cookies and len(app.cookies['authkit']) > 15

class TableParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self) # Old style class
        self.sel_id = kwargs.get("id")
        self.sel_class = kwargs.get("class")
        self.tables = []
        self.in_table = False # Mostly to differentiate selected from ignored tables
        self.in_cell = False
    def handle_starttag(self, tag, attrs):
        dattrs = dict(attrs)
        if tag == "table":
            if self.sel_id and dattrs.get("id") != self.sel_id:
                return # Fail selector - bail
            if self.sel_class and dattrs.get("class") != self.sel_class: # TODO: Support multiple classes
                return # Fail selector - bail
            self.tables.append([])
            self.in_table = True
        if not self.in_table:
            return
        if tag == "tr":
            self.tables[-1].append([])
        if tag == "td" or tag == "th":
            self.in_cell = True
            self.tables[-1][-1].append("")
    def handle_endtag(self, tag):
        if not self.in_table:
            return
        if tag == "td" or tag == "th":
            self.in_cell = False
        if tag == "table":
            self.in_table = False
    def handle_data(self, data):
        if not self.in_table:
            return
        if self.in_cell:
            self.tables[-1][-1][-1] += data
