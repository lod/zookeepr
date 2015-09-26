<%page args="category,products" />
<%namespace name="form" file="form_tags.mako" />

<%form:fieldset category="${category}">
  ## A single free accommodation option is a placeholder -> self organise
  %if len(products) == 0 or (len(products) == 1 and products[0].cost == 0):
	<input type="hidden" name="products.category_${ category.idname }">
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
      accom_category = product_categories[${category.id}];
      select = build_select_product_group(accom_category.id);
      // Add a dummy first option - force the user to select something
      // This avoids people turning up assuming accommodation is provided
      select.prepend("<option>--</option>");
      jQuery(select.children()[0]).prop('selected', true);
      // TODO: Set selected based on input data
      jQuery("#"+accom_category.idname+" div").append(select);

      jQuery("#"+accom_category.idname+" select").on("change", update_select_price);
    </script>
  %endif
</%form:fieldset>
