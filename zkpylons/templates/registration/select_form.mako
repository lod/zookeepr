<%page args="category, products"/>
%if category.name == 'Accommodation' and (len(category.products) == 0 or (len(category.products) == 1 and category.products[0].cost == 0)):
  <input type="hidden" name="products.category_${ category.clean_name() }">
%else:
  <div class="form-group">
    <select name="products.category_${ category.clean_name() }">
      <option value=""> - </option>
      %for product in products:
        <option value="${ product.id }">
          %if not product.available():
            SOLD&nbsp;OUT
          %endif
          ${ product.description } - ${ h.integer_to_currency(product.cost) }
        </option>
      %endfor
    </select>
  </div>
%endif
