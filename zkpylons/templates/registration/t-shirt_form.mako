<%page args="category, products"/>
<%namespace name="form" file="form_tags.mako" />

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

<%form:fieldset category="${category}">
  ## TODO: This structure causes a minor html bug when there are a different number of sizes for each gender
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
        %for (size, product) in fields[gender]:
          <td>
            %if category.display == 'qty':
              <%form:text name="${product.full_idname}" product_id="${product.id}" size="2"/>
            %elif category.display == 'checkbox':
              <%form:checkbox name="${product.full_idname}" product_id="${product.id}"/>
            %endif
          </td>
        %endfor # (size, product) in fields[gender]
      </tr>
    %endfor # gender in fields
  </table>
</%form:fieldset>
