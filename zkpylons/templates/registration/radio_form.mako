<%page args="category, products"/>
<ul class="entries">
  %for product in products:
    %if category.name == "Ticket":
      <li>
        <label onclick="javascript: ticketWarning(' ${ product.description } ');">
          ${ h.radio('products.category_' + category.clean_name(), str(product.id)) }
          %if not product.available():
            <span class="mandatory">SOLD&nbsp;OUT</span>
          %endif
          ${ product.description } - ${ h.integer_to_currency(product.cost) }
        </label>
        %if product.description.lower().find('student') > -1:
          <div id="warningDiv">
            <div class="message message-information">
              <p>Your student Id will be validated at the registration desk. Your card must be current or at least expired at the end of the previous term/semester.</p>
            </div>
          </div>
          <script type="text/javascript">
            jQuery("#warningDiv").hide();
          </script>
        %endif
      </li>
    %else:
      <li>
        <label>
          ${ h.radio('products.category_' + category.clean_name(), str(product.id)) }
          %if not product.available():
            <span class="mandatory">SOLD&nbsp;OUT</span>
          %endif
          ${ product.description } - ${ h.integer_to_currency(product.cost) }
        </label>
      </li>
    %endif
  %endfor
</ul>
