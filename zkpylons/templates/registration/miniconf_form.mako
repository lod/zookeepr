<%page args="category, products"/>
<%
  import re
  fields = {}
  for product in products:
    results = re.match("^([a-zA-Z0-9'_]+)\s+(.*)$", product.description)
    day = results.group(1).replace('_',' ')
    miniconf = results.group(2)

    if day not in fields:
      fields[day] = []
    fields[day].append((miniconf, product))
  endfor
%>
<table>
  <tr>
    %for day in sorted(fields):
      <th>${ day }</th>
    %endfor
  </tr>
  <tr>
    %for day in sorted(fields):
      <td>
        %for (miniconf, product) in sorted(fields[day]):
          %if category.display == 'qty':
            ${ h.text('products.product_' + product.clean_description(True) + '_qty', size=2, disabled=not product.available()) + ' ' + miniconf}
          %elif category.display == 'checkbox':
            ${ h.checkbox('products.product_' + product.clean_description(True) + '_checkbox', label=miniconf, disabled=not product.available()) }
          %endif
          %if not product.available():
            <span class="mandatory">SOLD&nbsp;OUT</span>
          %elif product.cost != 0:
            - ${ h.integer_to_currency(product.cost) }
          %endif
          <br>
        %endfor
      </td>
    %endfor
  </tr>
</table>
