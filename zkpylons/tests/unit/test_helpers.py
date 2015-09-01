import unittest

import zkpylons.lib.helpers as h
import markupsafe

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
