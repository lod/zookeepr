<%page args="category, products"/>
<%namespace name="form" file="form_tags.mako" />
<%
  fields = {}
  for product in products:
    ## Miniconf description field follows format of <day><whitespace><miniconf description>
    (day, miniconf) = product.description.split(None, 1)

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
      <td><ul class="nomarker">
        %for (miniconf, product) in sorted(fields[day]):
          <%
            name = ".".join(["products", c.js_categories[category.id]["idname"], c.js_products[product.id]["idname"]])
            label = miniconf + (" - " + h.integer_to_currency(product.cost) if product.cost != 0 else "")
          %>
          %if category.display == 'qty':
            <li><%form:text name="${name}" label="${label}" product_id="${product.id}" size="2"/></li>
          %elif category.display == 'checkbox':
            <li><%form:checkbox name="${name}" label="${label}" product_id="${product.id}"/></li>
          %endif
        %endfor
      </ul></td>
    %endfor
  </tr>
</table>
