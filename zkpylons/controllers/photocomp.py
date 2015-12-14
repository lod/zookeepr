import cStringIO
import logging
import os
import random
import re
import sys
import time
import errno

from datetime import datetime, date, timedelta
from PIL import Image

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort
from zkpylons.lib.helpers import redirect_to
from pylons.decorators import validate
from pylons.decorators.rest import dispatch_on

from formencode import htmlfill, validators
from formencode.variabledecode import NestedVariables

from zkpylons.lib.auth import Predicate, ActionProtector, in_group

from webhelpers import paginate

from zkpylons.config import zkpylons_config
from zkpylons.lib.base import BaseController, render
from zkpylons.lib import helpers as h
from zkpylons.model import Person
from zkpylons.model.config import Config

log = logging.getLogger(__name__)


DAYS_OPEN       = 4                     # Number of days the competition is open
ENTRY_NAMES     = ("1", "2")            # Names of daily entries
MAX_IMAGE_SIZE  = 10                    # Max image size in mega bytes
VALID_EXTENSIONS= ("jpg","jpeg")        # Acceptable file name extensions

#
# The photo files are stored in a directory, the file names describing all
# the required attributes.
#
class PhotoCompEntry(object):
    SCALES      = frozenset(('orig', '68x51', '250x250', '1024x768'))
    day         = None
    person_id   = None
    entry_id    = None
    image_name  = None
    image       = None
    scales      = None

    def __init__(self, person_id, day, entry_id, image_name):
        self.person_id = person_id
        self.day = day
        self.entry_id = entry_id
        self.image_name = image_name
        self.scales = set()

    def filename(self, scale):
        start_timestamp = datetime.strptime(Config.get("date"), "%Y-%m-%dT%H:%M:%S")
        date_day = start_timestamp + timedelta(self.day)
        date_str = date_day.strftime("%Y%m%d")
        return "%s-%08d-%d-%s-%s" % (date_str, self.person_id, self.entry_id, scale, self.image_name)

    def pathname(self, scale):
        return os.path.join(self.get_db_dir(), self.filename(scale))

    def write_orig(self, image_data):
        handle = open(self.pathname("orig"), "wb")
        try:
            return handle.write(image_data)
        except:
            handle.close()

    def write_scaled(self):
        if self.scales == self.SCALES:
            return
        unwanted_scales = self.scales - self.SCALES
        for scale in unwanted_scales:
            try:
                os.remove(self.pathname(scale))
            except EnvironmentError, e:
                if e.errno != errno.ENOENT:
                    raise
        self.scales -= unwanted_scales
        if self.scales == self.SCALES:
            return
        image = Image.open(self.pathname("orig"))
        scales = list(self.SCALES - self.scales)
        scales.sort(key=lambda s: -int(s.split("x")[0],10))
        for scale in scales:
            bbox = image.getbbox()
            x, y = bbox[2] - bbox[0], bbox[3] - bbox[1]
            max_x, max_y = [int(s) for s in scale.split("x")]
            x_scale, y_scale = float(x) / max_x, float(y) / max_y
            if x_scale > 1.0 or y_scale > 1.0:
                if x_scale <= y_scale:
                    new_size = (int(x / y_scale), max_y)
                else:
                    new_size = (max_x, int(y / x_scale))
                image = image.resize(new_size, Image.ANTIALIAS)
            image.save(self.pathname(scale))
            self.scales.add(scale)

    def delete(self, db):
        if self.person_id in db:
            db[self.person_id][self.day][self.entry_id] = None
        for scale in self.SCALES:
            try:
                os.remove(self.pathname(scale))
            except EnvironmentError, e:
                if e.errno != errno.ENOENT:
                    raise

    def add(self, db):
        if self.day < 0 or self.day >= DAYS_OPEN:
            log.info("Invalid day %d" % self.day, self)
            return
        if self.entry_id < 0 or self.entry_id >= len(ENTRY_NAMES):
            log.info("Invalid entry_id %d" % self.entry_id, self)
            return
        if not self.person_id in db:
            db[self.person_id] = []
            for day in range(DAYS_OPEN):
                db[self.person_id].append([None] * len(ENTRY_NAMES))
        current = db[self.person_id][self.day][self.entry_id]
        if current is None:
            db[self.person_id][self.day][self.entry_id] = self
            current = self
        current.scales |= self.scales

    def get(cls, db, person_id, day, entry_id):
        if not person_id in db:
            return None
        result = db[person_id][day][entry_id]
        if result is not None:
            result.write_scaled()
        return result
    get = classmethod(get)

    # Read the directory storing the photos and return:
    #  {person_id: [[MonEntry0,MonEntry1], ... [ThuEntry0,ThuEntry1]], ...}
    def read_db(cls):
        db_dir = cls.get_db_dir()
        db = {}
        count = 0
        for entry_filename in os.listdir(db_dir):
            if entry_filename.startswith("."):
                continue
            photo = cls.from_filename(entry_filename)
            photo.add(db)
            count += 1
        #
        # Get rid of photos that don't have an original.
        #
        for person_id in db:
            for day_photos in db[person_id]:
                for photo in day_photos:
                    if photo is None:
                        continue
                    if 'orig' not in photo.scales:
                        photo.delete(db)
        return db
    read_db = classmethod(read_db)

    def from_filename(cls, filename):
        toks = filename.split("-", 4)
        open_date = datetime.strptime(Config.get("date"), "%Y-%m-%dT%H:%M:%S")
        photo_date = datetime(*time.strptime(toks[0], "%Y%m%d")[:3])
        day = (photo_date.date() - open_date.date()).days
        assert day >= 0 # negative days can lead to interesting problems
        person_id = int(toks[1], 10)
        entry_id = int(toks[2], 10)
        image_name = toks[4]
        photo = cls(person_id, day, entry_id, image_name)
        photo.scales.add(toks[3])
        return photo
    from_filename = classmethod(from_filename)

    def get_db_dir(cls):
        db_dir = zkpylons_config.get_path('photocomp_path')
        if not os.path.exists(db_dir):
            os.mkdir(db_dir, 0777)
        return db_dir
    get_db_dir = classmethod(get_db_dir)

    def __repr__(self):
        return "PhotoCompEntry(%r)" % self.filename("orig")


