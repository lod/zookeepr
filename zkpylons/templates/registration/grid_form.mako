<%page args="category, products"/>
<table class="form-grid">
  <tr>
    %for product in products:
      <th>
        ${ product.description }
        <br>
        %if not product.available():
          <span class="mandatory">SOLD&nbsp;OUT</span><br>
        %endif
        (${ h.integer_to_currency(product.cost) })
      </th>
    %endfor
  </tr>
  <tr>
    %for product in products:
      %if category.display == 'qty':
        <td style="text-align:center">
			${ h.text('products.product_' + product.clean_description(True) + '_qty', product_id=product.id, size=2) }
        </td>
      %elif category.display == 'checkbox':
        <td style="text-align:center">
			${ h.checkbox('products.product_' + product.clean_description(True) + '_checkbox', product_id=product.id) }
        </td>
      %endif
    %endfor
  </tr>
</table>
