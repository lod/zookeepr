<%
  from zkpylons.model import ProductCategory
  category = ProductCategory.find_by_name("Partners' Programme")
  all_products = category.available_products(c.signed_in_person, stock=False)
  products = [x for x in all_products if c.product_available(x, stock=False)]
  products.sort(key=lambda p: p.display_order)
%>

<fieldset id="${ h.computer_title(category.name) }">
  <h2>${ category.name.title() } </h2>
  <p class="description">${ category.description |n}</p>
  <input type="hidden" name="${'products.error.' + category.clean_name()}">

  <div id="partner_selector">
    Will your partner be attending the Partners Program?
    <label class="radio-inline">
      <input name="partner_visibility" type="radio" value="true"> Yes
    </label>
    <label class="radio-inline">
      <input name="partner_visibility" type="radio" value="" checked> No
    </label>
  </div>

  <div id="partner_details">
    <%include file="grid_form.mako" args="category=category, products=products" />
    <%include file="partners_programme_extra_form.mako" />
  </div>
</fieldset>

<script>
  jQuery('input[name="partner_visibility"]:radio').change(function(){
    jQuery("#partner_details").toggle(Boolean(jQuery(this).val()));
    if (Boolean(jQuery(this).val()))
      jQuery('#partner_details input[name="products.product_Partners Programme_Adult_qty"]').val(1)
  })
  // TODO: Set state based on incoming data
  jQuery("#partner_details").hide();
  jQuery('#partners_programme input[value=""]:radio').prop('checked', true);
</script>
