<% from zkpylons.model import ProductCategory %>
<% category = ProductCategory.find_by_name('T-Shirt') %>
<script>
  jQuery(function() { add_swag_button(${category.id}) })
</script>
