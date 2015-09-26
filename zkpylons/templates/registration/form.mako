<p class="note">${ c.config.get('event_pricing_disclaimer') }</p>

<fieldset id="personal" class="form-horizontal">
  <%include file="personal_form.mako" />
</fieldset>

<fieldset id="voucher">
  <%include file="voucher_form.mako" />
</fieldset>

<%
  # Display each product group
  for category in c.product_categories: # Ordered by display order
    try:
      tmpl = app_globals.mako_lookup.get_template("/registration/"+h.computer_title(category.name)+"_form.mako")
    except:
      # No special case template, use default
      tmpl = context.lookup.get_template("/registration/default_form.mako")
    tmpl.render_context(context,category=category,products=category.valid_products)
%>

<fieldset>
  <%include file="further_information_form.mako" />
</fieldset>

%if c.config.get('lca_optional_stuff', category='rego') == 'yes':
  <fieldset>
    <%include file="optional_form.mako" />
  </fieldset>
%endif

<fieldset>
  <%include file="subscriptions_form.mako" />
</fieldset>

%if c.signed_in_person.is_speaker():
  <fieldset>
    <%include file="speaker_form.mako" />
  </fieldset>
%endif
