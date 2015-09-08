<%page args="category, products"/>
<div class="form-group">
  <span class="mandatory">#</span>
  <label for="productspartner_name">Your partner's name:</label>
  ${ h.text('products.partner_name', size=50) }
  #If your partner will be participating in the programme, then this field is required so that our Partners Programme manager can contact them.
</div>

<div class="form-group">
  <span class="mandatory">#</span>
  <label for="productspartner_email">Your partner's email address:</label>
  ${ h.text('products.partner_email', size=50) }
  #If your partner will be participating in the programme, then this field is required so that our Partners Programme manager can contact them.
</div>

<div class="form-group">
  <span class="mandatory">#</span>
  <label for="productspartner_mobile">enter number in international format. If you don't know the number, type "unknown".:</label>
  ${ h.text('products.partner_mobile', size=50) }
  A Partners Programme shirt is included with every adult partner ticket. Please indicate the appropriate number and sizes in the T-Shirt Section (above).
</div>
