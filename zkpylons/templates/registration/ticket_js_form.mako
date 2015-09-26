<%page args="category" />
<div id="ticket_div"></div>
<script>
  var ticket_cat_id = ${category.id};

  // Build div contents
  jQuery("#ticket_div").append(build_product_group(ticket_cat_id).append(build_radio_product_group(ticket_cat_id)));
  // TODO: student id warning is missing

  // Some ticket products provide swag
  jQuery('input[name="products.category_Ticket"]:radio').change(function(){
    product_id = jQuery(this).val()
    group = init_swag_group(product_categories[ticket_cat_id]);
    load_included_swag(product_id, group);
  });

  jQuery("#ticket_div input[type='radio']").on('change', update_radio_price);

  // On page load set the swag and price for the selected ticket
  jQuery(function(){
    group = init_swag_group(product_categories[ticket_cat_id]);
    load_included_swag(jQuery('#ticket input[name=products.category_Ticket]:checked').val(), group);
    jQuery("#ticket_div input[type='radio']:checked").each(update_radio_price);
  });
</script>