class is_same_person(Predicate):
    message = "matching person id"

    def evaluate(self, environ, credentials):
        person_email = environ.get('REMOTE_USER')
        person_id = environ['pylons.routes_dict'].get('id')

        if person_email is None or person_id is None:
            self.unmet()

        person = Person.find_by_id(person_id, abort_404=False)
        if person is None or person_email != person.email_address:
            self.unmet()

class is_photo_uploader(Predicate):
    message = "uploaded photo"

    def evaluate(self, environ, credentials):
        person_email = environ.get('REMOTE_USER')
        photo_filename = environ['pylons.routes_dict'].get('filename')
        if person_email is None or photo_filename is None:
            self.unmet()

        photo = PhotoCompEntry.from_filename(photo_filename)
        if photo is None:
            self.unmet()

        person = Person.find_by_id(photo.person_id)
        if person is None or person_email != person.email_address:
            self.unmet()

class is_photo_released(Predicate):
    """ Photos are uploaded for a specific day and released once that day has passed. """
    message = "photo released"

    def evaluate(self, environ, credentials):
        photo_filename = environ['pylons.routes_dict'].get('filename')
        if photo_filename is None:
            self.unmet()

        photo = PhotoCompEntry.from_filename(photo_filename)
        if photo is None:
            self.unmet()

        open_date = datetime.strptime(Config.get("date"), "%Y-%m-%dT%H:%M:%S")
        days_open = (date.today() - open_date.date()).days
        if days_open <= photo.day:
            self.unmet()

