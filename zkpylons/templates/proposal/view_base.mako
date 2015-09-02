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
  <table>
    <tr>
      <th># - Reviewer</th>
      <th>Score</th>
      %if len(c.streams) > 1:
        <th>Rec. Stream</th>
      %endif
      <th>Comment</th>
      <th>Private Comment</th>
    </tr>
    % for r in c.proposal.reviews:
      <tr class="${ h.cycle('even', 'odd') }, review_score">
        <td style="vertical-align: top;">
          ${ h.link_to("%s - %s %s" % (r.id, r.reviewer.firstname, r.reviewer.lastname), url=h.url_for(controller='review', id=r.id, action='view')) }
        </td>
        <td style="vertical-align: top;">
          ${ r.score }
        </td>
        % if len(c.streams) > 1:
          <td style="vertical-align: top;">
            % if r.stream is not None:
              ${ r.stream.name }
            % else:
              (none)
            % endif
          </td>
        % endif
        <td style="vertical-align: top;">
          ${ r.comment | h.line_break}
        </td>
        <td style="vertical-align: top;">
          ${ r.private_comment | h.line_break}
        </td>
      </tr>
    % endfor
    <tr class="review_score">
      <td colspan="${ 4 + (len(c.streams) > 1) }" style="text-align: center">
        <a id="hide_reviews">Hide other reviews</a>
      </td>
    </tr>
    <tr id="reviews_hidden" style="display: none">
      <td colspan="${ 4 + (len(c.streams) > 1) }" style="text-align: center">
        Reviews are hidden - <a id="show_reviews">show</a>
      </td>
    </tr>
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
      jQuery("tr.review_score").show();
      jQuery("tr#reviews_hidden").hide();
    }
    function hide_reviews() {
      document.cookie = "review_scores=hide"
      jQuery("tr.review_score").hide();
      jQuery("tr#reviews_hidden").show();
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
