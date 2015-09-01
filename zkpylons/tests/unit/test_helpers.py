import unittest

import zkpylons.lib.helpers as h
import markupsafe
import re
import urllib

class TestHelpers(unittest.TestCase):
    def setUp(self):
        pass

    def test_line_break(self):
        # Converts line breaks into <br> for HTML output
        # Also interacts with markupsafe to ensure that the <br> tag is not filtered out

        sample = "The small\n black cat \r\n\njumped over \r the\ndog"
        expected = "The small<br> black cat <br><br>jumped over \r the<br>dog"
        assert h.line_break(sample) == expected
        assert markupsafe.escape(h.line_break(sample)) == expected

        sample = "The <a href='blah'>small\n black cat \r\n\njumped"+markupsafe.Markup("<a>")+"over \r the\ndog"
        expected = "The &lt;a href=&#39;blah&#39;&gt;small<br> black cat <br><br>jumped<a>over \r the<br>dog"
        assert markupsafe.escape(h.line_break(sample)) == expected

    def test_url_to_link(self):
        # Converts bbcode [url][/url] to <a href=""></a>

        sample = "A [url=http://jim.com/]with[/url] a lot of [url=ftp://sandy/]random[/url] urls [url=https://google] scattered through[/url]"
        expected = 'A <a href="http://jim.com/">with</a> a lot of <a href="ftp://sandy/">random</a> urls <a href="https://google"> scattered through</a>'
        assert h.url_to_link(sample) == expected
        assert markupsafe.escape(h.url_to_link(sample)) == expected


        sample = "A [url=http://\"messy.url.com/?]<left>right!?bob]with[/url] a lot <br> <a href=\"\">of [url=ftp://sandy/]random[/url] urls [url=https://google] scattered"+markupsafe.Markup("<br>")+markupsafe.Markup("<a>")+"through[/url]"
        expected = 'A <a href="http://%22messy.url.com/?">&lt;left&gt;right!?bob]with</a> a lot &lt;br&gt; &lt;a href=&#34;&#34;&gt;of <a href="ftp://sandy/">random</a> urls <a href="https://google"> scattered<br><a>through</a>'
        assert markupsafe.escape(h.url_to_link(sample)) == expected


