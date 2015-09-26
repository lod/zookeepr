<%namespace name="form" file="form_tags.mako" />

<%def name="extended_option(name, options, **attrs)">
  <%doc>
    Render a list of options with an other category for manual entry.
  </%doc>
  <%
    # Name must not contain any whitespace characters
    name.replace(" ", "")

    # Build a list of html attributes from the passed hash
    attr_list = " ".join([k+'="'+attrs[k]+'"' for k in attrs if type(attrs[k]) == "str"])

    # Set the id to match the name - unless it is passed
    # HTML4 states that id must start with A-Z
    # Then contain only A-Z, 0-9, "-", "_", ":" and "."
    # HTML5 states than anything non-whitespace is fine, works IE6+
    id = attrs.get("id", name)
  %>
  <div class="form-group">
    <select id="${id}" name="${name}">
      <option value="">(please select)</option>
      %for s in options:
        <option value="${s}">${ s }</option>
      %endfor
      <option value="other">other</option>
    </select>

    ## TODO: Do we want to show the other text box when no-JS? This will require it to always be visible for them.
    <p class="entries" style="display: none">
      ${ h.text('${name}.text', size=12) }
    </p>
  </div>
  <script>
    // Show the other text input box when required
    // jQuery selector misinterprets . characters in ids, they need to be escaped
    sel_box = jQuery(document.getElementById("${id}"));
    sel_box.on("change", function() {
      jQuery(this).siblings("p").toggle(this.value == "other");
    });

    // Set initial state
    if (sel_box.val() == "other") {
      sel_box.siblings("p").show();
    }
  </script>

</%def>

<h2>Optional</h2>
<table>
  <tr>
    <th>Your favourite shell</th>
    <th>Your favourite editor</th>
    <th>Your favourite distro</th>
    <th>Your favourite vcs</th>
  </tr>
  <tr>
    <td>
      <%self:extended_option name="registration.shell", options="${c.config.get('shells', category='rego')}" />
    </td>
    <td>
      <%self:extended_option name="registration.editor", options="${c.config.get('editors', category='rego')}" />
    </td>
    <td>
      <%self:extended_option name="registration.distro", options="${c.config.get('distros', category='rego')}" />
    </td>
    <td>
      <%self:extended_option name="registration.vcs", options="${c.config.get('vcses', category='rego')}" />
    </td>
  </tr>
</table>

<%form:text name="registration.nick" label="Superhero Name">
  Your IRC nick or other handle you go by.
</%form:text>

%if c.config.get('pgp_collection', category='rego') != 'no':
  <%form:text name="registration.keyid" label="GnuPG/PGP Keyid">
    If you have a GnuPG or PGP key then please enter its short key id here and we will print it on your badge.
  </%form:text>
%endif

<%form:text name="registration.planetfeed" label="Planet Feed">
  If you have a blog and would like it included in the ${ c.config.get('event_name') } planet, please specify an <b>${ c.config.get('event_name') } specific feed</b> to be included. (This is the URL of the RSS feed.)
</%form:text>

<%form:constant label="Description">
  <blockquote class="entries">${ c.silly_description }</blockquote>
  ${ h.hidden('registration.silly_description') }
  ${ h.hidden('registration.silly_description_checksum') }
  This is a randomly chosen description for your name badge
</%form:constant>
