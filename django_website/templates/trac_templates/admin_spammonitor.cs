<h2>Spam Filtering: Logs</h2>

<form method="post">

  <?cs if:!admin.spamfilter.enabled ?><p>
    <strong>Note:</strong> Logging by the spam filter is currently disabled.
  </p><?cs /if ?>

  <p class="hint">
    Viewing entries <?cs var:admin.spamfilter.offset ?>–<?cs
      var:admin.spamfilter.offset + len(admin.spamfilter.entries) - 1 ?> of
    <?cs var:admin.spamfilter.total ?>.
  </p>
  <div class="nav"><?cs
   with:links = chrome.links ?><?cs
    if:len(links.prev) || len(links.next) ?><ul><?cs
     if:len(links.prev) ?>
      <li class="first<?cs if:!len(links.up) && !len(links.next) ?> last<?cs /if ?>">
       &larr; <a href="<?cs var:links.prev.0.href ?>"><?cs
         var:links.prev.0.title ?></a>
      </li><?cs
     /if ?><?cs
     if:len(links.next) ?>
      <li class="<?cs if:!len(links.prev) && !len(links.up) ?>first <?cs /if ?>last">
       <a href="<?cs var:links.next.0.href ?>"><?cs
         var:links.next.0.title ?></a> &rarr;
      </li><?cs
     /if ?></ul><?cs
    /if ?><?cs
   /with ?>
  </div>

  <table class="listing" id="spammonitor">
    <thead>
      <tr>
        <th class="sel">&nbsp;</th>
        <th>Author</th>
        <th>Path</th>
        <th>Karma</th>
        <th>IP Address</th>
        <th>Date/time</th>
      </tr>
    </thead>
    <tbody>
      <?cs each:entry = admin.spamfilter.entries ?>
        <tr class="<?cs if:name(entry) % 2 ?>odd<?cs else ?>even<?cs /if ?><?cs
                        if:entry.rejected ?> rejected<?cs /if ?>">
          <td  rowspan="2">
            <input type="checkbox" name="sel" value="<?cs var:entry.id ?>" />
          </td>
          <td class="author"<?cs
              if:entry.author != entry.author_clipped ?> title="<?cs var:entry.author ?>"<?cs
              /if ?>>
            <a href="<?cs var:entry.admin_href ?>"><img src="<?cs var:chrome.href ?>/spamfilter/<?cs
              if:entry.authenticated ?>yes<?cs else ?>no<?cs /if ?>.gif" alt="<?cs
              if:entry.authenticated ?>yes<?cs else ?>no<?cs /if ?>" title="User was<?cs
              if:!entry.authenticated ?> not<?cs /if ?> logged in"/>&nbsp;<?cs
              alt:entry.author_clipped ?>anonymous<?cs /alt ?></a>
          </td>
          <td class="path"<?cs
              if:entry.path != entry.path_clipped ?> title="<?cs var:entry.path ?>"<?cs
              /if ?>>
            <a href="<?cs var:entry.admin_href ?>"><?cs var:entry.path_clipped ?></a>
          </td>
          <td class="karma"><?cs var:entry.karma ?></td>
          <td class="ipnr"><?cs var:entry.ipnr ?></td>
          <td class="time"><?cs var:entry.time ?></td>
        </tr>
        <tr class="<?cs if:name(entry) % 2 ?>odd<?cs else ?>even<?cs /if ?>">
          <td class="details" colspan="5">
            <?cs if:len(entry.reasons) ?>
              <ul><?cs each:reason = entry.reasons ?>
                <li><?cs var:reason ?></li>
              <?cs /each ?></ul>
            <?cs /if ?>
            <blockquote><?cs var:entry.content ?></blockquote>
          </td>
        </tr>
      <?cs /each ?>
    </tbody>
  </table>

  <div class="nav"><?cs
   with:links = chrome.links ?><?cs
    if:len(links.prev) || len(links.next) ?><ul><?cs
     if:len(links.prev) ?>
      <li class="first<?cs if:!len(links.up) && !len(links.next) ?> last<?cs /if ?>">
       &larr; <a href="<?cs var:links.prev.0.href ?>"><?cs
         var:links.prev.0.title ?></a>
      </li><?cs
     /if ?><?cs
     if:len(links.next) ?>
      <li class="<?cs if:!len(links.prev) && !len(links.up) ?>first <?cs /if ?>last">
       <a href="<?cs var:links.next.0.href ?>"><?cs
         var:links.next.0.title ?></a> &rarr;
      </li><?cs
     /if ?></ul><?cs
    /if ?><?cs
   /with ?>
  </div>

  <div class="buttons">
    <input type="hidden" name="page" value="<?cs var:admin.spamfilter.page ?>" />
    <input type="submit" name="markspam" value="Mark selected as Spam" />
    <input type="submit" name="markham" value="Mark selected as Ham" />
    <input type="submit" name="delete" value="Deleted selected" />
  </div>

</form>
