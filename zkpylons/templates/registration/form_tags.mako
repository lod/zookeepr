<%! import types %>
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

    # Build a list of html attributes from the passed hash
	## TODO: Need to strip id out of attrs
    attr_list = " ".join([k+'='+str(attrs[k]) for k in attrs if hasattr(attrs[k], '__str__')])
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
    <input type="text" name="${name}" id="${id}" ${attr_list} />
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

    # Build a list of html attributes from the passed hash
    attr_list = " ".join([k+'='+str(attrs[k]) for k in attrs if hasattr(attrs[k], '__str__')])

    # Checked is handled specially, controlled by presence not value
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

    # Build a list of html attributes from the passed hash
    attr_list = " ".join([k+'='+str(attrs[k]) for k in attrs if hasattr(attrs[k], '__str__')])

    # Checked is handled specially, controlled by presence not value
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

<%def name="constant(label, **attrs)">\
  <%doc>
    Render a text constant, such as an un-editable input, in a form-group container.
  </%doc>\
  <div class="form-group">
    <label>${label}:</label>
    ${ caller.body() }
  </div>
</%def>
