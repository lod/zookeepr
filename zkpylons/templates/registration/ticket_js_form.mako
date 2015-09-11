<% from zkpylons.model import ProductCategory %>
<% category = ProductCategory.find_by_name('Ticket') %>
<div id="ticket_div"></div>
<script>
  // Build div contents
  jQuery("#ticket_div").append(build_product_group(${category.id}).append(build_radio_product_group(${category.id})));
  // TODO: student id warning is missing

  // Some ticket products provide swag
  jQuery('input[name="products.category_Ticket"]:radio').change(function(){
    product = jQuery(this).val()
    jQuery("#ticket_swag_list").empty();
    jQuery("#ticket_swag_list").append("<h3>Provided as part of "+products[product]["description"]);
    load_included_swag(product, jQuery("#ticket_swag_list"));
  });

  jQuery("#ticket_div input[type='radio']").on('change', update_radio_price);

  // On page load load the swag and price for the selected ticket
  jQuery(function(){
    load_included_swag(jQuery('#ticket input[name=products.category_Ticket]:checked').val());
	jQuery("#ticket_div input[type='radio']:checked").each(update_radio_price);
  });
</script>
