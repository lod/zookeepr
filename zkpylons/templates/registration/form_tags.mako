## This file defines custom tags for rendering form elements,
## particularly for the registration form.
##
## It is based on an approach documented by zzzeek, the creator of Mako
## http://techspot.zzzeek.org/2008/07/01/better-form-generation-with-mako-and-pylons/

<%! import types %>

<%def name="fieldset(category)">\
  <%doc>
    Render a form fieldset with heading, should be used to wrap a group of entries
  </%doc>\
    <fieldset id="${ category.idname }">
      <h2>${ category.name.title() }</h2>
      ## Some description content include html such as links
      ## Safe - can only be set by admins
      <p class="description">${ category.description |n}</p>
      <input type="hidden" name="${'products.error.' + category.idname}">
      ${ caller.body() }
      %if category.note:
        ## Some notes also include html such as links - safe same as description
        <p class="note">${ category.note | n }</p>
      %endif
    </fieldset>
</%def>

<%!
  def _build_attr_list(**attrs):
    ## Internal helper function to htmlise extra attributes
    ## TODO: Need to strip id out of attrs
    return " ".join([k+'='+str(attrs[k]) for k in attrs if hasattr(attrs[k], '__str__')])
%>

<%def name="text(name, label='', **attrs)">\
  <%doc>
    Render a text input in a form-group container.
  </%doc>\
  <%
    # Name must not contain any whitespace characters
    name.replace(" ", "")

    # Set the id to match the name - unless it is passed
    # HTML4 states that id must be alphanumeric plus a few
    # HTML5 states than anything non-whitespace is fine, works IE6+
    id = attrs.get("id", name)
  %>\
  <div class="form-group">
    ## Should use the html required attribute
    %if attrs.get("mandatory", false):
      <span class="mandatory">*</span>
    %endif
    %if len(label):
      <label for="${name}">${label}:</label>
    %else:
        ## Need a label so that horizontal form lays out ok
        <label for="${name}">&nbsp;</label>
    %endif
    <input type="text" name="${name}" id="${id}" ${ _build_attr_list(**attrs) } />
    ## Optionally allow extra input to be entered here
    ${ caller.body() }
  </div>
</%def>

<%def name="checkbox(name, label='', value=1, checked=False, **attrs)">\
  <%doc>
    Render a checkbox button with text label
    Label can be specified as either a parameter or in the body of the tag
  </%doc>\
  <%
    # Name must not contain any whitespace characters
    name.replace(" ", "")

    # Set the id to match the name - unless it is passed
    # HTML4 states that id must be alphanumeric plus a few
    # HTML5 states than anything non-whitespace is fine, works for IE6+
    id = attrs.get("id", name)

    # Checked is handled specially, controlled by presence not value
    attr_list = _build_attr_list(**attrs)
    if checked:
      attr_list += ' checked'
  %>\
  <div class="checkbox">
    <label>
      <input type="checkbox" value="${value}" name="${name}" id="${id}" ${attr_list}>
      ${label} ${ caller.body() }
    </label>
  </div>
</%def>

<%def name="radio(name, label='', value=1, checked=False, **attrs)">\
  <%doc>
    Render a radio button with text label
    Label can be specified as either a parameter or in the body of the tag
  </%doc>\
  <%
    # Name must not contain any whitespace characters
    name.replace(" ", "")

    # Set the id to match the name - unless it is passed
    # HTML4 states that id must be alphanumeric plus a few
    # HTML5 states than anything non-whitespace is fine, works for IE6+
    id = attrs.get("id", name)

    # Checked is handled specially, controlled by presence not value
    attr_list = _build_attr_list(**attrs)
    if checked:
      attr_list += ' checked'
  %>\
  <div class="radio">
    <label>
      <input type="radio" value="${value}" name="${name}" id="${id}" ${attr_list}>
      ${label} ${ caller.body() }
    </label>
  </div>
</%def>

<%def name="select(name, label='', options=[], **attrs)">
  <%doc>
    Render a basic select box, needs to be fleshed out a bit further to expand use cases.
  </%doc>\
  <div class="form-group">
    <span class="mandatory">*</span>
    <label for="${name}">${label}:</label>
    ${ h.select(name, None, id=name, options=options) }
  </div>
</%def>

<%def name="constant(label, **attrs)">\
  <%doc>
    Render a text constant, such as an un-editable input, in a form-group container.
  </%doc>\
  <div class="form-group">
    <label>${label}:</label>
    ${ caller.body() }
  </div>
</%def>
