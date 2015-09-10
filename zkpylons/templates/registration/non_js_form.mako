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
