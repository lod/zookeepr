<%page args="category, products"/>
<table>
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
          ${ h.text('products.product_' + product.clean_description(True) + '_qty', size=2) }
        </td>
      %elif category.display == 'checkbox':
        <td style="text-align:center">
          ${ h.checkbox('products.product_' + product.clean_description(True) + '_checkbox') }
        </td>
      %endif
    %endfor
  </tr>
</table>
