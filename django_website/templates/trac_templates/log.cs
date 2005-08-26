<?cs set:html.stylesheet = 'css/browser.css' ?>
<?cs include "header.cs"?>
<?cs include "macros.cs"?>

<div id="ctxtnav" class="nav">
 <ul>
  <li class="last"><a href="<?cs
    var:log.browser_href ?>">View Latest Revision</a></li><?cs
  if:len(chrome.links.prev) ?>
   <li class="first<?cs if:!len(chrome.links.next) ?> last<?cs /if ?>">
    &larr; <a href="<?cs var:chrome.links.prev.0.href ?>" title="<?cs
      var:chrome.links.prev.0.title ?>">Newer Revisions</a>
   </li><?cs
  /if ?><?cs
  if:len(chrome.links.next) ?>
   <li class="<?cs if:!len(chrome.links.prev) ?>first <?cs /if ?>last">
    <a href="<?cs var:chrome.links.next.0.href ?>" title="<?cs
      var:chrome.links.next.0.title ?>">Older Revisions</a> &rarr;
   </li><?cs
  /if ?>
 </ul>
</div>


<div id="content" class="log">
 <h1><?cs call:browser_path_links(log.path, log) ?></h1>
 <form id="prefs" action="<?cs var:browser_current_href ?>" method="get">
  <div>
   <input type="hidden" name="action" value="<?cs var:log.mode ?>" />
   <label>View log starting at <input type="text" id="rev" name="rev" value="<?cs
    var:log.items.0.rev ?>" size="5" /></label>
   <label>and back to <input type="text" id="stop_rev" name="stop_rev" value="<?cs
    var:log.stop_rev ?>" size="5" /></label>
   <br />
   <div class="choice" ?>
    <fieldset>
     <legend>Mode:</legend>
     <label for="stop_on_copy">
      <input type="radio" id="stop_on_copy" name="mode" value="stop_on_copy" <?cs
       if:log.mode != "follow_copy" || log.mode != "path_history" ?> checked="checked" <?cs
       /if ?> />
      Stop on copy 
     </label>
     <label for="follow_copy">
      <input type="radio" id="follow_copy" name="mode" value="follow_copy" <?cs
       if:log.mode == "follow_copy" ?> checked="checked" <?cs /if ?> />
      Follow copies
     </label>
     <label for="path_history">
      <input type="radio" id="path_history" name="mode" value="path_history" <?cs
       if:log.mode == "path_history" ?> checked="checked" <?cs /if ?> />
      Show only adds, moves and deletes
     </label>
    </fieldset>
   </div>
   <label><input type="checkbox" name="verbose" <?cs
    if:log.verbose ?> checked="checked" <?cs
    /if ?> /> Show full log messages</label>
  </div>
  <div class="buttons">
   <input type="submit" value="Update" 
          title="Warning: by updating, you will clear the page history" />
  </div>
 </form>
 <div class="diff">
  <div id="legend">
   <h3>Legend:</h3>
   <dl>
    <dt class="add"></dt><dd>Added</dd><?cs
    if:log.mode == "path_history" ?>
     <dt class="rem"></dt><dd>Removed</dd><?cs
    /if ?>
    <dt class="mod"></dt><dd>Modified</dd>
    <dt class="cp"></dt><dd>Copied or renamed</dd>
   </dl>
  </div>
 </div>
 <table id="chglist" class="listing">
  <thead>
   <tr>
    <th class="change"></th>
    <th class="data">Date</th>
    <th class="rev">Rev</th>
    <th class="chgset">Chgset</th>
    <th class="author">Author</th>
    <th class="summary">Log Message</th>
   </tr>
  </thead>
  <tbody><?cs
   set:indent = #1 ?><?cs
   each:item = log.items ?><?cs
    if:item.copyfrom_path ?>
     <tr class="<?cs if:name(item) % #2 ?>even<?cs else ?>odd<?cs /if ?>">
      <td class="copyfrom_path" colspan="6" style="padding-left: <?cs var:indent ?>em">
       copied from <a href="<?cs var:item.browser_href ?>"?><?cs var:item.copyfrom_path ?></a>:
      </td>
     </tr><?cs
     set:indent = indent + #1 ?><?cs
    elif:log.mode == "path_history" ?><?cs
      set:indent = #1 ?><?cs
    /if ?>
    <tr class="<?cs if:name(item) % #2 ?>even<?cs else ?>odd<?cs /if ?>">
     <td class="change" style="padding-left:<?cs var:indent ?>em">
      <a title="View log starting at this revision" href="<?cs var:item.log_href ?>">
       <div class="<?cs var:item.change ?>"></div>
       <span class="comment">(<?cs var:item.change ?>)</span>
      </a>
     </td>
     <td class="date"><?cs var:log.changes[item.rev].date ?></td>
     <td class="rev">
      <a href="<?cs var:item.browser_href ?>"><?cs var:item.rev ?></a>
     </td>
     <td class="chgset">
      <a href="<?cs var:item.changeset_href ?>"><?cs var:item.rev ?></a>
     </td>
     <td class="author"><?cs var:log.changes[item.rev].author ?></td>
     <td class="summary"><?cs var:log.changes[item.rev].message ?></td>
    </tr><?cs
   /each ?>
  </tbody>
 </table><?cs
 if:len(links.prev) || len(links.next) ?><div id="paging" class="nav"><ul><?cs
  if:len(links.prev) ?><li class="first<?cs
   if:!len(links.next) ?> last<?cs /if ?>">&larr; <a href="<?cs
   var:links.prev.0.href ?>" title="<?cs
   var:links.prev.0.title ?>">Younger Revisions</a></li><?cs
  /if ?><?cs
  if:len(links.next) ?><li class="<?cs
   if:len(links.prev) ?>first <?cs /if ?>last"><a href="<?cs
   var:links.next.0.href ?>" title="<?cs
   var:links.next.0.title ?>">Older Revisions</a> &rarr;</li><?cs
  /if ?></ul></div><?cs
 /if ?>

</div>
<?cs include "footer.cs"?>
