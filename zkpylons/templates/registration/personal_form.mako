<h2>Personal Information</h2>

<p class="note">
  <span class="mandatory">*</span> - Mandatory field
</p>

<div class="form-group">
  <label>Name:</label>
  % if c.registration and c.registration.person:
    ${ c.registration.person.fullname }
  % else:
    ${ c.signed_in_person.fullname }
  % endif
</div>

<div class="form-group">
  <label>Email address:</label>
  % if c.registration and c.registration.person:
    ${ c.registration.person.email_address }
  % else:
    ${ c.signed_in_person.email_address }
  % endif
</div>

%if c.config.get('personal_info', category='rego')['home_address'] == 'yes':
  <div class="form-group">
    <span class="mandatory">*</span>
    <label for="personaddress1">Address:</label>
      ${ h.text('person.address1', size=40) }
  </div>
  <div class="form-group">
    <label>&nbsp;</label>
    ${ h.text('person.address2', size=40) }
  </div>

  <div class="form-group">
    <span class="mandatory">*</span>
    <label for="personcity">City/Suburb:</label>
    ${ h.text('person.city', size=40) }
  </div>

  <div class="form-group">
    <label for="personstate">State/Province:</label>
    ${ h.text('person.state', size=40) }
  </div>

  <div class="form-group">
    <span class="mandatory">*</span>
    <label for="personpostcode">Postcode/ZIP:</label>
    ${ h.text('person.postcode', size=40) }
  </div>
%else:
  ${ h.hidden('person.address1') }
  ${ h.hidden('person.address2') }
  ${ h.hidden('person.city') }
  ${ h.hidden('person.state') }
  ${ h.hidden('person.postcode') }
%endif

<div class="form-group">
  <span class="mandatory">*</span>
  <label for="personcountry">Country:</label>
  <select id="personcountry" name="person.country">
    % for country in h.countries():
      <option value="${country}">${ country }</option>
    % endfor
  </select>
</div>

%if c.config.get('personal_info', category='rego')['phone'] == 'yes':
  <div class="form-group">
    <label for="personphone">Phone number (International Format):</label>
    ${ h.text('person.phone') }
  </div>

  <div class="form-group">
    % if is_speaker:
      <span class="mandatory">*</span>
    % endif
    <label for="personmobile">Mobile/Cell number (International Format):</label>
    ${ h.text('person.mobile') }
  </div>
%else:
  ${ h.hidden('person.phone') }
  ${ h.hidden('person.mobile') }
%endif

<div class="form-group">
  <label for="personcompany">Company:</label>
  ${ h.text('person.company', size=60) }
</div>
