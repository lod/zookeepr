<%
  from zkpylons.model import ProductCategory
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
<script>
  jQuery("#${h.computer_title(category.name)} input[type='checkbox'][name^='products.product_']").on('change', update_checkbox_price);

  jQuery(function(){
    jQuery("#${h.computer_title(category.name)} input[type='checkbox'][name^='products.product_']:checked").each(update_checkbox_price);
  });

</script>
