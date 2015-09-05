<%inherit file="/base.mako" />

<%def name="title()" >
Reviews - ${ parent.title() }
</%def>

<%def name="contents()">
% for group in c.groups:
  <li><a href="#${group.simple_name}">${group.name} proposals</a></li>
% endfor
</%def>

<script language="Javascript">

h_show = function () { jQuery(this).find("div").show() };
h_hide = function () { jQuery(this).find("div").hide() };

jQuery(document).ready(function() {
  jQuery('.proposals td').not('.person').hover(h_show, h_hide)
  jQuery('.proposals td.person > div').hover(h_show, h_hide)
});

</script>

<style type="text/css">

td.score { text-align: center }
td.person > div { display: inline }

</style>


<h2>Review Summary</h2>

% for group in c.groups:

  <a name="${ group.simple_name }"></a>
  <h2>${ group.name } proposals</h2>

  <table class="zebra proposals">
    <tr>
      <th>#</th>
      <th>Proposal</th>
      <th>Submitters</th>
      <th>Avg Score</th>
      <th>Reviewers</th>
      <th>Winning Stream</th>
    </tr>

    % for proposal in group.proposals:
    <tr>
      <td>
        ${ h.link_to(proposal.id, url=h.url_for(controller='proposal', action='view', id=proposal.id)) }
      </td>
      <td>
        ${ h.link_to(proposal.title, url=h.url_for(controller='proposal', action='view', id=proposal.id)) }
        <div class="large_popup">
          <strong>Abstract:</strong>
          <p>${ proposal.abstract | h.line_break}</p>
        </div>
      </td>
      <td class='person'>
        % for person in proposal.people:
          <div>
            ${ person.fullname },
            <div id="${ "bio%s" % person.id }" class="large_popup">
              ${ person.fullname }
              <br>
              <strong>Bio:</strong>
              <p>${ person.bio }</p>
              <strong>Experience:</strong>
              <p> ${person.experience }</p>
            </div>
          </div>
        % endfor
      </td>
      <td class='score'>
        % if proposal.status == c.pending_status:
          % if proposal.average_score is None:
            <b>No Reviews</b>
          % else:
            ${ "%0.2f" % proposal.average_score }
            <div class="small_popup">
              % for review in proposal.reviews:
                ${ review.reviewer.fullname }:  ${ review.score }
                <br>
              % endfor
            </div>
          % endif
        % else:
          ${ proposal.status.name }
        % endif
      </td>
      <td>
        % for review in proposal.reviews:
          ${ h.link_to(review.reviewer.fullname, url=h.url_for(controller='review', action='view', id=review.id)) }, 
%         if review.comment or review.private_comment:
            <div class="small_popup">
              <b>${ review.reviewer.fullname } Comments:</b> ${ review.comment }<br />
              <br>
              <b>${ review.reviewer.fullname } Private Comments:</b> ${ review.private_comment }
            </div>
          % endif
        % endfor
      </td>

<%
    streams = {}
    for review in proposal.reviews:
      if review.stream is not None:
        streams[review.stream.name] = streams.get(review.stream.name, 0) + 1

    highest_stream_score = max(streams.values() or [0])
    highest_streams = [k for k,v in streams.items() if v == highest_stream_score]
    if len(highest_streams) > 1:
      highest_stream = "TIE"
    elif len(highest_streams) == 0:
      highest_stream = "None"
    else:
      highest_stream = highest_streams[0]
%>

      <td>
        ${ highest_stream } (${ highest_stream_score })
        % if streams:
          <div class="large_popup">
            % for stream, score in streams.items():
              ${ stream } : ${ str(score) }
              <br>
            % endfor
          </div>
        % endif
      </td>
    </tr>
    % endfor group.proposals
  </table>
% endfor c.groups
