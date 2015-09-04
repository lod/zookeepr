<%namespace name="toolbox" file="/leftcol/toolbox.mako"/>
<%inherit file="/base.mako" />
<% c.signed_in_person = h.signed_in_person() %>
<%
  if h.auth.authorized(h.auth.has_organiser_role):
    allow_edit = True
  elif c.signed_in_person in c.proposal.people:
    if c.proposal_editing == 'open':
      allow_edit = True
    elif h.auth.authorized(h.auth.has_late_submitter_role):
      allow_edit = True
    else:
      allow_edit = False
  else:
    allow_edit = False
%>

<%def name="toolbox_extra()">
  % if allow_edit:
    ${ toolbox.make_link('Edit Proposal', url=h.url_for(controller='proposal', action='edit', id=c.proposal.id)) }
  % endif 
</%def>

<%def name="toolbox_extra_reviewer()">
  ${ toolbox.make_link('Review this proposal', url=h.url_for(action='review')) }
</%def>

<%def name="heading()">
  ${ c.proposal.title }
</%def>

<% c.signed_in_person = h.signed_in_person() %>

<h2>${ self.heading() }</h2>

% if c.proposal.type.name == 'Miniconf':
  <%include file="view_fragment_miniconf.mako" />
% else:
  <%include file="view_fragment.mako" />
% endif

% if allow_edit:
  ${ toolbox.make_link('Edit Proposal', url=h.url_for(controller='proposal', action='edit',id=c.proposal.id)) }
% endif

% if h.auth.authorized(h.auth.Or(h.auth.has_organiser_role, h.auth.has_reviewer_role, h.auth.has_proposals_chair_role)):
  % if len(c.duplicates):
    <h3>Possible duplicates</h3>
    <table id="duplicates">
      <tr>
        <th>Submitters</th>
        <th>Title</th>
      </tr>
      % for dup in c.duplicates:
        <tr>
			<td>${ ", ".join([h.link_to(
					x.fullname or x.id,
					url=h.url_for(controller='person', id=x.id)
				) for x in dup.people]) |n}</td>
			<td>${ h.link_to(dup.title, url=h.url_for(controller='proposal',id=dup.id)) }</td>
        </tr>
      % endfor
    </table>
  % endif
% endif


% if h.auth.authorized(h.auth.Or(h.auth.has_organiser_role, h.auth.has_reviewer_role, h.auth.has_proposals_chair_role)):
  <table class="review_scores">
    % for r in c.proposal.reviews:
      <tbody>
        <tr>
          <th>Reviewer</th>
          <td>
            ${ h.link_to(r.reviewer.fullname, url=h.url_for(controller='review', id=r.id, action='view')) }
          </td>
          <th>Score</th>
          <td>
            % if r.score:
              ${ r.score }
            % else:
              &mdash;
            % endif
          </td>
          % if len(c.streams) > 1:
            <th>Rec. Stream</th>
            <td>
              % if r.stream is not None:
                ${ r.stream.name }
              % else:
                (none)
              % endif
            </td>
          % endif
        </tr>
        <tr>
          <th>Comment</th>
          <td colspan="${ 3 + 2*(len(c.streams) > 1) }">
            ${ r.comment | h.line_break}
          </td>
        </tr>
        <tr>
          <th>Private Comment</th>
          <td colspan="${ 3 + 2*(len(c.streams) > 1) }">
            ${ r.private_comment | h.line_break}
          </td>
        </tr>
      </tbody>
    % endfor
    <tfoot>
      <tr>
        <td colspan="${ 4 + 2*(len(c.streams) > 1) }" style="text-align: center">
          <a id="hide_reviews">Hide other reviews</a>
        </td>
      </tr>
      <tr id="reviews_hidden" style="display: none">
        <td colspan="${ 4 + 2*(len(c.streams) > 1) }">
          Reviews are hidden - <a id="show_reviews">show</a>
        </td>
      </tr>
    </tfoot>
  </table>
  <style type="text/css">
    /* Anchor without href uses text cursor by default */
    a#hide_reviews, a#show_reviews { cursor:pointer; }
  </style>
  <script>
    /* Reviewers report that they find it distracting to be thinking of a score
     * while being confronted with all the other scores, the pressure to be
     * conformist is probably distorting the review results.
     *
     * Yet later it is vital that these scores be easily visible.
     *
     * So we hide the scores by default but provide a button to show them.
     * The button selection is stored so that it is persistent across pages.
     * We also fallback to showing scores if javascript is disabled.
     *
     * Note: The positioning of the script tag is a bit of a hack, we can
     * assume that the dom we care about is loaded without waiting for the
     * rest of the page. This help minimise the flash before we override the
     * display state.
     */
    function show_reviews() {
      document.cookie = "review_scores=show"
      jQuery("table.review_scores tbody").show();
      jQuery("#hide_reviews").parents("tr").show();
      jQuery("#show_reviews").parents("tr").hide();
    }
    function hide_reviews() {
      document.cookie = "review_scores=hide"
      jQuery("table.review_scores tbody").hide();
      jQuery("#hide_reviews").parents("tr").hide();
      jQuery("#show_reviews").parents("tr").show();
    }
    jQuery("#show_reviews").click(show_reviews);
    jQuery("#hide_reviews").click(hide_reviews);
    // Test for show state in cookie list
    if (/(?:^|;\s*)review_scores=show\s*(?:;|$)/.test(document.cookie)) {
      show_reviews();
    } else {
      hide_reviews();
    }
  </script>
% endif

${ next.body() }
