<noscript>
  ## This page assumes javascript
  ## There is a non-js version which should be loaded if they don't have js
  ## So getting here probably means they are playing silly buggers enabling/disabling it
  ## Regardless, send them somewhere that can fix up the cookie state
  ## TODO: build the cookie fixup page
</noscript>

<%
  from zkpylons.model import ProductCategory, ProductInclude
  import re
  available_products = [x for x in c.products if c.product_available(x, stock=False)]
  simple_products = {p.id:{'id':p.id, 'category':p.category_id, 'active':p.active, 'description':p.description, 'clean_description':p.clean_description(True), 'cost':p.cost} for p in available_products}
  simple_includes = {i.product_id:{} for i in ProductInclude.find_all()}
  for i in ProductInclude.find_all():
    simple_includes[i.product_id][i.include_category_id] = i.include_qty
    simple_categories = {x.id:{'id':x.id, 'name':x.name, 'idname':h.computer_title(x.name), 'description':x.description, 'clean_name':x.clean_name(), 'display_order':x.display_order, 'invoice_free_products':x.invoice_free_products} for x in c.product_categories}
  for cat in simple_categories:
    scategory = ProductCategory.find_by_name(simple_categories[cat]['name'])
    cat_products = scategory.available_products(c.signed_in_person, stock=False)
    simple_categories[cat]['products'] = [x.id for x in cat_products if c.product_available(x, stock=False)]
%>

<script>
  product_categories = ${h.json.dumps(simple_categories)|n};
  product_includes = ${h.json.dumps(simple_includes)|n};
  products = ${h.json.dumps(simple_products)|n};

  function to_id(str) {
    str = str.toLowerCase();
    str = str.replace(/[\s-]/g, "_");
    str = str.replace(/\W/g, "");
    return str;
  }


  // Functions to build product groups
  function build_radio_product_group(cat_id) {
    cat_products = product_categories[cat_id]['products'].map(function(a){return products[a]});
    list = jQuery("<ul>");
    cat_products.forEach(function(p){
      input = jQuery("<input type='radio' value='"+p['id']+"' name='products.category_"+product_categories[cat_id]['clean_name']+"' product_category='"+cat_id+"'>")
      label = jQuery("<label>"+p['description']+" - $"+parseFloat(p['cost']/100).toFixed(2)+"</label>");
      list.append(jQuery("<li>").append(label.prepend(input)));
    });
    return list;
  }

  function build_product_group(cat_id) {
    cat = product_categories[cat_id];
    fset = jQuery("<fieldset id='"+cat['idname']+"'></fieldset>");
    fset.append("<h2>"+cat['name']+"</h2>");
    fset.append("<p>"+cat['description']+"</p>");
    return fset;
  }


  // Functions to manage the swag list
  function load_product_group(category, target) {
    cat_products = product_categories[category]['products'].map(function(a){return products[a]});
    select = jQuery("<select>");
    cat_products.forEach(function(p){select.append('<option>'+p['description']+'</option>')});
    jQuery(target).append("<div class='form-group'><label>"+product_categories[category]['name']+"</label>"+select[0].outerHTML+"</div>");
  }

  function load_included_swag(product, target) {
    for (var category in product_includes[product]) {
      for (var i = 0; i < product_includes[product][category]; i++) {
        console.log(category, product, i, product_includes[product][category]);
        load_product_group(category, target);
      }
    }
  }

  function add_swag_button(category_id) {
    category = product_categories[category_id];
    button = jQuery("<button type='button' id='swag_add_"+category['idname']+"' category_id='"+category_id+"'>Buy "+category['name']+"</button>");

    button.on('click', function() {
      if (jQuery("#additional_swag_list").children().length == 0) {
        jQuery("#additional_swag_list").append("<h3>Purchased</h3>");
      }
      cat_id = jQuery(this).attr('category_id');
      console.log("CLICK", this, jQuery(this).attr('category_id'));
      load_product_group(cat_id, jQuery("#additional_swag_list"));
    });

    jQuery("#additional_swag_buttons").append(button);
  }



  // Functions to manage the price summary
  function update_price_total() {
    // Tally up the last column
    total = 0;
    jQuery("#price_tally tbody tr td:last-child").each(
      function(undef,cell){total += parseFloat(cell.textContent)}
    );
    jQuery("#price_total").text(parseFloat(total).toFixed(2));
  }

  function update_price_row(product_id, description, price, qty) {
    // Update a row if it exists, otherwise create it, delete rows with qty = 0
    if(jQuery("#price_"+product_id).length > 0) {
      // if exists, delete it
      jQuery("#price_"+product_id).remove()
    }

    if(qty > 0) {
      row = jQuery("<tr id='price_"+product_id+"'>");
      row.append("<td>"+description+"</td>");
      row.append("<td>"+qty+"</td>");
      row.append("<td>"+parseFloat(price/100).toFixed(2)+"</td>");
      row.append("<td>"+parseFloat(qty*price/100).toFixed(2)+"</td>");
      jQuery("#price_tally tbody").append(row);
    }

    update_price_total();
  }
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
  for category in c.product_categories: # Ordered by display order
    try:
      tmpl = app_globals.mako_lookup.get_template("/registration/"+h.computer_title(category.name)+"_js_form.mako")
    except:
      context.write("NOT FOUND: "+h.computer_title(category.name)+"_js_form.mako"); # TODO: Handle new product groups
    else:
      tmpl.render_context(context)
