<%inherit file="/base.mako" />

<h2>Funding Applications You Haven't Reviewed</h2>

<p>Below is all of the funding applications that you have not yet reviewed. To start, please click "review now".</p>

% for col in c.categories:
<h2 id="${ h.computer_title(col.type.name) }">${ col.type.name } requests (${ len(col.collection) })</h2>

<table class="list">
	<thead>
		<tr>
			<th>ID</th>
			<th>Submitter</th>
			<th>Submission Time</th>
			<th>Number of reviews</th>
			<th>Reviewed?</th>
		</tr>
	</thead>

	<tbody>
		% for s in col.collection:
			<tr>
				<td>
					${ h.link_to(s.id, url=h.url_for(action='view', id=s.id)) }
				</td>
				<td>
					${ h.link_to( s.person.fullname, url=h.url_for(controller='person', action='view', id=s.person.id)) }
				</td>
				<td>
					${ s.creation_timestamp.strftime("%Y-%m-%d&nbsp;%H:%M") |n}
				</td>
				<td align="right">
					${ len(s.reviews) }
				</td>
				<td>
					% if col.min_reviews < 3 and len(s.reviews) > col.min_reviews :
						<small>
							Review something with ${ col.min_reviews } reviews first;
							${ h.link_to("review anyway", url=h.url_for(action="review", id=s.id)) }
						</small>
					% else:
						${ h.link_to("Review!", url=h.url_for(action="review", id=s.id)) }
					% endif
				</td>
			</tr>
		% endfor col.collection
	</tbody>
</table>

<br>

% endfor proposal types

<%def name="title()" >
	Funding Applications you haven't reviewed - ${ parent.title() }
</%def>

<%def name="contents()">
<%
	menu = ''
	for ft in c.funding_types:
		menu += '<li><a href="#%s">%s  requests</a></li>' % (h.computer_title(ft.name), ft.name)
	return menu
%>
</%def>

