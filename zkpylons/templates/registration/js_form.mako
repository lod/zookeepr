<noscript>
  ## This page assumes javascript
  ## There is a non-js version which should be loaded if they don't have js
  ## So getting here probably means they are playing silly buggers enabling/disabling it
  ## Regardless, send them somewhere that can fix up the cookie state
  ## TODO: build the cookie fixup page, create an override disable js cookie
</noscript>

<script>
<%include file="js_form.script.mako" />
</script>


<p class="note">${ c.config.get('event_pricing_disclaimer') }</p>

<fieldset id="personal" class="form-horizontal">
  <%include file="personal_form.mako" />
</fieldset>

<fieldset id="voucher">
  <%include file="voucher_form.mako" />
</fieldset>

<%
  # Display each product group
  for category in sorted(c.js_categories.values(), key=lambda cat: cat.display_order):
    try:
      tmpl = context.lookup.get_template("/registration/"+category.idname+"_js_form.mako")
    except:
      # No special case template, use default
      tmpl = context.lookup.get_template("/registration/default_js_form.mako")
    products = sorted([c.js_products[x] for x in category.product_ids], key=lambda p:p.display_order)
    tmpl.render_context(context,category=category,products=products)
%>

<!-- Swag section is shown when we have some possible swag, not before -->
<!-- TODO: swag should be inserted at the location of the first use, as per display order -->
<fieldset id="swag_section" style="display:none" class="form-horizontal">
  <h2>Swag</h3>
  <div id="included_swag_lists"></div>
  <div id="additional_swag_list"></div>
  <div id="additional_swag_buttons"></div>
</fieldset>

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