class PhotocompController(BaseController):

    def index(self):
        day_filter = request.GET.get('day', 'All')
        person_filter = request.GET.get('person', 'All')
        submitted = request.GET.get('s', None)
        randomise = not submitted or 'randomise' in request.GET

        c.DAYS_OPEN = DAYS_OPEN

        c.open_date = datetime.strptime(Config.get("date"), "%Y-%m-%dT%H:%M:%S")
        days_open = (date.today() - c.open_date.date()).days

        photo_db = PhotoCompEntry.read_db()

        photos = [
            photo
            for days in photo_db.values()
            for entries in days
            for photo in entries
            if photo is not None and photo.day < days_open]

        c.no_photos = not photos

        if day_filter and day_filter != 'All':
            photos = [p for p in photos if str(p.day) == day_filter]

        if person_filter and person_filter != 'All':
            photos = [p for p in photos if str(p.person_id) == person_filter]

        if randomise:
            random.shuffle(photos)
        else:
            photos.sort(key=lambda p: (p.day, p.person_id, p.entry_id))

        person_map = {}
        for photo in photos:
            photo.write_scaled()
            person_map[photo.person_id] = None

        c.all_person = []
        for person_id in person_map:
            person = Person.find_by_id(person_id, abort_404=False)
            if person:
                person_map[person_id] = person
                c.all_person.append(person)
        c.all_person.sort(key=lambda person: person.fullname.lower())

        c.photos = photos

        def photo_title(photo):
            return "%s, %s entry %s, %s" % (
                person_map[photo.person_id].fullname,
                (c.open_date + timedelta(photo.day)).strftime('%A'),
                ENTRY_NAMES[photo.entry_id],
                photo.image_name,)

        c.photo_title = photo_title

        field_values = {
            'day':      day_filter,
            'person':   person_filter,
        }

        if randomise:
            field_values['randomise'] = '1'

	if submitted == 'Full Screen' and photos:
            html = render('/photocomp/index-fullscreen.mako')
        else:
            html = render('/photocomp/index.mako')

        return htmlfill.render(html, field_values)

    @ActionProtector(h.auth.Any(is_same_person(), in_group('organiser')))
    def edit(self, id):
        if id is None:
            abort(404)
        print "ID:", type(id), id
        person_id = int(id, 10)
        c.open_date = datetime.strptime(Config.get("date"), "%Y-%m-%dT%H:%M:%S")
        c.days_open = (date.today() - c.open_date.date()).days
        photo_db = PhotoCompEntry.read_db()
        c.photo = lambda day, entry: PhotoCompEntry.get(photo_db, person_id, day, entry)
        c.is_organiser = h.auth.has_group('organiser')
        c.DAYS_OPEN = DAYS_OPEN
        c.ENTRY_NAMES = ENTRY_NAMES
        return render('/photocomp/edit.mako')

    @ActionProtector(h.auth.Any(is_same_person(), in_group('organiser')))
    def upload(self, id):
        if id is None:
            abort(404)
        open_date = datetime.strptime(Config.get("date"), "%Y-%m-%dT%H:%M:%S")
        days_open = (date.today() - open_date.date()).days
        photo_db = PhotoCompEntry.read_db()
        if len(VALID_EXTENSIONS) == 1:
            valid_extensions = VALID_EXTENSIONS[0]
        else:
            valid_extensions = ', '.join(VALID_EXTENSIONS[:-1]) + " or " + VALID_EXTENSIONS[-1]
        #
        # See what photos he has given us.  The an organiser can upload
        # anything without restrictions.
        #
        if h.auth.has_group('organiser'):
            day_range = range(0, DAYS_OPEN)
        else:
            day_range = range(max(days_open, 0), DAYS_OPEN)
        for day in day_range:
            for entry_id in range(len(ENTRY_NAMES)):
                old_photo = PhotoCompEntry.get(photo_db, int(id), day, entry_id)
                photo_field_name = 'photo-%d-%d' % (day, entry_id)
                delete_field_name = 'delete-%d-%d' % (day, entry_id)
                if hasattr(request.POST.get(photo_field_name), 'value'):
                    image_data = request.POST[photo_field_name].value
                    image_name = request.POST[photo_field_name].filename
                    if len(image_data) > MAX_IMAGE_SIZE*1024*1024:
                        error = "%s is larger than %dMib" % (image_name, MAX_IMAGE_SIZE)
                        log.info(error)
                        h.flash(error)
                        continue
                    toks = list(os.path.splitext(os.path.basename(image_name)))
                    if toks[0].upper() == toks[0]:
                        toks[0] = toks[0].lower()
                    toks[1] = toks[1].lower()
                    if not toks[1][1:] in VALID_EXTENSIONS:
                        error = "%s doesn't end in %s." % (image_name, valid_extensions)
                        log.info(error)
                        h.flash(error)
                        continue
                    image_file = cStringIO.StringIO(image_data)
                    try:
                        image = Image.open(image_file)
                        image.load()
                    except:
                        error = "%s doesn't look like a valid image" % image_name
                        log.info(error)
                        h.flash(error)
                        continue
                    if image.format != "JPEG":
                        error = "%s isn't a JPEG image" % image_name
                        log.info(error)
                        h.flash(error)
                        continue
                    new_image_name = toks[0] + toks[1]
                    if old_photo:
                        old_photo.delete(photo_db)
                    new_photo = PhotoCompEntry(int(id), day, entry_id, new_image_name)
                    new_photo.write_orig(image_data)
                    new_photo.add(photo_db)
                elif delete_field_name in request.POST:
                    if old_photo:
                        old_photo.delete(photo_db)
        redirect_to(action="edit", id=id)

    #
    # Return a photo in the database to the client.
    #
    # TODO: Making this the view method, or mapping the view on to this would better match ZK convention
    def photo(self, filename=None):
        if not filename:
            abort(404)
        if "/" in filename or filename.startswith("."):
            abort(403)
        open_date = datetime.strptime(Config.get("date"), "%Y-%m-%dT%H:%M:%S")
        days_open = (date.today() - open_date.date()).days

        try:
            photo = PhotoCompEntry.from_filename(filename)
        except:
            # There are a number of ways that the filename parsing can fail
            # All imply an invalid filename -> file that doesn't exist
            abort(404)

        #
        # If the entries haven't closed for this day then only the logged in
        # person or an organiser can see it.
        #
        id_str = str(photo.person_id)
        if days_open <= photo.day:
            if not h.auth.has_group('organiser') and not h.auth.has_group('photocomp_judge')and photo.person_id != h.auth.get_person_id():
                abort(403)
        #
        # They can have it.
        #
        try:
            # photo.scales will only have one entry in this instance
            # TODO: Should be default parameter...
            handle = open(photo.pathname(tuple(photo.scales)[0]), "rb")
        except EnvironmentError, e:
            if e.errno != errno.ENOENT:
                raise
            abort(404)
        try:
            image_data = handle.read()
        finally:
            handle.close()
        response.headers['Content-type'] = 'image/jpeg'
        return image_data