%>

<fieldset class="form-horizontal">
  <h2>Swag</h3>
  <div id="ticket_swag_list"></div>
  <div id="partner_swag_list"></div>
  <div id="additional_swag_list"></div>
  <div id="additional_swag_buttons"></div>
</fieldset>

<script>
  // Partner's program

  var partner_cat = 6; // TODO: Shouldn't hardcode this
  function update_partner_program() {
    jQuery("#partner_swag_list").empty();
    jQuery("#partner_swag_list").append("<h3>Provided as part of "+product_categories[partner_cat]['name']+"</h3>");

    product_categories[partner_cat]['products'].forEach(function(product){
      val = jQuery("#"+to_id("products.product_"+products[product]['clean_description']+'_qty')).val()
      for(var i=0; i < val; i++) {
        load_included_swag(product, jQuery("#partner_swag_list"));
      }
    });
  }

  product_categories[partner_cat]['products'].forEach(function(product){
    jQuery("#"+to_id("products.product_"+products[product]['clean_description']+'_qty')).change(update_partner_program);
  });

</script>


## If no-js include non_js_form.mako

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

<script>
  radio_boxes = jQuery("input[type='radio'][name^='products.category_']:checked");
  check_boxes = jQuery("input[type='checkbox'][name^='products.product_']:checked");
  text_boxes = jQuery.grep(jQuery("input[type=text][name^='products.product_']"), function(x){return x.value > 0});


  function update_text_price(text_input) {
    var id = jQuery(text_input).attr('product_id');
    var product = products[id];
    var category = product_categories[product['category']];
    if (product.cost != 0 || category['invoice_free_products']) {
      update_price_row(id, category.name+" - "+product.description, product.cost, text_input.val());
    }
  }

  function update_radio_price(radio_input) {
    var cat_id = jQuery(radio_input).attr('category_id');
    var product_id = jQuery(radio_input).attr('value');
    var product = products[product_id];
    // If it is free and we hide free we need to hide the row
    // This requires deletion, in case we previously had a visible option
    // Easiest way to do this is with a quantity of zero to trigger it
    var qty = product.cost != 0 || product_categories[cat_id]['invoice_free_products'] ? 1 : 0;
    update_price_row("C"+cat_id, product.description, product.cost, qty);
  }

  function update_checkbox_price(cb_input) {
    var product_id = jQuery(cb_input).attr('product_id');
    var product = products[product_id];
    var category = product_categories[product['category']];
    var qty = cb_input.attr('checked') ? 1 : 0

    if (product.cost != 0 || category['invoice_free_products']) {
      update_price_row(product_id, category.name+" - "+product.description, product.cost, qty);
    }
  }

  jQuery("input[type=text][name^='products.product_']").on('change', function(){update_text_price(jQuery(this))});
  jQuery("input[type=text][name^='products.product_']").each(function(){update_text_price(jQuery(this))});

  jQuery("input[type='radio'][name^='products.category_']").on('change', function(){update_radio_price(jQuery(this))});
  jQuery("input[type='radio'][name^='products.category_']:checked").each(function(){update_radio_price(jQuery(this))});

  jQuery("input[type='checkbox'][name^='products.product_']").on('change', function(){update_checkbox_price(jQuery(this))});
  jQuery("input[type='checkbox'][name^='products.product_']:checked").each(function(){update_checkbox_price(jQuery(this))});
</script>
