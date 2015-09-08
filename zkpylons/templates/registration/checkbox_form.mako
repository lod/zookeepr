<%page args="category, products"/>
%for product in products:
  <%
    soldout = ''
    if not product.available():
      soldout = ' <span class="mandatory">SOLD&nbsp;OUT</span> '
  %>
  <div class="form-group">
    ${ h.checkbox(
        'products.product_' + product.clean_description(True) + '_checkbox',
        label=soldout + ' ' + product.description + ' - ' + h.integer_to_currency(product.cost)
    ) }
  </div>
%endfor
