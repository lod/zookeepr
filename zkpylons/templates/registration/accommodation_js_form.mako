<%
  import re
  from zkpylons.model import ProductCategory

  category = ProductCategory.find_by_name('Accommodation')
  all_products = category.available_products(c.signed_in_person, stock=False)
  products = [x for x in all_products if c.product_available(x, stock=False)]
  products.sort(key=lambda p: p.display_order)

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

${products}

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

<script>
  $('div[id$="double_div"]').hide();
  $('div[id$="double_breakfast_div"]').hide();
  $('div[id$="single_breakfast_div"]').hide();

  function accommdisplay() {
    if (jQuery('input[id="breaky_accomm_option"]').attr('checked')) {
      jQuery('div[id$="breakfast_div"]').show();
      jQuery('div[id$="double_div"]').hide();
      jQuery('div[id$="single_div"]').hide();
    } else {
      jQuery('div[id$="breakfast_div"]').hide();
      jQuery('div[id$="double_div"]').show();
      jQuery('div[id$="single_div"]').show();
    }
    if (jQuery('input[id="double_accomm_option"]').attr('checked')) {
      jQuery('div[id*="_single_"]').hide();
    } else {
      jQuery('div[id*="_double_"]').hide();
    }
    jQuery('input[id*="_accommodation_"]').attr('checked', false);
  }

  $('input[id$="accomm_option"]').change( function() {
    accommdisplay();
  });
</script>

<%include file="accommodation_name_form.mako" args="category=category, products=products" />
