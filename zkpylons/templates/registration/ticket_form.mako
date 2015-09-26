<%page args="category, products"/>
<%namespace name="form" file="form_tags.mako" />

<%form:fieldset category="${category}">

<ul class="entries">
  %for product in products:
    <li>
      <%form:radio name="products.${category.clean_name()}" value="${product.id}" product_id="${product.id}" />
        ${ product.description } - ${ h.integer_to_currency(product.cost) }
      </%form:radio>
      %if product.description.lower().find('student') > -1:
        <div id="warningDiv" class="message message-information">
          <p>Your student Id will be validated at the registration desk. Your card must be current or at least expired at the end of the previous term/semester.</p>
        </div>
      %endif
    </li>
  %endfor
</ul>
</%form:fieldset>
