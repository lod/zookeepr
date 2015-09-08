<h2>Further Information</h2>

<div class="form-group">
  <span class="mandatory">*</span> <label>Are you over 18?</label>
  <label class="radio-inline">
    <input type="radio" name="registration.over18" value="1"> Yes
  </label>
  <label class="radio-inline">
    <input type="radio" name="registration.over18" value="0"> No
  </label>
  <p>Being under 18 will not stop you from registering. We need to know whether you are over 18 to allow us to cater for you at venues that serve alcohol.</p>
</div>

<div class="form-group">
  <label for="registrationdiet">Dietary requirements:</label>
  ${ h.text('registration.diet', size=60) }
</div>

<div class="form-group">
  <label for="registrationspecial">Other special requirements:</label>
  ${ h.text('registration.special', size=60) }
  Please enter any requirements if necessary; access requirements, etc.
</div>
%if c.config.get('ask_past_confs', category='rego'):
  <label>Have you attended ${ c.config.get('event_generic_name') } before?</label>
  <table>
    <tr>
      <td>
        %for (year, desc) in c.config.get('past_confs', category='rego'):
          <% label = 'registration.prevlca.%s' % year %>
          <label>${ h.checkbox(label) } ${ desc }</label><br />
        %endfor
      </td>
    </tr>
  </table>
%endif
