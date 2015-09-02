<% import urllib %>

<%def name="title()">
  ${ h.truncate(c.proposal.title) } - ${ c.proposal.type.name } proposal - ${ parent.title() }
</%def>

<%def name="allow(b)"><%
  return 'I allow' if b else 'I DO NOT allow'
%></%def>

<%def name="http_prepend(url)">
  ## FIXME: I reckon this should go into the helpers logic
  % if '://' in url:
    <a href="${ url }">${ url }</a>
  % else:
    <a href="http://${ url }">${ url }</a>
  % endif
</%def>


<%def name="google(title, query)">
  ${ h.link_to(title, url='http://google.com/search?q=%s' % urllib.quote_plus(query)) }
</%def>


<div id="proposal">

<p class="submitted">
  Proposal for a
  ${ c.proposal.type.name } 
  submitted by
  % for p in c.proposal.people:
    ${ p.fullname } &lt;${ p.email_address }&gt;
  % endfor
  at
  ${ c.proposal.creation_timestamp.strftime("%Y-%m-%d&nbsp;%H:%M") | n}
  <br />
  (last updated at ${ c.proposal.last_modification_timestamp.strftime("%Y-%m-%d&nbsp;%H:%M") | n})
</p>

% if c.proposal.type.name:
  <p class="url">
    <em>Proposal Type:</em>
    ${ c.proposal.type.name }
  </p>
% endif

<div class="abstract">
  <p>
    <em>Abstract:</em>
  </p>
  <blockquote>
    <p>${ c.proposal.abstract | h.line_break}</p>
  </blockquote>
</div>

<div class="private_abstract">
  <p>
    <em>Private Abstract:</em>
  </p>
  <blockquote>
    <p>${ c.proposal.private_abstract | h.line_break}</p>
  </blockquote>
</div>

% if c.proposal.technical_requirements:
  <div class="technical_requirements">
    <p>
      <em>Technical Requirements:</em>
    </p>
    <blockquote>
      <p>${ c.proposal.technical_requirements | h.line_break}</p>
    </blockquote>
  </div>
% endif

% if c.proposal.audience.name:
  <p class="url">
    <em>Target Audience:</em>
    ${ c.proposal.audience.name }
  </p>
% endif


% if c.proposal.project:
  <p class="url">
    <em>Project:</em>
    ${ c.proposal.project }
  </p>
% endif

% if c.proposal.url:
  <p class="url">
    <em>URL:</em>
    ${ http_prepend(c.proposal.url) }
  </p>
% endif

% if c.proposal.abstract_video_url:
  <p class="video">
    <em>Video Abstract:</em>
    ${ http_prepend(c.proposal.abstract_video_url) }
  </p>
% endif


% for person in c.proposal.people:
  <h2>${ person.fullname } </h2>
  % if h.auth.authorized(h.auth.Or(h.auth.has_organiser_role, h.auth.has_reviewer_role, h.auth.has_proposals_chair_role)):
    <p class="submitted">
      ${ person.fullname } &lt;${ person.email_address }&gt;
      % if person.url is not None and len(person.url) > 0:
        <a href="${ person.url}">Speaker's Homepage</a>
      % endif
      <br>
      ${ h.link_to('(view details)', url=h.url_for(controller='person', action='view', id=person.id)) }
      ${ google('(stalk on Google)', " ".join(filter(None, [person.fullname, person.email_address]))) }
      ${ google('(linux specific stalk)', " ".join(filter(None, ["linux", person.fullname, person.email_address]))) }
      ${ google('(email only stalk)', person.email_address) }
    </p>
  % endif
  <div class="bio">
    <p><em>Bio:</em></p>
    <blockquote><p>
      % if person.bio:
        ${ person.bio | h.line_break}
      % else:
        [none provided]
      % endif
    </p></blockquote>
  </div>

  <div class="experience">
    <p><em>Experience:</em></p>
    <blockquote><p>
      % if person.experience:
        ${ person.experience | h.line_break}
      % else:
        [none provided]
      % endif
    </p></blockquote>
  </div>
% endfor

