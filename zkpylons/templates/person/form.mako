<div class="form-horizontal">
  <div class="form-group">
    <span class="mandatory">*</span>
    <label for="personfirstname">Your first name:</label>
    ${ h.text('person.firstname', size=40) }
  </div>

  <div class="form-group">
    <span class="mandatory">*</span>
    <label for="personlastname">Your last name:</label>
    ${ h.text('person.lastname', size=40) }
  </div>

  ${ h.hidden('person.company', value='') }

  <div class="form-group">
    <span class="mandatory">*</span>
    <label for="personemail_address">Email address:</label>
    % if c.form is not 'edit' or h.auth.authorized(h.auth.has_organiser_role):
      ${ h.text('person.email_address', size=40) }
    % else:
      ${ h.text('person.email_address', size=40, readonly=True) }
      If you wish to change your email address please contact the organisers.
    % endif
  </div>

  % if c.form is not 'edit':
    <div class="form-group">
      <span class="mandatory">*</span>
      <label for="personpassword">Choose a password:</label>
      ${ h.password("person.password", size=40) }
    </div>

    <div class="form-group">
      <span class="mandatory">*</span>
      <label for="personpassword_confirm">Confirm your password:</label>
      ${ h.password("person.password_confirm", size=40) }
    </div>
  % endif

  %if c.config.get('personal_info', category='rego')['phone'] == 'yes':
    <div class="form-group">
      <label for="personphone">Phone number:</label>
      ${ h.text('person.phone') }
    </div>

    <div class="form-group">
      % if c.mobile_is_mandatory:
        <span class="mandatory">*</span>
      % endif
      <label for="personmobile">Mobile/Cell number:</label>
      ${ h.text('person.mobile') }
    </div>
  %else:
    ${ h.hidden('person.phone') }
    ${ h.hidden('person.mobile') }
  %endif

  %if c.config.get('personal_info', category='rego')['home_address'] == 'yes':
    <div class="form-group">
      <span class="mandatory">*</span>
      <label for="personaddress1">Address:</label>
      ${ h.text('person.address1', size=40) }
    </div>
    <div class="form-group">
      <label for="personaddress2">&nbsp;</label>
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
    ${ h.select('person.country', None, h.countries()) }
  </div>

  %if False and c.social_networks:
    <div class="form-group">
      Your <b>username</b> on social networking sites:
      <table>
        %for network in c.social_networks:
          <tr>
            <td>
              <img style="padding-right: 5px" src="/images/${ network.logo }">
              ${ network.name }
            </td>
            %if c.person:
              <td>
                ${ h.hidden('social_network-%s.name' % network.id, value=network.name) }
                ${ h.text('social_network-%s.account_name' % network.id, value=c.person.social_network[network.name]) }
              </td>
            %else:
              <td>
                ${ h.hidden('social_network-%s.name' % network.id, value=network.name) }
                ${ h.text('social_network-%s.account_name' % network.id, value='') }
              </td>
            %endif
          </tr>
        %endfor
      </table>
    </div>
  %endif

</div>

%if not c.person or not c.person.i_agree:
  <div class="form-group" style="text-align: center">
    <label for="personi_agree">
      I agree to the
      <a href="/cor/terms_and_conditions" target="_blank">conditions of registration</a>
      ${ h.checkbox('person.i_agree') }
    </label>
  </div>
%else:
  <div class="form-group">
    ${ h.yesno(True) |n }
    <label>I agree to the</label>
    <a href="/cor/terms_and_conditions" target="_blank">conditions of registration</a>
  </div>
  ${ h.hidden('person.i_agree', True) }
%endif
