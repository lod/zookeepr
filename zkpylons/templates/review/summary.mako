<%inherit file="/base.mako" />

<%def name="title()" >
Summary of Reviewers - ${ parent.title() }
</%def>

<h2>Summary of Reviewers</h2>

<table>
  <tr>
    <th>Reviewer</th>
    <th>Reviews</th>
    <th>Declined</th>
%   if c.show_average:
      <th>Avg Score</th>
%   endif
  </tr>
% for entry in c.reviewers:
    <tr>
      <td>${ entry.reviewer }</td>
      <td>${ entry.reviewed }</td>
      <td>${ entry.declined }</td>
%     if c.show_average:
        <td>${ "%#.2f" % entry.average }</td>
%     endif
    </tr>
% endfor
</table>
