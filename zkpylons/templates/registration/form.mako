<script type="text/javascript">
  function ticketWarning(tickettype){
  var str=/student/i;
    if(tickettype.match(str)){
      jQuery('#warningDiv').slideDown(1000);
    }
    else{
      jQuery('#warningDiv').slideUp(1000);
    }
  }
  function showRocketWarning(){
    jQuery('#rocket_warning').slideDown(1000);
    jQuery("#rocket_see_note").show();
  }
</script>

<p class="note">${ c.config.get('event_pricing_disclaimer') }</p>

<fieldset id="personal" class="form-horizontal">
  <%include file="personal_form.mako" />
</fieldset>

<fieldset id="voucher">
  <%include file="voucher_form.mako" />
</fieldset>

%for category in c.product_categories:
  <%
    all_products = category.available_products(c.signed_in_person, stock=False)
    products = [x for x in all_products if c.product_available(x, stock=False)]
  %>
  %if len(products) > 0:
    <fieldset id="${ h.computer_title(category.name) }">
      <h2>${ category.name.title() }</h2>
      <p class="description">${ category.description |n}</p>
      <input type="hidden" name="${'products.error.' + category.clean_name()}">
      ## Manual category display goes here:
      %if category.display_mode == 'shirt':
        <%include file="shirt_form.mako" args="category=category, products=products" />
      %elif category.display_mode == 'miniconf':
        <%include file="miniconf_form.mako" args="category=category, products=products" />
      %elif category.display_mode == 'accommodation':
        <%include file="accommodation_form.mako" args="category=category, products=products" />
      %elif category.display_mode == 'grid':
        <%include file="grid_form.mako" args="category=category, products=products" />
      %elif category.display == 'radio':
        <%include file="radio_form.mako" args="category=category, products=products" />
      %elif category.display == 'select':
        <%include file="select_form.mako" args="category=category, products=products" />
      %elif category.display == 'checkbox':
        <%include file="checkbox_form.mako" args="category=category, products=products" />
      %elif category.display == 'qty':
        <%include file="qty_form.mako" args="category=category, products=products" />
      %endif

      %if category.name == 'Accommodation':
        <%include file="accommodation_name_form.mako" args="category=category, products=products" />
      %elif category.name == "Partners' Programme":
        <%include file="partner_form.mako" args="category=category, products=products" />
      %endif

      %if category.note:
        <p class="note">${ category.note | n }</p>
      %endif
    </fieldset>
  %endif
%endfor

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
