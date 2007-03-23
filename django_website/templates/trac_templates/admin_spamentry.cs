<div class="nav"><?cs
 with:links = chrome.links ?><ul><?cs
  if:len(links.prev) ?>
   <li class="first<?cs if:!len(links.up) && !len(links.next) ?> last<?cs /if ?>">
    &larr; <a href="<?cs var:links.prev.0.href ?>">Previous Log Entry</a>
   </li><?cs
  /if ?><li class="up">
   <a href="<?cs var:links.up.0.href ?>">Back to List</a>
  </li><?cs
  if:len(links.next) ?>
   <li class="<?cs if:!len(links.prev) && !len(links.up) ?>first <?cs /if ?>last">
    <a href="<?cs var:links.next.0.href ?>">Next Log Entry</a> &rarr;
   </li><?cs
  /if ?></ul><?cs
 /with ?>
</div>
<h2>Spam Filtering: Monitoring</h2>

<?cs with:entry = admin.spamfilter.entry ?>
<form class="mod" id="spamentry" method="post">
  <fieldset>
    <legend>Log Entry:</legend>
    <h3>Information</h3>
    <table class="meta"><tr>
      <th>Time:</th>
      <td><?cs var:entry.time ?> (<?cs var:entry.timedelta ?> ago)</td>
    </tr><tr>
      <th>Path:</th>
      <td><a href="<?cs var:entry.href ?>"><?cs var:entry.url ?></a></td>
    </tr><tr>
      <th>Author:</th>
      <td><?cs var:entry.author ?></td>
    </tr><tr>
      <th>Authenticated:</th>
      <td><?cs if:entry.authenticated ?>yes<?cs else ?>no<?cs /if ?></td>
    </tr><tr>
      <th>IP address:</th>
      <td><?cs var:entry.ipnr ?></td>
    </tr><tr>
      <th>Karma:</th>
      <td>
        <strong><?cs var:entry.karma ?></strong>
        (marked as <?cs if:entry.rejected ?>spam<?cs else ?>ham<?cs /if ?>)
        <ul><?cs each:reason = entry.reasons ?>
          <li><?cs var:reason ?></li>
        <?cs /each ?></ul>
      </td>
    </tr></table>
    <div class="content">
      <h3>Submitted content</h3>
      <pre><?cs var:entry.full_content ?></pre>
    </div>
    <div class="headers">
      <h3>HTTP headers</h3>
      <pre><?cs var:entry.headers ?></pre>
    </div>
    <div class="buttons">
      <input type="hidden" name="sel" value="<?cs var:entry.id ?>" />
      <input type="submit" name="markspam" value="Mark as Spam" />
      <input type="submit" name="markham" value="Mark as Ham" />
      <input type="submit" name="delete" value="Delete" />
    </div>
  </fieldset>
</form>
<?cs /with ?>
