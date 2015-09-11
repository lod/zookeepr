<%page args="category, products"/>

<%
  fields = dict()
  for product in products:
    # Description must follow a "Gender Size" pattern
    (gender, size) = product.description.split(None, 1)

    if gender not in fields:
      fields[gender] = []
    fields[gender].append((size, product))
  endfor # product in products
%>

<fieldset id="${ h.computer_title(category.name) }">
  <h2>${ category.name.title() }</h2>
  <p class="description">${ category.description |n}</p>
  <input type="hidden" name="${'products.error.' + category.clean_name()}">

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
          <td>
            %if category.display == 'qty':
              ${ h.text('products.product_' + product.clean_description(True) + '_qty', size=2) }
            %elif category.display == 'checkbox':
              ${ h.checkbox('products.product_' + product.clean_description(True) + '_checkbox') }
            %endif
          </td>
        %endfor # (size, product) in fields[gender]
      </tr>
    %endfor # gender in fields
  </table>

  %if category.note:
    <p class="note">${ category.note | n }</p>
  %endif
</fieldset>
