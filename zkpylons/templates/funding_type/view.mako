<%inherit file="/base.mako" />

<h2>View Funding Type</h2>

<p>
   <b>Name:</b>
    ${ c.funding_type.name }
</p>

<p>
  <b>Active:</b> ${ h.yesno(c.funding_type.active) }
</p>

<p>
   <b>Notify Email:</b>
    ${ c.funding_type.notify_email }
</p>

${ h.link_to('Edit', url=h.url_for(action='edit',id=c.funding_type.id)) } |
${ h.link_to('Back', url=h.url_for(action='index', id=None)) }
