<%page args="category, products"/>
<fieldset id="${ h.computer_title(category.name) }">
  <h2>${ category.name.title() } </h2>
  <p class="description">${ category.description |n}</p>
  <input type="hidden" name="${'products.error.' + category.clean_name()}">

  <div id="partner_details">
    <%include file="grid_form.mako" args="category=category, products=products" />
	<%include file="partners_programme_extra_form.mako" args="category=category, products=products" />
  </div>

</fieldset>

