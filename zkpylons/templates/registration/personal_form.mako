<%namespace name="form" file="form_tags.mako" />

<h2>Personal Information</h2>

<p class="note">
  <span class="mandatory">*</span> - Mandatory field
</p>

% if c.registration and c.registration.person:
  <%form:constant label="Name">${ c.registration.person.fullname }</%form:constant>
  <%form:constant label="Email address">${ c.registration.person.email_address }</%form:constant>
% else:
  <%form:constant label="Name">${ c.signed_in_person.fullname }</%form:constant>
  <%form:constant label="Email address">${ c.signed_in_person.email_address }</%form:constant>
% endif

%if c.config.get('personal_info', category='rego')['home_address'] == 'yes':
  <%form:text name="person.address1" label="Address" mandatory="true" />
  <%form:text name="person.address2" />
  <%form:text name="person.city" label="City/Suburb" mandatory="true" />
  <%form:text name="person.state" label="State/Province" />
  <%form:text name="person.postcode" label="Postcode/ZIP" mandatory="true" />
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
  <%form:text name="person.phone" label="Phone number (International Format)" />
  <%form:text name="person.mobile" label="Mobile/Cell number (International Format)" mandatory="${c.signed_in_person.is_speaker()}" />
%else:
  ${ h.hidden('person.phone') }
  ${ h.hidden('person.mobile') }
%endif

<%form:text name="person.company" label="Company" />
