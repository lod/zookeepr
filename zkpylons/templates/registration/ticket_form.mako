<%page args="category, products"/>
<%namespace name="form" file="form_tags.mako" />

<fieldset id="${ h.computer_title(category.name) }">
<h2>${ category.name.title() }</h2>
<p class="description">${ category.description |n}</p>
<input type="hidden" name="${'products.error.' + category.clean_name()}">

<ul class="entries">
  %for product in products:
    <li>
      <%form:radio name="products.${category.clean_name()}" value="${product.id}" product_id="${product.id}" />
        ${ product.description } - ${ h.integer_to_currency(product.cost) }
      </%form:radio>
      %if product.description.lower().find('student') > -1:
        <div id="warningDiv">
          <div class="message message-information">
            <p>Your student Id will be validated at the registration desk. Your card must be current or at least expired at the end of the previous term/semester.</p>
          </div>
        </div>
      %endif
    </li>
  %endfor
</ul>

%if category.note:
<p class="note">${ category.note | n }</p>
%endif
</fieldset>
