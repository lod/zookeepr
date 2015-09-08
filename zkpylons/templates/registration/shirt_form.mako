<%page args="category, products"/>
<%
  import re

  fields = dict()
  for product in products:
    results = re.match("^([a-zA-Z0-9']+)\s+(.*)$", product.description)
    gender = results.group(1)
    size = results.group(2)

    if gender not in fields:
      fields[gender] = []
    fields[gender].append((size, product))
  endfor # product in products
%>
<table>
  %for gender in fields:
    <tr>
      <th>&nbsp;</th>
      %for (size, product) in fields[gender]:
        <th>${ size }</th>
      %endfor
    </tr>
    <tr>
      <td>${ gender }</td>
      ## This structure causes a minor html bug when there are a different number of sizes for each gender
      %for (size, product) in fields[gender]:
        %if not product.available():
          <td>
            <span class="mandatory">SOLD&nbsp;OUT</span>
            <br />
            ${ h.hidden('products.product_' + product.clean_description(True) + '_qty', 0) }
          </td>
        %else:
          %if category.display == 'qty':
            <td>
              ${ h.text('products.product_' + product.clean_description(True) + '_qty', size=2) }
            </td>
          %elif category.display == 'checkbox':
            <td>
              ${ h.checkbox('products.product_' + product.clean_description(True) + '_checkbox') }
            </td>
          %endif
        %endif
      %endfor # (size, product) in fields[gender]
    </tr>
  %endfor # gender in fields
</table>
