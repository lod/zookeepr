<%
  from zkpylons.model import ProductCategory, ProductInclude
  import re
  def to_id(ugly):
    ugly = ugly.lower();
    ugly = re.sub(r'[\s-]', "_", ugly)
    ugly = re.sub(r'\W', "", ugly)
    return ugly
  available_products = [x for x in c.products if c.product_available(x, stock=False)]
  simple_products = {p.id:{'category':p.category_id, 'active':p.active, 'description':p.description, 'clean_description':p.clean_description(True), 'cost':p.cost} for p in available_products}
  simple_includes = {i.product_id:{} for i in ProductInclude.find_all()}
  for i in ProductInclude.find_all():
    simple_includes[i.product_id][i.include_category_id] = i.include_qty
    simple_categories = {x.id:{'name':x.name, 'idname':to_id(x.name), 'description':x.description} for x in c.product_categories}
  for cat in simple_categories:
    scategory = ProductCategory.find_by_name(simple_categories[cat]['name'])
    cat_products = scategory.available_products(c.signed_in_person, stock=False)
    simple_categories[cat]['products'] = [x.id for x in cat_products if c.product_available(x, stock=False)]
%>
<script>
  product_categories = ${h.json.dumps(simple_categories)|n}
  product_includes = ${h.json.dumps(simple_includes)|n}
  products = ${h.json.dumps(simple_products)|n}


  function to_id(str) {
    str = str.toLowerCase();
    str = str.replace(/[\s-]/g, "_");
    str = str.replace(/\W/g, "");
    return str;
  }
</script>


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
    category = ProductCategory.find_by_name('Ticket')
    all_products = category.available_products(c.signed_in_person, stock=False)
    products = [x for x in all_products if c.product_available(x, stock=False)]
  %>
  <p class="description">${ category.description |n}</p>
  <input type="hidden" name="${'products.error.' + category.clean_name()}">
  <%include file="radio_form.mako" args="category=category, products=products" />
</fieldset>

<fieldset id="${ h.computer_title("Partners' Programme") }">
  <%include file="partner_form.mako" />
</fieldset>

<fieldset class="form-horizontal">
  <h2>Swag</h3>
  <div id="ticket_swag_list"></div>
  <div id="partner_swag_list"></div>
  <div id="additional_swag_list"></div>
  <div id="additional_swag_buttons">
    ##%for name in [simple_categories[x]['name'] for x in simple_categories]:
    %for cat_id in simple_categories:
      ##%if name not in ['Ticket', 'Accommodation', "Partners' Programme", 'Miniconfs']:
      %if simple_categories[cat_id]['name'] not in ['Ticket', 'Accommodation', "Partners' Programme", 'Miniconfs']:
        <button type="button" id="swag_add_${simple_categories[cat_id]['idname']}" category_id="${cat_id}">Buy ${simple_categories[cat_id]['name']}</button>
      %endif
    %endfor
  </div>

  <script>
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

    jQuery('input[name="products.category_Ticket"]:radio').change(function(){
      product = jQuery(this).val()
      jQuery("#ticket_swag_list").empty();
      jQuery("#ticket_swag_list").append("<h3>Provided as part of "+products[product]["description"]);
      load_included_swag(product, jQuery("#ticket_swag_list"));
    });
    // On page load load the swag for the selected ticket
    load_included_swag(jQuery('#ticket input[name=products.category_Ticket]:checked').val());

    // Partner's program

    var partner_cat = 6; // TODO: Shouldn't hardcode this
    function update_partner_program() {
      jQuery("#partner_swag_list").empty();
      jQuery("#partner_swag_list").append("<h3>Provided as part of "+product_categories[partner_cat]['name']+"</h3>");

      product_categories[partner_cat]['products'].forEach(function(product){$
        val = jQuery("#"+to_id("products.product_"+products[product]['clean_description']+'_qty')).val()
        for(var i=0; i < val; i++) {
          load_included_swag(product, jQuery("#partner_swag_list"));
        }
      });
    }

    product_categories[partner_cat]['products'].forEach(function(product){
      jQuery("#"+to_id("products.product_"+products[product]['clean_description']+'_qty')).change(update_partner_program);
    });

    jQuery("#additional_swag_buttons button").on('click', function() {
      if (jQuery("#additional_swag_list").children().length == 0) {
        jQuery("#additional_swag_list").append("<h3>Purchased</h3>");
      }
      cat_id = jQuery(this).attr('category_id');
      console.log("CLICK", this, jQuery(this).attr('category_id'));
      load_product_group(cat_id, jQuery("#additional_swag_list"));
    });
  </script>
</fieldset>

<%
  category = ProductCategory.find_by_name('Miniconfs')
  all_products = category.available_products(c.signed_in_person, stock=False)
  products = [x for x in all_products if c.product_available(x, stock=False)]
  products.sort(key=lambda p: p.display_order)
%>
<fieldset id="${ h.computer_title(category.name) }">
  <h2>${ category.name.title() }</h2>
  <p class="description">${ category.description |n}</p>
  <input type="hidden" name="${'products.error.' + category.clean_name()}">
  <%include file="miniconf_form.mako" args="category=category, products=products" />
</fieldset>

%for category in c.product_categories:
  <%
    all_products = category.available_products(c.signed_in_person, stock=False)
    products = [x for x in all_products if c.product_available(x, stock=False)]
    products.sort(key=lambda p: p.display_order)
  %>
  ##%if len(products) > 0:
  %if false:
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
