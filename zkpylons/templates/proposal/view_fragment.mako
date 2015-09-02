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
