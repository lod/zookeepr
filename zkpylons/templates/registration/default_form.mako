<%page args="category, products"/>
<%namespace name="form" file="form_tags.mako" />

<%form:fieldset category="${category}">
  <%include file="grid_form.mako" args="category=category, products=products" />
</%form:fieldset>
