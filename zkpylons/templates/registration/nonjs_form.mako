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
      context.write("NOT FOUND: "+h.computer_title(category.name)+"_form.mako"); # TODO: Handle new product groups
    else:
      all_products = category.available_products(c.signed_in_person, stock=False)
      products = [x for x in all_products if c.product_available(x, stock=False)]
      products.sort(key=lambda p: p.display_order)
      if len(products) > 0:
        tmpl.render_context(context,category=category,products=products)
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

##<div style="background: white; border: 2px solid; position: fixed; right: 0; margin-right: 20px; width: 150px; top:150px; ">
<fieldset>
  <h2 style="text-align: center">Price</h2>
  <table id="price_tally">
    <thead>
      <tr>
        <th>Description</th>
        <th>Qty</th>
        <th>Price</th>
        <th>Total</th>
      </tr>
    </thead>
    <tbody>
    </tbody>
    <tfoot>
      <td>&nbsp;</td>
      <td>&nbsp;</td>
      <th>Total</th>
      <td id="price_total">$0.00</td>
    </tfoot>
  </table>
</fieldset>
