<%page args="category, products"/>
<%namespace name="form" file="form_tags.mako" />

<table class="form-grid">
  <tr>
    %for product in products:
      <th>
        ${ product.description }
        <br>
        (${ h.integer_to_currency(product.cost) })
      </th>
    %endfor
  </tr>
  <tr>
    %for product in products:
      <td style="text-align:center">
        %if category.display == 'qty':
          <%form:text name="${product.full_idname}" product_id="${product.id}" size="2"/>
        %elif category.display == 'checkbox':
          <%form:checkbox name="${product.full_idname}" product_id="${product.id}"/>
        %endif
      </td>
    %endfor
  </tr>
</table>
