<%page args="category,products" />
<%namespace name="form" file="form_tags.mako" />

<%form:fieldset category="${category}">
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
</%form:fieldset>

<script>
  var partner_category = product_categories[${category.id}];
  var partner_inputs = "#partner_details input[type=text][name^='products."+partner_category['idname']+".']";

  jQuery('input[name="partner_visibility"]:radio').change(function(){
    jQuery("#partner_details").toggle(Boolean(jQuery(this).val()));
    if (Boolean(jQuery(this).val())) {
      jQuery('#products\\.partners_programme\\.adult').val(1)
      update_partner_swag();
      jQuery(partner_inputs).each(update_text_price);
    }
  })

  function update_partner_swag() {
    // Update full group, allows clear and re-add to ensure the correct values
    // TODO: Clear and re-add removes all preset sizing information - also impacts ticket freebies
    var group = init_swag_group(partner_category);

    jQuery(partner_inputs).each(function(){
      var product_id = jQuery(this).attr("product_id");
      for(var i=0; i < this.value; i++) {
        load_included_swag(product_id, group);
      }
    });
  }

  jQuery(partner_inputs).on('change', update_partner_swag);
  jQuery(partner_inputs).on('change', update_text_price);

  // Set state based on incoming data
  jQuery("#partner_details").hide();
  jQuery('#partners_programme input[value=""]:radio').prop('checked', true);
  jQuery(partner_inputs).each(function(){
    if (parseInt(jQuery(this).val()) > 0) {
      jQuery('input[name="partner_visibility"][value=true]:radio').attr('checked', true);
      jQuery("#partner_details").show()
    }
  });

  // Update swag and price lists based on initial values - after they are loaded
  jQuery(function(){
    update_partner_swag();
    jQuery(partner_inputs).each(update_text_price);
  });

</script>
