<%namespace name="form" file="form_tags.mako" />

<div class="form-horizontal">
  <h3> Please enter your partner's details </h3>

  <%form:text name="products.partner_name" label="Name" mandatory="true" />
  <%form:text name="products.partner_email" label="Email address" mandatory="true" />
  <%form:text name="products.partner_mobile" label="Mobile phone number (international format)" mandatory="true" />

  <noscript>
    <p>
      A Partners Programme shirt is included with every adult partner ticket. Please indicate the appropriate number and sizes in the T-Shirt Section.
    </p>
  </noscript>
</div>
