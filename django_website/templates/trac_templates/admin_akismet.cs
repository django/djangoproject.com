<h2>Spam Filtering: Akismet</h2>

<form class="mod" id="spamconfig" method="post">

  <fieldset>
    <legend>Akismet</legend>
    <p class="hint">
      The Akismet filter uses the free
      <a class="ext-link" href="http://akismet.com/">Akismet</a>
      service to content submissions are potential spam. You need to obtain an
      API key to use the service, which is freely available for personal use.
      You can enable or disable this filter from the &ldquo;<em>General &rarr;
      Plugins</em>&rdquo; panel of the web administration interface.
    </p>
    <div class="field">
      <label>API key:<br />
        <input type="text" id="api_key" name="api_key" size="24"
               value="<?cs var:admin.akismet.api_key ?>" />
      </label>
    </div>
    <div class="field">
      <label>URL:<br />
        <code>http://</code>
        <input type="text" id="api_url" name="api_url" size="40"
               value="<?cs var:admin.akismet.api_url ?>" />
      </label>
    </div>

    <?cs if:admin.akismet.error ?>
    <div class="system-message">
      <strong>Key validation failed:</strong> <?cs var:admin.akismet.error ?>
    </div>
    <?cs /if ?>

  </fieldset>

  <div class="buttons">
    <input type="submit" value="Apply changes" />
    <?cs if:admin.akismet.error ?>
      <input type="submit" name="Cancel" value="Revert changes" />
    <?cs /if ?>
  </div>
</form>
