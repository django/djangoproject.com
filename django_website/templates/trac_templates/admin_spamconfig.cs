<h2>Spam Filtering: Configuration</h2>

<form class="mod" id="spamconfig" method="post">

  <fieldset id="karmatuning">
    <legend>Karma Tuning</legend>
    <div class="field">
      <label>
        Minimum karma required for a successful submission:
        <input type="text" id="min_karma" name="min_karma" size="3"
               value="<?cs var:admin.spamfilter.min_karma ?>" />
      </label>
    </div>
    <p class="hint">
      Content submissions are passed through a set of registered and enabled
      <em>filter strategies</em>, each of which check the submitted content
      and may assign <em>karma points</em> to it. The sum of these karma
      points needs to be greater than or equal to the minimum karma
      configured here for the submission to be accepted.
    </p>
    <table class="listing" id="karmapoints">
      <thead><tr>
        <th>Strategy</th>
        <th>Karma points</th>
        <th>Description</th>
      </tr></thead>
      <?cs each:strategy = admin.spamfilter.strategies ?><tr>
        <th><?cs var:strategy.name ?></th>
        <td>
          <input type="text" name="<?cs var:strategy.name ?>_karmapoints"
                 value="<?cs var:strategy.karma_points ?>" size="3" />
        </td>
        <td><p class="hint"><?cs var:strategy.karma_help ?></p></td>
      </tr><?cs /each ?>
    </table>
  </fieldset>

  <fieldset id="logging">
    <legend>Logging</legend>
    <div class="field">
      <label>
        <input type="checkbox" id="logging_enabled" name="logging_enabled" <?cs
            if:admin.spamfilter.logging_enabled ?> checked="checked"<?cs /if ?> />
        Enable
      </label>
    </div>
    <p class="hint">
      The spam filter plugin can optionally log every content submission so
      that you can monitor and tune the effectiveness of the filtering. The
      log is stored in the database, and can be viewed under &ldquo;<em>Spam
      Filtering &rarr; Monitoring</em>&rdquo; from the web administration
      interface.
    </p>
    <div class="field">
      <label>
        Purge old entries after
        <input type="text" id="purge_age" name="purge_age" size="3"
               value="<?cs var:admin.spamfilter.purge_age ?>" />
        days
      </label>
    </div>
  </fieldset>

  <div class="buttons">
    <input type="submit" value="Apply changes"/>
  </div>
</form>

<script type="text/javascript">
  var loggingEnabled = document.getElementById("logging_enabled");
  function updateLoggingEnabled() {
    enableControl("purge_age", loggingEnabled.checked);
  }
  addEvent(window, 'load', updateLoggingEnabled);
  addEvent(loggingEnabled, 'click', updateLoggingEnabled);
</script>
