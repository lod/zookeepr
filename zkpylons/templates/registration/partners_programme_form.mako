<%page args="category, products"/>
<%namespace name="form" file="form_tags.mako" />

<%form:fieldset category="${category}">
  <div id="partner_details">
    <%include file="grid_form.mako" args="category=category, products=products" />
    <%include file="partners_programme_extra_form.mako" args="category=category, products=products" />
  </div>
</%form:fieldset>

