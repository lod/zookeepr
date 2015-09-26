<%page args="category, products"/>
<fieldset id="${ h.computer_title(category.name) }">
  <h2>${ category.name.title() }</h2>
  <p class="description">${ category.description |n}</p>
  <input type="hidden" name="${'products.error.' + category.clean_name()}">
  <%include file="grid_form.mako" args="category=category, products=products" />
  %if category.note:
    <p class="note">${ category.note | n }</p>
  %endif
</fieldset>
