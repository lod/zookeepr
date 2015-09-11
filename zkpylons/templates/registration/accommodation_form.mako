<%page args="category, products"/>
<%
  import re
  fields = {}
  for product in products:
    results = re.match("^([a-zA-Z0-9'_]+)\s+(.*)$", product.description)
    day = results.group(1).replace('_',' ')
    accom = results.group(2)

    if day not in fields:
      fields[day] = []
    fields[day].append((accom, product))
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
        %for (accom, product) in sorted(fields[day]):
<div id="${ product.clean_description(True).replace(' ','_') + '_div'}">
          %if category.display == 'qty':
            ${ h.text('products.product_' + product.clean_description(True) + '_qty', size=2, disabled=not product.available()) + ' ' + accom}
          %elif category.display == 'checkbox':
            ${ h.checkbox('products.product_' + product.clean_description(True) + '_checkbox', label=accom, disabled=not product.available()) }
          %endif # category.display
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

<%include file="accommodation_name_form.mako" args="category=category, products=products" />
