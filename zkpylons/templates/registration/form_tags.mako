<%def name="text(name, label, **attrs)">\
  <%doc>
    Render a text input in a form-group container.
  </%doc>\
  <%
    # Name must not contain any whitespace characters
    name.replace(" ", "")

    # Build a list of html attributes from the passed hash
    attr_list = " ".join([k+'="'+attrs[k]+'"' for k in attrs if type(attrs[k]) == "str"])

    # Set the id to match the name - unless it is passed
    # HTML4 states that id must start with A-Z
    # Then contain only A-Z, 0-9, "-", "_", ":" and "."
    # HTML5 states than anything non-whitespace is fine, works IE6+
    if attrs.get("id") == None:
      id = name
      attr_list += ' id="'+name+'"'
    else:
      id = attrs["id"]
  %>

  <div class="form-group">
    %if attrs.get("mandatory", false):
      <span class="mandatory">*</span>
    %endif
    <label for="${name}">${label}:</label>
    <input type="text" name="${name}" ${attr_list} />
    ## Optionally allow extra input to be entered here
    ${ caller.body() }
  </div>
</%def>

<%def name="constant(label, **attrs)">\
  <%doc>
    Render a text constant, such as an un-editable input, in a form-group container.
  </%doc>\
  <%
    # Build a list of html attributes from the passed hash
    attr_list = " ".join([k+'="'+attrs[k]+'"' for k in attrs if type(attrs[k]) == "str"])
  %>

  <div class="form-group">
    <label>${label}:</label>
    ${ caller.body() }
  </div>
</%def>
