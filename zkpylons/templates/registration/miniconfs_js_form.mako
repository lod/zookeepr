<%page args="category,products" />

<%include file="miniconfs_form.mako" args="category=category, products=products" />

<script>
  var miniconf_cat_idname = product_categories[${category.id}].idname;
  var miniconf_inputs = "#"+miniconf_cat_idname+" input[name^='products."+miniconf_cat_idname+".']";
  jQuery(miniconf_inputs).on('change', update_checkbox_price);

  jQuery(function(){
    jQuery(miniconf_inputs+":checked").each(update_checkbox_price);
  });

</script>
