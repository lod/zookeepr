import random
import os
import subprocess
import re

from routes import url_for
from freezegun import freeze_time
from BeautifulSoup import BeautifulSoup

from zkpylons.config import zkpylons_config

from .fixtures import faker, ConfigFactory, CompletePersonFactory, RoleFactory
from .utils import do_login

class TestPhotocompController(object):
    def delete_photos(self):
        """ Delete sample images if they exists. """
        path = zkpylons_config.get_path('photocomp_path')
        if not os.path.exists(path):
            os.mkdir(path, 0777)
        else:
            for f in os.listdir(path):
                os.remove(os.path.join(path, f))

    def create_photos(self, db_session):
        """ Create 500 sample images for testing. """
        path = zkpylons_config.get_path('photocomp_path')
        if not os.path.exists(path):
            os.mkdir(path, 0777)
        else:
            self.delete_photos()

        # Each person can create two entries, id=0,1 per day
        # Easiest to just use two entries on any day
        # We have 125 unique images (5*5*5) so need 63 people
        peeps = [ CompletePersonFactory() for i in range(63) ]
        db_session.commit()

        entry_id = 5 # a number > 1
        current_person = None

        for r in xrange(0,255,60):
            for g in xrange(0,255,60):
                for b in xrange(0,255,60):
                    date_str = "201601%02d" % random.randint(1,4)

                    # Roll through each person, 2 entries each
                    if entry_id >= 1:
                        current_person = peeps.pop()
                        entry_id = 0
                    else:
                        entry_id += 1

                    imagename = "%s%s" % (faker.word(), faker.word())
                    for scale in ('orig', '68x51', '250x250', '1024x768'):
                        filename = "%s-%08d-%d-%s-%s" % (date_str, current_person.id, entry_id, scale, imagename)
                        if scale == 'orig':
                            size = "%dx%d" % (random.randint(100,2000), random.randint(100,2000))
                        else:
                            size = scale
                        os.system('convert -size %s xc:"#%02X%02X%02X" %s.jpg' % (size, r, g, b, os.path.join(path, filename)))



    def test_permissions(self, app, db_session):
        # index - public ok
        # edit - organiser or submitter
        # upload - organiser or submitter
        # photo - public ok
        #    Can only see photos after the comp day has closed, unless organiser or own photo

        # ids correspond to person ids

        pass

    def test_index(self, app, db_session):
        ConfigFactory(key='date', value='2016-01-01T00:00:00')
        db_session.commit()

        # Index shows special error if there are no photo
        self.delete_photos()
        with freeze_time("2016-01-02"):
            resp = app.get(url_for(controller='photocomp', action='index', id=None))
        body = unicode(resp.body, 'utf-8')
        print resp
        assert "Photo Competition" in body
        assert "There are no Photo Competition entries ready for viewing" in body
        assert "There are no entries matching your filter" not in body
        assert 'div id="gallery"' not in body

        # Index shows special error if we filter out all possible photos
        self.create_photos(db_session)
        # Generated photos have person ids 1-1000 # TODO: No longer true
        with freeze_time("2016-01-02"):
            resp = app.get(url_for(controller='photocomp', action='index', id=None, person=1023))
        body = unicode(resp.body, 'utf-8')
        print resp
        assert "Photo Competition" in body
        assert "There are no Photo Competition entries ready for viewing" not in body
        assert "There are no entries matching your filter" in body
        assert 'div id="gallery"' not in body

        # Regular page - no errors
        with freeze_time("2016-01-02"):
            resp = app.get(url_for(controller='photocomp', action='index', id=None, person=None))
        body = unicode(resp.body, 'utf-8')
        print resp
        assert "Photo Competition" in body
        assert "There are no Photo Competition entries ready for viewing" not in body
        assert "There are no entries matching your filter" not in body
        assert 'div id="gallery"' in body

        # There should be a thumbnail for each image linking to the big version
        # Because of the time we set only images from 20160101 are shown
        soup = BeautifulSoup(body)
        links = soup.find(id='gallery').findAll('a')
        #assert len(links) == 125
        link_re = re.compile(r"^/photocomp/photo/ 20160101 - \d{8} - \d{1} - 1024x768 - \w+\.jpg$", re.X)
        img_re  = re.compile(r"^/photocomp/photo/ 20160101 - \d{8} - \d{1} -    68x51 - \w+\.jpg$", re.X)
        title_re = re.compile(r"^\w+ \s \w+, \s \w+ \s entry \s \d, \s \w+.jpg$", re.X)
        for link in links:
            img = link.find('img')
            assert re.match(link_re, link['href']) is not None
            assert re.match(img_re, img['src']) is not None
            assert re.match(title_re, img['title']) is not None

        # There should be combo boxes allowing you to filter by day or submitter
        assert "Person filter" in body
        person_select = soup.find('select', {'name':"person"})
        assert person_select is not None
        assert "Day Filter" in body
        assert len(person_select.findAll('option')) > 1
        day_select = soup.find('select', {'name':"day"})
        assert day_select is not None
        assert len(day_select.findAll('option')) == 5
        assert "Friday" in str(day_select)
        assert "Saturday" in str(day_select)
        assert "Sunday" in str(day_select)
        assert "Monday" in str(day_select)

        # There should be a link to submit new photos
        assert "Submit an entry" in body
        assert '/photocomp/edit' in body


        # End of week page - should have all the images
        # This allows us to do more precise checks on number shown etc.
        with freeze_time("2016-01-08"):
            resp = app.get(url_for(controller='photocomp', action='index', id=None, person=None))
        body = unicode(resp.body, 'utf-8')
        print resp
        assert "Photo Competition" in body
        assert "There are no Photo Competition entries ready for viewing" not in body
        assert "There are no entries matching your filter" not in body
        assert 'div id="gallery"' in body

        # There should be a thumbnail for each image linking to the big version
        soup = BeautifulSoup(body)
        links = soup.find(id='gallery').findAll('a')
        assert len(links) == 125
        link_re = re.compile(r"^/photocomp/photo/ \d{8} - \d{8} - \d{1} - 1024x768 - \w+\.jpg$", re.X)
        img_re  = re.compile(r"^/photocomp/photo/ \d{8} - \d{8} - \d{1} -    68x51 - \w+\.jpg$", re.X)
        title_re = re.compile(r"^\w+ \s \w+, \s \w+ \s entry \s \d, \s \w+.jpg$", re.X)
        for link in links:
            img = link.find('img')
            assert re.match(link_re, link['href']) is not None
            assert re.match(img_re, img['src']) is not None
            assert re.match(title_re, img['title']) is not None

        # There should be combo boxes allowing you to filter by day or submitter
        assert "Person filter" in body
        person_select = soup.find('select', {'name':"person"})
        assert person_select is not None
        assert "Day Filter" in body
        assert len(person_select.findAll('option')) == 64 # 63 people + "All"
        day_select = soup.find('select', {'name':"day"})
        assert day_select is not None
        assert len(day_select.findAll('option')) == 5
        assert "Friday" in str(day_select)
        assert "Saturday" in str(day_select)
        assert "Sunday" in str(day_select)
        assert "Monday" in str(day_select)

        # There should be a link to submit new photos
        assert "Submit an entry" in body
        assert '/photocomp/edit' in body


        # Fullscreen mode runs a javascript slide show
        with freeze_time("2016-01-08"):
            resp = app.get(url_for(controller='photocomp', action='index', id=None, person=None, s="Full Screen"))
        body = unicode(resp.body, 'utf-8')
        print resp
        assert "Photo Competition Full Screen" in body
        assert "There are no Photo Competition entries ready for viewing" not in body
        assert "There are no entries matching your filter" not in body
        assert 'div id="gallery"' in body
        assert "start_slidshow" in body # Matching spelling mistake

        # There should be a thumbnail for each image linking to the big version
        soup = BeautifulSoup(body)
        links = soup.find(id='gallery').findAll('a')
        assert len(links) == 125
        link_re = re.compile(r"^/photocomp/photo/ \d{8} - \d{8} - \d{1} - 1024x768 - \w+\.jpg$", re.X)
        img_re  = re.compile(r"^/photocomp/photo/ \d{8} - \d{8} - \d{1} -    68x51 - \w+\.jpg$", re.X)
        title_re = re.compile(r"^\w+ \s \w+, \s \w+ \s entry \s \d, \s \w+.jpg$", re.X)
        for link in links:
            img = link.find('img')
            assert re.match(link_re, link['href']) is not None
            assert re.match(img_re, img['src']) is not None
            assert re.match(title_re, img['title']) is not None

        # No form boxes
        assert "Person filter" not in body
        person_select = soup.find('select', {'name':"person"})
        assert person_select is None
        assert "Day Filter" not in body
        day_select = soup.find('select', {'name':"day"})
        assert day_select is None

        # There should be a link to submit new photos
        assert "Submit an entry" not in body
        assert '/photocomp/edit' not in body

    def test_edit(self, app, db_session):
        """ Edit page displays a table
            One row per day
            One column per entry allowed
            If an entry has been submitted it is shown
            If that day is open to submission, or you are an organiser
                The entry cells has a file input and delete checkbox
            If it is still possible to add entries a submit button is at the bottom.
            There is explanation text at the top showing the current state.
        """
        ConfigFactory(key='date', value='2016-01-01T00:00:00')
        user = CompletePersonFactory()
        db_session.commit()
        self.delete_photos()

        with freeze_time("2016-01-03 05:00:00"):
            do_login(app, user)
            resp = app.get(url_for(controller='photocomp', action='edit', id=user.id))
        body = unicode(resp.body, 'utf-8')
        soup = BeautifulSoup(body)
        print resp

        assert "Photo Competition Entry Form" in body
        assert "The competition has not opened yet" not in body
        assert "Entries have closed." not in body

        table = soup.find('table')
        assert table is not None

        head = table.find('thead')
        assert head is not None
        assert len(head.findAll('tr')) == 1
        assert len(head.findAll('td')) == 3 # head column + 2 entry rows

        foot = table.find('tfoot')
        assert foot is not None
        assert len(foot.findAll('tr')) == 1
        assert len(foot.findAll('td')) == 2 # head column + full width cell

        rows = table.find('tbody').findAll('tr', recursive=False)
        assert len(rows) == 4 # 4 days of conference
        row_cells = []
        for row in rows:
            print row
            cells = row.findAll('td', recursive=False)
            row_cells.append(cells)
            assert len(cells) == 3 # head column + 2 entry rows
            assert "Not open" not in str(cells[0])
            assert "/images/photocomp-noentry.png" in str(cells[1])
            assert "/images/photocomp-noentry.png" in str(cells[2])

            for cell in cells[1:]:
                checkbox = cell.find('input', {'type':'checkbox'})
                file = cell.find('input', {'type':'file'})
                if "Sunday" in str(cells[0]) or "Monday" in str(cells[0]): # Today/Future
                    assert "Closed" not in str(cells[0])
                    assert "Delete" in str(cell)
                    assert checkbox is not None
                    assert file is not None
                else: # Past
                    assert "Closed" in str(cells[0])
                    assert "Delete" not in str(cell)
                    assert checkbox is None
                    assert file is None

        assert "Friday"   in str(row_cells[0][0])
        assert "Saturday" in str(row_cells[1][0])
        assert "Sunday"   in str(row_cells[2][0])
        assert "Monday"   in str(row_cells[3][0])

        # Upload some images, two for Sunday, one for Monday
        cmd = ["convert", "-size", "500x800", "xc:#FA2030", "jpg:-"]
        gen1 = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout
        cmd = ["convert", "-size", "800x500", "xc:#40FA30", "jpg:-"]
        gen2 = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout
        cmd = ["convert", "-size", "1000x1000", "xc:#4050FA", "jpg:-"]
        gen3 = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout
        print gen3

        upload = [
                ('photo-2-0', 'generated_red.jpg', gen1.read()),
                ('photo-2-1', 'generated_green.jpg', gen2.read()),
                ('photo-3-1', 'generated_blue.jpg', gen3.read()),
        ]

        with freeze_time("2016-01-03 05:00:00"):
            post_resp = resp.form.submit(upload_files=upload)
        # submit actually feeds into the upload function

        assert post_resp.status_code == 302, BeautifulSoup(post_resp.body).find(id="flash")
        assert url_for(controller='photocomp', action='edit', id=user.id) in post_resp.location

        # Upload does not create the resized files - for some reason
        # These are created on retrieval
        path = zkpylons_config.get_path('photocomp_path')
        files = sorted([f for f in os.listdir(path)])
        assert len(files) == 3
        assert files[0] == "20160103-%08d-0-orig-generated_red.jpg"   % user.id
        assert files[1] == "20160103-%08d-1-orig-generated_green.jpg" % user.id
        assert files[2] == "20160104-%08d-1-orig-generated_blue.jpg"  % user.id


    # Named test_photo_func as opposed to test_photo to allow exclusive selection using -k
    def test_photo_func(self, app, db_session):
        """ Photos are accessible by filename if they are in the past
            or uploaded by us
            or we are an organiser
        """

        # Just need a single test image
        ConfigFactory(key='date', value='2016-01-01T00:00:00')
        owner = CompletePersonFactory()
        organiser = CompletePersonFactory(roles=[RoleFactory(name='organiser')])
        judge = CompletePersonFactory(roles=[RoleFactory(name='photocomp_judge')])
        bad_roles = ['team', 'reviewer', 'miniconf', 'proposals_chair', 'late_submitter',
                     'funding_reviewer', 'press', 'miniconfsonly', 'public', 'checkin']
        bad_guy = CompletePersonFactory(roles=[RoleFactory(name=n) for n in bad_roles])
        db_session.commit()
        path = zkpylons_config.get_path('photocomp_path')
        date_str = "20160103"
        entry_id = 0
        scale = 'orig'
        imagename = 'download_test'
        filename = "%s-%08d-%d-%s-%s.jpg" % (date_str, owner.id, entry_id, scale, imagename)
        os.system('convert -size 100x100 xc:"#AABBCC" %s' % (os.path.join(path, filename)))
        file_size = os.path.getsize(os.path.join(path, filename))


        # Future - no login - everything is sweet
        with freeze_time("2016-01-04 05:00:00"):
            resp = app.get('/photocomp/photo/'+filename, headers={'Cookie':''})
        assert resp.content_length == file_size
        assert resp.content_type == "image/jpeg"

        # Past - no login - denied
        with freeze_time("2016-01-01 05:00:00"):
            resp = app.get('/photocomp/photo/'+filename, headers={'Cookie':''}, status=403)

        # Past - owner - good
        with freeze_time("2016-01-01 05:00:00"):
            do_login(app, owner)
            resp = app.get('/photocomp/photo/'+filename)
        assert resp.content_length == file_size
        assert resp.content_type == "image/jpeg"

        # Past - organiser - good
        with freeze_time("2016-01-01 05:00:00"):
            do_login(app, organiser)
            resp = app.get('/photocomp/photo/'+filename)
        assert resp.content_length == file_size
        assert resp.content_type == "image/jpeg"

        # Past - judge - good
        with freeze_time("2016-01-01 05:00:00"):
            do_login(app, judge)
            resp = app.get('/photocomp/photo/'+filename)
        assert resp.content_length == file_size
        assert resp.content_type == "image/jpeg"

        # Past - login, other roles - denied
        with freeze_time("2016-01-01 05:00:00"):
            do_login(app, bad_guy)
            resp = app.get('/photocomp/photo/'+filename, status=403)

        # Non existent filename
        with freeze_time("2016-01-04 05:00:00"):
            resp = app.get('/photocomp/photo/'+'20160103-00000000-0-orig-non_existent_file.jpg', headers={'Cookie':''}, status=404)

        # Bad format filenames
        with freeze_time("2016-01-04 05:00:00"):
            resp = app.get('/photocomp/photo/'+'IamNOTreally.a.file.jpg', headers={'Cookie':''}, status=404)
            resp = app.get('/photocomp/photo/'+'19160103-10000000-12-orig-non_existent_file.jpg', headers={'Cookie':''}, status=404)
            resp = app.get('/photocomp/photo/'+'00160103-10000000-12-orig-non_existent_file.jpg', headers={'Cookie':''}, status=404)
            resp = app.get('/photocomp/photo/'+'1-1-1-orig-non_existent_file.jpg', headers={'Cookie':''}, status=404)
            resp = app.get('/photocomp/photo/'+'----------.jpg', headers={'Cookie':''}, status=404)
            bad_scale_filename = filename.replace('orig', 'haha')
            resp = app.get('/photocomp/photo/'+bad_scale_filename, headers={'Cookie':''}, status=404)

        # Injected paths
        with freeze_time("2100-01-04 05:00:00"): # Future date to ensure all files are old to us
            resp = app.get('/photocomp/photo/'+'../jquery.min.js',          headers={'Cookie':''}, status=404)
            resp = app.get('/photocomp/photo/'+'../jquery.min.js',          headers={'Cookie':''}, status=404)
            resp = app.get('/photocomp/photo/'+'///etc/passwd',             headers={'Cookie':''}, status=404)
            resp = app.get('/photocomp/photo/'+'\.\.\/jquery.min.js',       headers={'Cookie':''}, status=404)
            resp = app.get('/photocomp/photo'+'?filename=../jquery.min.js', headers={'Cookie':''}, status=404)
            resp = app.get('/photocomp/photo/',                             headers={'Cookie':''}, status=404)
            resp = app.get('/photocomp/photo',                              headers={'Cookie':''}, status=404)
            # NOTE: none of these actually reach the controller's injection protection, I am not sure what will

        # TODO: Add photocomp_judge to alembic default roles

    def test_upload(self, app, db_session):
        """ Upload files, they then get stored to disk.
            Must be either owner (matching id) or organiser
        """

        ConfigFactory(key='date', value='2016-01-01T00:00:00')
        owner = CompletePersonFactory()
        organiser = CompletePersonFactory(roles=[RoleFactory(name='organiser')])
        db_session.commit()

        self.delete_photos()
        path = zkpylons_config.get_path('photocomp_path')


        # Generate a sample image
        cmd = ["convert", "-size", "100x100", "xc:#FA2030", "jpg:-"]
        img = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read()

        # Try to upload filenames that break things
        upload = [
                ('photo-0-0', 'breaking_samples.jpg', img),
                ('photo-0-1', 'break on spaces.jpeg', img),
                ('photo-1-0', 'try%08%08%08%08%20 %09to%0A%0D%2Fbreak%5c%2Fstuff.jpg', img),
                ('photo-1-1', 'more-dashes-than-asked-for.jpg', img),
                ('photo-2-0', 'some[regex]character\ws.*HAHAHA.jpg', img),
                ('photo-2-1', 'extra.extensions.jpeg.car.bar.jpg', img),
                ('photo-3-0', '\n\t\b\c.jpg', img),
                ('photo-3-1', '\.jpg', img),
        ]

        with freeze_time("2016-01-01 05:00:00"):
            do_login(app, organiser)
            post_resp = app.post(url_for(controller='photocomp', action='upload', id=owner.id), upload_files=upload)

        assert post_resp.status_code == 302
        assert url_for(controller='photocomp', action='edit', id=owner.id) in post_resp.location

        expected_files = [
            '20160101-%08d-0-orig-breaking_samples.jpg' % owner.id,
            '20160101-%08d-1-orig-break on spaces.jpeg' % owner.id,
            ('20160102-%08d' % owner.id) + '-0-orig-try%08%08%08%08%20 %09to%0A%0D%2Fbreak%5c%2Fstuff.jpg',
            '20160102-%08d-1-orig-more-dashes-than-asked-for.jpg' % owner.id,
            '20160103-%08d-0-orig-some[regex]character\ws.*HAHAHA.jpg' % owner.id,
            '20160103-%08d-1-orig-extra.extensions.jpeg.car.bar.jpg' % owner.id,
            '20160104-%08d-0-orig-\n \b\c.jpg' % owner.id,
            '20160104-%08d-1-orig-\.jpg' % owner.id,
        ]
        files = sorted([f for f in os.listdir(path)])
        assert len(files) == len(expected_files)
        for expected in expected_files:
            assert files.pop(0) == expected

        follow_resp = post_resp.follow()
        flash = BeautifulSoup(follow_resp.body).find(id="flash").text
        assert flash == ""

        # Pulling up the edit page triggers the creation of all the different scaled images
        assert len(os.listdir(path)) == len(expected_files)*4



        # Try to upload files which are invalid
        self.delete_photos()

        # Generate a png image to use as rubbish
        cmd = ["convert", "-size", "100x100", "xc:#FA2030", "png:-"]
        png_img = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read()

        # Generate a big image, over 10mb (this is roughly 11mb) to use
        os.system('convert -size 10000x1300 xc: +noise Random  too_big.jpg')

        upload = [
                ('photo-0-0', 'document.txt', img), # Invalid extension
                ('photo-0-1', 'document.jpg.txt', img), # Invalid extension
                ('photo-1-0', '.jpg', img), # Invalid extension
                ('photo-1-1', 'an-image-that-should-work.jpg', img),
                ('photo-2-0', 'empty.jpg', ''), # Not an image
                ('photo-2-1', 'bad_formatted_data.jpg', 'some random string'), # Not an image
                ('photo-3-0', 'too_big.jpg'), # 10mb max image size, this is a real file
                ('photo-3-1', 'sneaky.png.jpg', png_img), # Invalid image type
        ]

        with freeze_time("2016-01-01 05:00:00"):
            do_login(app, organiser)
            post_resp = app.post(url_for(controller='photocomp', action='upload', id=owner.id), upload_files=upload)

        os.remove('too_big.jpg')

        assert post_resp.status_code == 302
        assert url_for(controller='photocomp', action='edit', id=owner.id) in post_resp.location

        expected_files = [
            '20160102-%08d-1-orig-an-image-that-should-work.jpg' % owner.id,
        ]
        files = sorted([f for f in os.listdir(path)])
        assert len(files) == len(expected_files)
        for expected in expected_files:
            assert files.pop(0) == expected

        # Flash is a ul/li list, we just rip the text portions out and concatenate them
        expected_flash = "".join([
                "document.txt doesn't end in jpg or jpeg.",
                "document.jpg.txt doesn't end in jpg or jpeg.",
                ".jpg doesn't end in jpg or jpeg.",
                "empty.jpg doesn't look like a valid image",
                "bad_formatted_data.jpg doesn't look like a valid image",
                "too_big.jpg is larger than 10Mib",
                "sneaky.png.jpg isn't a JPEG image",
        ])

        follow_resp = post_resp.follow()
        flash = BeautifulSoup(follow_resp.body).find(id="flash").text
        assert flash == expected_flash

        # Pulling up the edit page triggers the creation of all the different scaled images
        assert len(os.listdir(path)) == len(expected_files)*4