<div class="attachment">
  <p><em>Attachments:</em></p>
  % if len(c.proposal.attachments) > 0:
    <table>
      <tr>
        <th>Filename</th>
        <th>Size</th>
        <th>Date uploaded</th>
        <th>&nbsp;</th>
      </tr>
      % for a in c.proposal.attachments:
        <tr class="${ h.cycle('even', 'odd') }">
          <td>
            ${ h.link_to(h.util.html_escape(a.filename), url=h.url_for(controller='attachment', action='view', id=a.id)) }
          </td>
          <td>
            % if len(a.content) >= (1024*1024):
              ${ round(len(a.content)/1024.0/1024.0, 1) } MB
            % elif len(a.content) >= (1024):
              ${ round(len(a.content)/1024.0, 1) } kB
            % else:
              ${ len(a.content) } B
            % endif
          </td>
          <td>
            ${ a.creation_timestamp.strftime("%Y-%m-%d %H:%M") }
          </td>
          <td>
            ${ h.link_to('delete', url=h.url_for(controller='attachment', action='delete', id=a.id)) }
          </tr>
      % endfor
    </table>
  % endif

  % if c.signed_in_person in c.proposal.people or ('organiser' in [x.name for x in c.signed_in_person.roles]):
    <p>
      ${ h.link_to('Add an attachment', url=h.url_for(action='attach')) }
    </p>
  % endif
</div>

% if c.cfp_hide_assistance_info == 'no':
  <div id="assistance">
    % if c.proposal.accommodation_assistance:
      <p>
        <em>Accommodation assistance:</em> ${ c.proposal.accommodation_assistance.name }
      </p>
    % endif
    % if c.proposal.travel_assistance:
      <p>
        <em>Travel assistance:</em> ${ c.proposal.travel_assistance.name }
      </p>
    % endif
    <p><a id="hide_assistance">Hide assistance</a></p>
  </div>
  <div id="assistance_hidden" style="display: none">
    <p>Assistance is hidden - <a id="show_assistance">show</a></p>
  </div>
  <style type="text/css">
    /* Anchor without href uses text cursor by default */
    a#hide_assistance, a#show_assistance { cursor:pointer; }
  </style>
  <script>
    /* The assistance preferences have been shown to impact the reviewer scores.
     * So for the first pass of reviews we want to hide the assistance preferences.
     * Later the assistance can be shown for the final decisions.
     *
     * c.cfp_hide_assistance_info specifies that assistance shouldn't be an option
     * offered to people, in that instance we just hide the whole lot.
     *
     * We use cookies so that the preference is persistent, particularly across pages.
     *
     * Note: The positioning of the script tag is a bit of a hack, we can
     * assume that the dom we care about is loaded without waiting for the
     * rest of the page. This help minimise the flash before we override the
     * display state.
     */
    function show_assistance() {
      document.cookie = "assistance=show"
      jQuery("#assistance").show();
      jQuery("#assistance_hidden").hide();
    }
    function hide_assistance() {
      document.cookie = "assistance=hide"
      jQuery("#assistance").hide();
      jQuery("#assistance_hidden").show();
    }
    jQuery("#hide_assistance").click(hide_assistance);
    jQuery("#show_assistance").click(show_assistance);
    // Set state to match cookie value, hide by default
    // Doing it this way shows assistance as no-js fallback
    if (/(?:^|;\s*)assistance=show\s*(?:;|$)/.test(document.cookie)) {
      show_assistance();
    } else {
      hide_assistance();
    }
  </script>
% endif

<div class="consents">
  <em>Consents:</em>
  <blockquote>
    <p>I allow ${ c.config.get("event_parent_organisation") } to record my talk.</p>

    <p>
      ${ allow(c.proposal.video_release) } ${ c.config.get("event_parent_organisation") } to release any
      recordings of my presentations, tutorials and minconfs under the
      <a href="${ c.config.get("media_license_url") }">${ c.config.get("media_license_name") }</a>
    </p>

    <p>
      ${ allow(c.proposal.slides_release) } ${ c.config.get("event_parent_organisation") } to release
      any other material (such as slides) from my presentations, tutorials and minconfs under the
      <a href="${ c.config.get("media_license_url") }">${ c.config.get("media_license_name") }</a>
    </p>

    % if c.proposal.video_release or c.proposal.slides_release:
      <p>I confirm that I have the authority to allow
        ${ c.config.get("event_parent_organisation") } to release the above material.
        i.e., if your talk includes any information about your employer, or another
        persons copyrighted material, that person has given you authority to
        release this information.
      </p>
    % endif

    % if not c.proposal.video_release or not c.proposal.slides_release:
      <p>
        Please consider allowing us to share both the video of your talk and your
        slides, so that the community can gain the maximum benefit from your
        talk!
      </p>
    % endif
  </blockquote>
</div>

<hr>

</div><!-- id="proposal" -->
