<h2>Partners' Programme</h2>
<%
  from zkpylons.model import ProductCategory
  category = ProductCategory.find_by_name("Partners' Programme")
  all_products = category.available_products(c.signed_in_person, stock=False)
  products = [x for x in all_products if c.product_available(x, stock=False)]
%>
<p class="description">${ category.description |n}</p>
<input type="hidden" name="${'products.error.' + category.clean_name()}">

<div id="partner_selector">
  Will your partner be attending the Partners Program?
  <label class="radio-inline">
    <input name="partner_visibility" type="radio" value="true"> Yes
  </label>
  <label class="radio-inline">
    <input name="partner_visibility" type="radio" value="" checked> No
  </label>
</div>

<div id="partner_details">
  <%include file="grid_form.mako" args="category=category, products=products" />

  <div class="form-horizontal">
    <h3> Please enter your partner's details </h3>

    <div class="form-group">
    <span class="mandatory">*</span>
    <label for="productspartner_name">Name:</label>
    ${ h.text('products.partner_name') }
    </div>

    <div class="form-group">
    <span class="mandatory">*</span>
    <label for="productspartner_email">Email address:</label>
    ${ h.text('products.partner_email') }
    </div>

    <div class="form-group">
    <span class="mandatory">*</span>
    <label for="productspartner_mobile">Mobile phone number (international format):</label>
    ${ h.text('products.partner_mobile') }
    <noscript>
      <p>
        A Partners Programme shirt is included with every adult partner ticket. Please indicate the appropriate number and sizes in the T-Shirt Section.
      </p>
    </noscript>
    </div>
  </div>
</div>

<style>
  /* Hide selector from non-JS clients */
  #partner_selector: { display: none; }
</style>

<script>
  // TODO: Note display order must be forced, adult < child < infant
  jQuery('input[name="partner_visibility"]:radio').change(function(){
    jQuery("#partner_details").toggle(Boolean(jQuery(this).val()));
    if (Boolean(jQuery(this).val()))
      jQuery('#partner_details input[name="products.product_Partners Programme_Adult_qty"]').val(1)
  })
  // Show selector for JS clients
  // TODO: Set state based on incoming data
  jQuery("#partner_selector").show();
  jQuery("#partner_details").hide();
  jQuery('#partners_programme input[value=""]:radio').prop('checked', true);
</script>


