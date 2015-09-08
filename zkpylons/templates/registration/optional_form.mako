<h2>Optional</h2>
<script src="/silly.js"></script>
<table>
  <tr>
    <th>Your favourite shell</th>
    <th>Your favourite editor</th>
    <th>Your favourite distro</th>
    <th>Your favourite vcs</th>
  </tr>
  <tr>
    <td>
      <div class="form-group">
        <select id="registration.shell" name="registration.shell" onchange="toggle_select_hidden(this.id, 'shell_other')">
          <option value="">(please select)</option>
          %for s in c.config.get('shells', category='rego'):
            <option value="${s}">${ s }</option>
          %endfor
          <option value="other">other</option>
        </select>
      </div>

      %if not c.registration or c.registration.shell in c.config.get('shells', category='rego') or c.registration.shell == '':
        <p id="shell_other" class="entries" style="display: none">
      %else:
        <p id="shell_other" class="entries" style="display: inline">
      %endif
          ${ h.text('registration.shelltext', size=12) }
        </p>
    </td>

    <td>
      <div class="form-group">
        <select id="registration.editor" name="registration.editor" onchange="toggle_select_hidden(this.id, 'editor_other')">
          <option value="">(please select)</option>
          %for e in c.config.get('editors', category='rego'):
            <option value="${ e }">${ e }</option>
          %endfor
          <option value="other">other</option>
        </select>
      </div>

      % if not c.registration or c.registration.editor in c.config.get('editors', category='rego') or c.registration.editor == '':
        <p id="editor_other" class="entries" style="display: none">
      % else:
        <p id="editor_other" class="entries" style="display: inline">
      % endif
          ${ h.text('registration.editortext', size=12) }
        </p>
    </td>

    <td>
      <div class="form-group">
        <select id="registration.distro" name="registration.distro" onchange="toggle_select_hidden(this.id, 'distro_other')">
          <option value="">(please select)</option>
          %for d in c.config.get('distros', category='rego'):
            <option value="${ d }">${ d }</option>
          %endfor
          <option value="other">other</option>
        </select>
      </div>

      %if not c.registration or c.registration.distro in c.config.get('distros', category='rego') or c.registration.distro == '':
        <p id="distro_other" class="entries" style="display: none">
      %else:
        <p id="distro_other" class="entries" style="display: inline">
      %endif
          ${ h.text('registration.distrotext', size=12) }
        </p>
    </td>

    <td>
      <div class="form-group">
        <select id="registration.vcs" name="registration.vcs" onchange="toggle_select_hidden(this.id, 'vcs_other')">
          <option value="">(please select)</option>
          %for s in c.config.get('vcses', category='rego'):
            <option value="${s}">${ s }</option>
          %endfor
          <option value="other">other</option>
        </select>
      </div>

      %if not c.registration or c.registration.vcs in c.config.get('vcses', category='rego') or c.registration.vcs == '':
        <p id="vcs_other" class="entries" style="display: none">
      %else:
        <p id="vcs_other" class="entries" style="display: inline">
      %endif
          ${ h.text('registration.vcstext', size=12) }
        </p>
    </td>
  </tr>
</table>

<div class="form-group">
  <label for="registrationnick">Superhero name:</label>
  ${ h.text('registration.nick', size=30) }
  Your IRC nick or other handle you go by.
</div>

%if c.config.get('pgp_collection', category='rego') != 'no':
  <div class="form-group">
    <label for="registrationkeyid">GnuPG/PGP Keyid:</label>
    ${ h.text('registration.keyid', size=10) }
    If you have a GnuPG or PGP key then please enter its short key id here and we will print it on your badge.
  </div>
%endif

<div class="form-group">
  <label for="registrationplanetfeed">Planet Feed:</label>
  ${ h.text('registration.planetfeed', size=50) }
  If you have a blog and would like it included in the ${ c.config.get('event_name') } planet, please specify an <b>${ c.config.get('event_name') } specific feed</b> to be included. (This is the URL of the RSS feed.)
</div>

<div class="form-group">
  <label>Description:</label>
  <blockquote class="entries">${ c.silly_description }</blockquote>
  ${ h.hidden('registration.silly_description') }
  ${ h.hidden('registration.silly_description_checksum') }
  This is a randomly chosen description for your name badge
</div>
