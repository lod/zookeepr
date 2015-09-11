<%
  from zkpylons.model import ProductCategory
  category = ProductCategory.find_by_name('Accommodation')
%>
<fieldset id="${ h.computer_title(category.name) }">
  <h2>${ category.name.title() }</h2>
  <p class="description">${ category.description |n}</p>
  <input type="hidden" name="${'products.error.' + category.clean_name()}">

  ## A single free accommodation option is a placeholder -> self organise
  %if len(category.products) == 0 or (len(category.products) == 1 and category.products[0].cost == 0):
    <input type="hidden" name="products.category_${ category.clean_name() }">
    <p class="note">
      Please see the
      <a href="/register/accommodation" target="_blank">accommodation page</a>
      for discounted rates for delegates. You <strong>must</strong> book
      your accommodation directly through the accommodation providers
      yourself. Registering for the conference <strong>does not</strong>
      book your accommodation.
    </p>
  %else:
    <div class="form-group"></div>
    <p>Please see the <a href="/register/accommodation" target="_blank">accommodation page</a> for prices and details.</p>
	<script>
		select = build_select_product_group(${category.id});
		// Add a dummy first option - force the user to select something
		// This avoids people turning up assuming accommodation is provided
		select.prepend("<option>--</option>");
		jQuery(select.children()[0]).prop('selected', true);
		// TODO: Set selected based on input data
		jQuery("#${ h.computer_title(category.name) } div").append(select);
	</script>
  %endif
</fieldset>
