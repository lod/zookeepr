<%namespace name="form" file="form_tags.mako" />

<h2>Subscriptions</h2>
<p class="note">Tick below to sign up for any of the following:</p>

<%form:checkbox name="registration.signup.linuxaustralia">
  membership with Linux Australia <a href="http://www.linux.org.au/" target="_blank">(read more)</a>
</%form:checkbox>

<%form:checkbox name="registration.signup.announce">
  the low traffic <b>${ c.config.get('event_name') }  announcement list</b>
</%form:checkbox>

<%form:checkbox name="registration.signup.chat">
  the <b>${ c.config.get('event_name') } attendees list</b>
</%form:checkbox>
