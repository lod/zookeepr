<h2>Subscriptions</h2>
<p class="note">Tick below to sign up for any of the following:</p>

<div class="form-group">
  <label>
    ${ h.checkbox('registration.signup.linuxaustralia') }
    membership with Linux Australia
    <a href="http://www.linux.org.au/" target="_blank">(read more)</a>
  </label>
</div>

<div class="form-group">
  ${ h.checkbox('registration.signup.announce') }
  the low traffic <b>${ c.config.get('event_name') }  announcement list</b>
</div>

<div class="form-group">
  ${ h.checkbox('registration.signup.chat') }
  the <b>${ c.config.get('event_name') } attendees list</b>
</div>
