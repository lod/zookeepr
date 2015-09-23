<%page args="category" />
<%
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

  function update_partner_program() {
    jQuery("#partner_swag_list").empty();
    jQuery("#partner_swag_list").append("<h3>Provided as part of "+product_categories[${category.id}]['name']+"</h3>");

    product_categories[${category.id}]['products'].forEach(function(product){
      val = jQuery("#"+to_id("products.product_"+products[product]['clean_description']+'_qty')).val()
      for(var i=0; i < val; i++) {
        load_included_swag(product, jQuery("#partner_swag_list"));
      }
    });
  }

  product_categories[${category.id}]['products'].forEach(function(product){
    jQuery("#"+to_id("products.product_"+products[product]['clean_description']+'_qty')).change(update_partner_program);
  });

  jQuery("#partner_details input[type=text][name^='products.product_']").on('change', update_text_price);

  // Set state based on incoming data
  jQuery("#partner_details").hide();
  jQuery('#partners_programme input[value=""]:radio').prop('checked', true);
  jQuery("#partner_details input[type=text][name^='products.product_']").each(function(){
    if (parseInt(jQuery(this).val()) > 0) {
      jQuery('input[name="partner_visibility"][value=true]:radio').attr('checked', true);
      jQuery("#partner_details").show()
    }
  });

  // Update swag and price lists based on initial values
  jQuery(function(){
    update_partner_program()
    jQuery("#partner_details input[type=text][name^='products.product_']").each(update_text_price);
  });

</script>
