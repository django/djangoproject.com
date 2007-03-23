<h2>Spam Filtering: Bayes</h2>

<form class="mod" id="spamconfig" method="post">

  <fieldset>
    <legend>Configuration</legend>
    <p>The bayesian filter requires training before it can effectively
    differentiate between spam and ham. The training database currently
    contains <strong><?cs var:admin.bayes.nspam ?> spam</strong> and
    <strong><?cs var:admin.bayes.nham ?> ham</strong> submissions.</p>
    <div class="field">
      <label><input type="checkbox" id="reset" name="reset" <?cs
          if:!admin.bayes.nham && !admin.bayes.nspam ?> disabled="disabled"<?cs /if ?> />
        Clear training database
      </label>
      <p class="hint">
        Resetting the training database can help when training was incorrect
        and is producing bad results.
      </p>
    </div>
    <div class="field">
      <label>Minimum training required:
        <input type="text" id="min_training" name="min_training" size="3"
               value="<?cs var:admin.bayes.min_training ?>" />
      </label>
      <p class="hint">
        The minimum number of spam and ham in the training database before
        the filter starts affecting the karma of submissions.
      </p>
    </div>
    <div class="buttons">
      <input type="submit" value="Apply changes" />
    </div>
  </fieldset>

  <fieldset>
    <legend>Training</legend>
    <p class="hint">
      While you can train the spam filter from the &ldquo;<em>Spam
      Filtering &rarr; Monitoring</em>&rdquo; panel in the web
      administration interface, you can also manually train the filter by
      entering samples here, or check what kind of spam probabilty
      currently gets assigned to the content.
    </p>
    <div class="field">
      <label for="content">Content:</label><br />
      <textarea id="content" name="content" rows="10" cols="60">
<?cs var:admin.bayes.content ?></textarea>
    </div>
    <?cs if:admin.bayes.content ?>
      <div class="field">
        <?cs if:admin.bayes.error ?>
          <strong>Error: <?cs var:admin.bayes.error ?></strong>
        <?cs else ?>
          <strong>Score: <?cs var:admin.bayes.score ?>%</strong>
        <?cs /if ?>
      </div>
    <?cs /if ?>
    <div class="buttons">
      <input type="submit" name="test" value="Test" <?cs
         if:!admin.bayes.nham || !admin.bayes.nspam ?> disabled="disabled"<?cs /if ?> />
      <input type="submit" name="train" value="Train as Spam" />
      <input type="submit" name="train" value="Train as Ham" />
    </div>
  </fieldset>

  <script type="text/javascript">
    enableControl("reset", <?cs if:admin.bayes.nspam || admin.bayes.nham ?>true<?cs else ?>false<?cs /if ?>);
  </script>

</form>
