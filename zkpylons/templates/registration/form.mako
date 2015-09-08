<p class="note">${ c.config.get('event_pricing_disclaimer') }</p>

<fieldset id="personal" class="form-horizontal">
  <%include file="personal_form.mako" />
</fieldset>

<fieldset id="voucher">
  <%include file="voucher_form.mako" />
</fieldset>


<fieldset id="${ h.computer_title('Ticket') }">
  <h2>Ticket</h2>
  <%
    from zkpylons.model import ProductCategory, ProductInclude
    category = ProductCategory.find_by_name('Ticket')
    all_products = category.available_products(c.signed_in_person, stock=False)
    products = [x for x in all_products if c.product_available(x, stock=False)]
    product_includes = {}
    for product in products:
      include_objs = ProductInclude.find_by_product(product)
      product_includes[product.id] = {x.include_category.id: x.include_qty for x in include_objs}
    simple_categories = {x.id:{'name':x.name, 'description':x.description} for x in c.product_categories}
    for cat in simple_categories:
      scategory = ProductCategory.find_by_name(simple_categories[cat]['name'])
      cat_products = scategory.available_products(c.signed_in_person, stock=False)
      simple_categories[cat]['products'] = [x.id for x in cat_products if c.product_available(x, stock=False)]
      simple_products = {p.id:{'category':p.category_id, 'active':p.active, 'description':p.description, 'cost':p.cost} for p in c.products}
  %>
  <script>
    product_categories = ${h.json.dumps(simple_categories)|n}
    product_includes = ${h.json.dumps(product_includes)|n}
    products = ${h.json.dumps(simple_products)|n}
  </script>
  <p class="description">${ category.description |n}</p>
  <input type="hidden" name="${'products.error.' + category.clean_name()}">
  <%include file="radio_form.mako" args="category=category, products=products" />
</fieldset>

<fieldset id="${ h.computer_title("Partners' Programme") }">
  <%include file="partner_form.mako" />
</fieldset>

<fieldset class="form-horizontal">
  <h2>Swag</h3>
  <div id="ticket_swag_list">
  </div>

  <script>
    function load_included_swag(chosen) {
      jQuery("#ticket_swag_list").empty();
      for (var category in product_includes[chosen]) {
        for (var i = 0; i < product_includes[chosen][category]; i++) {
          cat_products = product_categories[category]['products'].map(function(a){return products[a]});
          console.log(product_categories[category]['products'].map(function(a){return products[a]}));
          select = jQuery("<select>");
          cat_products.forEach(function(p){select.append('<option>'+p['description']+'</option>')});
          jQuery("#ticket_swag_list").append("<div class='form-group'><label>"+product_categories[category]['name']+"</label>"+select[0].outerHTML+"</div>");
        }
      }
    }
    jQuery('input[name="products.category_Ticket"]:radio').change(function(){
      load_included_swag(jQuery(this).val());
    });
    // On page load load the swag for the select ticket
    load_included_swag(jQuery('#ticket input[name=products.category_Ticket]:checked').val())
  </script>
</fieldset>

%for category in c.product_categories:
  <%
    all_products = category.available_products(c.signed_in_person, stock=False)
    products = [x for x in all_products if c.product_available(x, stock=False)]
    products.sort(key=lambda p: p.display_order)
    if category.name == 'Ticket':
      products = []
    if category.name == "Partners' Programme":
      products = []
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
