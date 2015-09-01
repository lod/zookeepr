<%def name="title()" >
  Proposals you haven't reviewed - ${ parent.title() }
</%def>

<%def name="contents()">
% for group in c.groups:
    <li><a href="#${group.simple_name}">${group.name} proposals</a></li>
% endfor
</%def>

<%inherit file="/base.mako"/>

<h2>Proposals You Haven't Reviewed</h2>

<%
if c.num_reviewers <= 0:
  c.num_reviewers = 1
endif
%>
<p>Below is all of the proposals that you have not yet reviewed. To start, please click "review now".</p>
<p>You have reviewed ${ len(c.person.reviews) } out of your quota of  ${ c.num_proposals * 3 / c.num_reviewers }. </p>

% for group in c.groups:
  <a name="${ group.simple_name }"></a>
  <h2>${ group.name } proposals (${ len(group.proposals) })</h2>

  <table class="list">
    <tr>
      <th>ID - Title</th>
      <th>Submitter(s)</th>
      <th>Submission Time</th>
      <th>Number of reviews</th>
      <th>Reviewed?</th>
    </tr>

%   for proposal in group.proposals:
      <tr class="${ h.cycle('even', 'odd') }">
        <td>
          ${ h.link_to("%s - %s" % (proposal.id, proposal.title), url=h.url_for(action='view', id=proposal.id)) }
        </td>
        <td>
%         for p in proposal.people:
            ${ h.link_to(p.fullname or p.email_address or p.id, url=h.url_for(controller='person', action='view', id=p.id)) }
%         endfor
        </td>
        <td>
          ${ proposal.creation_timestamp.strftime("%Y-%m-%d&nbsp;%H:%M") |n}
        </td>
        <td align="right">
          ${ len(proposal.reviews) }
        </td>
        <td>
%         if group.min_reviews < 3 and len(proposal.reviews) > group.min_reviews :
            <small>
              Review something with ${ group.min_reviews } reviews first;
              ${ h.link_to("review anyway", url=h.url_for(action="review", id=proposal.id)) }
            </small>
%         else:
            ${ h.link_to("Review!", url=h.url_for(action="review", id=proposal.id)) }
%         endif
        </td>
      </tr>
%   endfor group.proposals
  </table>

  <br>
% endfor c.groups
