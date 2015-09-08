<%page args="category, products"/>
%if len(category.products) == 0 or (len(category.products) == 1 and category.products[0].cost == 0):
  <p class="note">Please see the
  <a href="/register/accommodation" target="_blank">accommodation page</a>
  for discounted rates for delegates. You <strong>must</strong> book
  your accommodation directly through the accommodation providers
  yourself. Registering for the conference <strong>does not</strong>
  book your accommodation.</p>
%else:
  <p>Please see the <a href="/register/accommodation" target="_blank">accommodation page</a> for prices and details.</p>
%endif
