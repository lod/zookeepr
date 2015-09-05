import pytest
from mock import MagicMock, patch

from pylons import request, tmpl_context
import zkpylons.controllers.schedule as schedule


class TestSchedule(object):

    def test_view_talk(self, monkeypatch):
        # c.day = request.get['day'] or 'all'
        # c.talk = Proposal(id) on success
        # c.talk_id = id on failure
        # c.webmaster_email = Config.get('webmaster_email')
        # returns render /schedule/table_view.mako on success
        # returns render /schedule/invalid_talkid.mako on failure

        class myreq:
            def __init__(self):
                self.GET = {}

        class status_stub:
            def __init__(self, status_str):
                self.name = status_str

        class proposal_stub:
            def __init__(self, status_str):
                self.status = status_stub(status_str)

        # Weird magical stacked thread objects, have to be initialised
        request._push_object(myreq())
        tmpl_context._push_object(myreq())

        monkeypatch.setattr(schedule.Config, 'get', MagicMock(return_value="mocked config"))
        proposal_find = MagicMock()
        monkeypatch.setattr(schedule.Proposal, 'find_by_id', proposal_find)

        render = MagicMock(return_value="mocked render")
        monkeypatch.setattr(schedule, 'render', render)

        # Sucessful finding of proposal
        monkeypatch.setattr(schedule.request, 'GET', {'day':'Tomorrow'})
        proposal_find.return_value = proposal_stub('Accepted')
        sched = schedule.ScheduleController()
        assert sched.view_talk(23) == "mocked render"
        # Success
        assert render.call_args == (('/schedule/table_view.mako',),{})
        # Context set correctly
        assert schedule.c.talk == proposal_find.return_value
        assert schedule.c.day == "Tomorrow"

        # Failure to find proposal
        monkeypatch.setattr(schedule.request, 'GET', {}) # No day
        proposal_find.return_value = None
        assert sched.view_talk(21) == "mocked render"
        # Failure
        assert render.call_args == (('/schedule/invalid_talkid.mako',),{})
        # Context set correctly
        assert schedule.c.day == "all"
        assert schedule.c.talk_id == 21
        assert schedule.c.webmaster_email == "mocked config"

        # Found incorrect proposal state
        monkeypatch.setattr(schedule.request, 'GET', {'day':'Yesterday'})
        proposal_find.return_value = proposal_stub('Withdrawn')
        assert sched.view_talk(13) == "mocked render"
        # Failure
        assert render.call_args == (('/schedule/invalid_talkid.mako',),{})
        # Context set correctly
        assert schedule.c.day == "Yesterday"
        assert schedule.c.talk_id == 13
        assert schedule.c.webmaster_email == "mocked config"
