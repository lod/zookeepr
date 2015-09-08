<%page args="category, products"/>
%for product in products:
  <div class="form-group">
    %if not product.available():$
      <span class="mandatory">SOLD&nbsp;OUT</span>
    %endif

    ${ soldout |n}
    ${ product.description }
    ${ h.text('products.product_' + product.clean_description(True) + '_qty', size=2) }
    x
    ${ h.integer_to_currency(product.cost) }
  </div>
%endfor # product in products
