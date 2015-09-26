<%page args="category" />
<div id="ticket_div"></div>
<script>
  var ticket_cat_id = ${category.id};

  // Build div contents
  jQuery("#ticket_div").append(build_product_group(ticket_cat_id).append(build_radio_product_group(ticket_cat_id)));

  // Scare students by pretending we care about checking their ids
  var student_entry = jQuery(document.getElementById("products.ticket.student_ticket"));
  if (student_entry.length) {
    student_entry.parents("label").after(
      "<div id='student_warning' style='display:none' class='message message-information'>" +
      "  <p>Your student Id will be validated at the registration desk. Your card must be current or at least expired at the end of the previous term/semester.</p>" +
      "</div>"
    );
    // Need to trigger on all radios to catch deselect
    jQuery('#ticket_div input:radio').on('change', function() {
      jQuery("#student_warning").toggle(student_entry.prop('checked'));
    });
  }

  // Some ticket products provide swag
  jQuery('#ticket_div input:radio').change(function(){
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
