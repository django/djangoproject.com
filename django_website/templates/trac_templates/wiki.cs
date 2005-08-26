<?cs include "header.cs" ?>
<?cs include "macros.cs" ?>

<div id="ctxtnav" class="nav">
 <h2>Wiki Navigation</h2>
 <ul>
  <li><a href="<?cs var:trac.href.wiki ?>">Start Page</a></li>
  <li><a href="<?cs var:trac.href.wiki ?>/TitleIndex">Title Index</a></li>
  <li><a href="<?cs var:trac.href.wiki ?>/RecentChanges">Recent Changes</a></li>
  <?cs if:wiki.history_href ?>
   <li class="last"><a href="<?cs var:wiki.history_href ?>">Page History</a></li>
  <?cs else ?>
   <li class="last">Page History</li>
  <?cs /if ?>
 </ul>
 <hr />
</div>

<div id="content" class="wiki">

 <?cs if wiki.action == "delete" ?>
  <h1>Delete <?cs
   if:?wiki.version ?>version <?cs var:wiki.version ?> of <?cs /if ?><a href="<?cs
    var:wiki.current_href ?>"><?cs var:wiki.page_name ?></a></h1>
  <form action="<?cs var:wiki.href ?>" method="post">
   <input type="hidden" name="action" value="delete" />
   <p><strong>Are you sure you want to <?cs
    if:!?wiki.version ?>completely <?cs /if ?>delete <?cs
    if:?wiki.version ?>version <?cs var:wiki.version ?> of <?cs
    /if ?>this page?</strong><br /><?cs
   if:wiki.only_version ?>
    This is the only version the page, so the page will be removed
    completely!<?cs
   /if ?>
   This is an irreversible operation.</p>
   <div class="buttons">
    <input type="submit" name="cancel" value="Cancel" />
    <input type="submit" value="Delete <?cs
      if:?wiki.version ?>this version<?cs else ?>page<?cs /if ?>" />
   </div>
  </form>
 
 <?cs elif:wiki.action == "diff" ?>
  <h1>Changes between Version <?cs var:wiki.old_version?> and <?cs
    var:wiki.version?> of <a href="<?cs var:wiki.current_href ?>"><?cs 
    var:wiki.page_name ?></a></h1>
  <form method="post" id="prefs" action="<?cs var:wiki.current_href ?>">
   <div>
    <input type="hidden" name="action" value="diff" />
    <input type="hidden" name="version" value="<?cs var:wiki.version ?>" />
    <label>View differences <select name="style">
     <option value="inline"<?cs
       if:diff.style == 'inline' ?> selected="selected"<?cs
       /if ?>>inline</option>
     <option value="sidebyside"<?cs
       if:diff.style == 'sidebyside' ?> selected="selected"<?cs
       /if ?>>side by side</option>
    </select></label>
    <div class="field">
     Show <input type="text" name="contextlines" id="contextlines" size="2"
       maxlength="2" value="<?cs var:diff.options.contextlines ?>" />
     <label for="contextlines">lines around each change</label>
    </div>
    <fieldset id="ignore">
     <legend>Ignore:</legend>
     <div class="field">
      <input type="checkbox" id="blanklines" name="ignoreblanklines"<?cs
        if:diff.options.ignoreblanklines ?> checked="checked"<?cs /if ?> />
      <label for="blanklines">Blank lines</label>
     </div>
     <div class="field">
      <input type="checkbox" id="case" name="ignorecase"<?cs
        if:diff.options.ignorecase ?> checked="checked"<?cs /if ?> />
      <label for="case">Case changes</label>
     </div>
     <div class="field">
      <input type="checkbox" id="whitespace" name="ignorewhitespace"<?cs
        if:diff.options.ignorewhitespace ?> checked="checked"<?cs /if ?> />
      <label for="whitespace">White space changes</label>
     </div>
    </fieldset>
    <div class="buttons">
     <input type="submit" name="update" value="Update" />
    </div>
   </div>
  </form>
  <dl id="overview">
   <dt class="author">Author:</dt>
   <dd class="author"><?cs
    if:wiki.num_changes > 1 ?><em class="multi">(multiple changes)</em><?cs
    else ?><?cs var:wiki.author ?> <span class="ipnr">(IP: <?cs
     var:wiki.ipnr ?>)</span><?cs
    /if ?></dd>
   <dt class="time">Timestamp:</dt>
   <dd class="time"><?cs
    if:wiki.num_changes > 1 ?><em class="multi">(multiple changes)</em><?cs
    elif:wiki.time ?><?cs var:wiki.time ?> (<?cs var:wiki.time_delta ?> ago)<?cs
    else ?>--<?cs
    /if ?></dd>
   <dt class="comment">Comment:</dt>
   <dd class="comment"><?cs
    if:wiki.num_changes > 1 ?><em class="multi">(multiple changes)</em><?cs
    else ?><?cs var:wiki.comment ?><?cs /if ?></dd>
  </dl>
  <div class="diff">
   <div id="legend">
    <h3>Legend:</h3>
    <dl>
     <dt class="unmod"></dt><dd>Unmodified</dd>
     <dt class="add"></dt><dd>Added</dd>
     <dt class="rem"></dt><dd>Removed</dd>
     <dt class="mod"></dt><dd>Modified</dd>
    </dl>
   </div>
   <ul class="entries">
    <li class="entry">
     <h2><?cs var:wiki.page_name ?></h2><?cs
      if:diff.style == 'sidebyside' ?>
      <table class="sidebyside" summary="Differences">
       <colgroup class="l"><col class="lineno" /><col class="content" /></colgroup>
       <colgroup class="r"><col class="lineno" /><col class="content" /></colgroup>
       <thead><tr>
        <th colspan="2">Version <?cs var:wiki.old_version ?></th>
        <th colspan="2">Version <?cs var:wiki.version ?></th>
       </tr></thead><?cs
       each:change = wiki.diff ?><?cs
        call:diff_display(change, diff.style) ?><?cs
       /each ?>
      </table><?cs
     else ?>
      <table class="inline" summary="Differences">
       <colgroup><col class="lineno" /><col class="lineno" /><col class="content" /></colgroup>
       <thead><tr>
        <th title="Version <?cs var:wiki.old_version ?>">v<?cs
          var:wiki.old_version ?></th>
        <th title="Version <?cs var:wiki.version ?>">v<?cs
          var:wiki.version ?></th>
        <th>&nbsp;</th>
       </tr></thead><?cs
       each:change = wiki.diff ?><?cs
        call:diff_display(change, diff.style) ?><?cs
       /each ?>
      </table><?cs
     /if ?>
    </li>
   </ul>
  </div>

 <?cs elif wiki.action == "history" ?>
  <h1>Change History of <a href="<?cs var:wiki.current_href ?>"><?cs
    var:wiki.page_name ?></a></h1>
  <?cs if:len(wiki.history) ?><form method="get" action="">
   <input type="hidden" name="action" value="diff" />
   <table id="wikihist" class="listing" summary="Change history">
    <thead><tr>
     <th class="diff"></th>
     <th class="version">Version</th>
     <th class="date">Date</th>
     <th class="author">Author</th>
     <th class="comment">Comment</th>
    </tr></thead>
    <tbody><?cs each:item = wiki.history ?>
     <tr class="<?cs if:name(item) % #2 ?>even<?cs else ?>odd<?cs /if ?>">
      <td class="diff"><input type="radio" name="old_version" value="<?cs
        var:item.version ?>"<?cs
        if:name(item) == 1 ?> checked="checked"<?cs
        /if ?> /> <input type="radio" name="version" value="<?cs
        var:item.version ?>"<?cs
        if:name(item) == 0 ?> checked="checked"<?cs
        /if ?> /></td>
      <td class="version"><a href="<?cs
        var:item.url ?>" title="View this version"><?cs
        var:item.version ?></a></td>
      <td class="date"><?cs var:item.time ?></td>
      <td class="author" title="IP-Address: <?cs var:item.ipaddr ?>"><?cs 
        var:item.author ?></td>
      <td class="comment"><?cs var:item.comment ?></td>
     </tr>
    <?cs /each ?></tbody>
   </table>
   <div class="buttons">
    <input type="submit" value="View changes" />
   </div>
  </form><?cs /if ?>
 
 <?cs else ?>
  <?cs if wiki.action == "edit" || wiki.action == "preview" || wiki.action == "collision" ?>
   <h1>Editing "<?cs var:wiki.page_name ?>"</h1><?cs
    if wiki.action == "preview" ?>
     <fieldset id="preview">
      <legend>Preview (<a href="#edit">skip</a>)</legend>
      <div class="wikipage"><?cs var:wiki.page_html ?></div>
     </fieldset><?cs
     elif wiki.action =="collision"?>
     <div class="system-message">
       Sorry, this page has been modified by somebody else since you started 
       editing. Your changes cannot be saved.
     </div><?cs
    /if ?>
   <form id="edit" action="<?cs var:wiki.current_href ?>" method="post">
    <fieldset class="iefix">
     <input type="hidden" name="action" value="edit" />
     <input type="hidden" name="version" value="<?cs var:wiki.version ?>" />
     <input type="hidden" id="scroll_bar_pos" name="scroll_bar_pos" value="<?cs
       var:wiki.scroll_bar_pos ?>" />
     <div id="rows">
      <label for="editrows">Adjust edit area height:</label>
      <select size="1" name="editrows" id="editrows" tabindex="43"
        onchange="resizeTextArea('text', this.options[selectedIndex].value)"><?cs
       loop:rows = 8, 42, 4 ?>
        <option value="<?cs var:rows ?>"<?cs
          if:rows == wiki.edit_rows ?> selected="selected"<?cs /if ?>><?cs
          var:rows ?></option><?cs
       /loop ?>
      </select>
     </div>
     <p><textarea id="text" class="wikitext" name="text" cols="80" rows="<?cs
       var:wiki.edit_rows ?>"><?cs var:wiki.page_source ?></textarea></p>
     <script type="text/javascript">
       var scrollBarPos = document.getElementById("scroll_bar_pos");
       var text = document.getElementById("text");
       addEvent(window, "load", function() {
         if (scrollBarPos.value) text.scrollTop = scrollBarPos.value;
       });
       addEvent(text, "blur", function() { scrollBarPos.value = text.scrollTop });
     </script>
    </fieldset>
    <div id="help">
     <b>Note:</b> See <a href="<?cs var:$trac.href.wiki
?>/WikiFormatting">WikiFormatting</a> and <a href="<?cs var:$trac.href.wiki
?>/TracWiki">TracWiki</a> for help on editing wiki content.
    </div>
    <fieldset id="changeinfo">
     <legend>Change information</legend>
     <div class="field">
      <label>Your email or username:<br />
      <input id="author" type="text" name="author" size="30" value="<?cs
        var:wiki.author ?>" /></label>
     </div>
     <div class="field">
      <label>Comment about this change (optional):<br />
      <input id="comment" type="text" name="comment" size="60" value="<?cs
        var:wiki.comment?>" /></label>
     </div><br />
     <?cs if trac.acl.WIKI_ADMIN ?>
      <div class="options">
       <label><input type="checkbox" name="readonly" id="readonly"<?cs
         if wiki.readonly == "1"?>checked="checked"<?cs /if ?> />
       Page is read-only</label>
      </div>
     <?cs /if ?>
    </fieldset>
    <div class="buttons"><?cs
     if wiki.action == "collision" ?>
     <input type="submit" name="preview" value="Preview" disabled="" />&nbsp;
     <input type="submit" name="save" value="Submit changes" disabled="" />&nbsp;
     <?cs else ?>
     <input type="submit" name="preview" value="Preview" />&nbsp;
     <input type="submit" name="save" value="Submit changes" />&nbsp;
     <?cs /if ?>
     <input type="submit" name="cancel" value="Cancel" />
    </div>
    <script type="text/javascript" src="<?cs
      var:htdocs_location ?>js/wikitoolbar.js"></script>
   </form>
  <?cs /if ?>
  <?cs if wiki.action == "view" ?>
   <div class="wikipage">
    <div id="searchable"><?cs var:wiki.page_html ?></div>
   </div>
   <?cs if:len(wiki.attachments) ?>
    <h3 id="tkt-changes-hdr">Attachments</h3>
    <ul class="tkt-chg-list"><?cs
     each:attachment = wiki.attachments ?><li class="tkt-chg-change"><a href="<?cs
      var:attachment.href ?>"><?cs
      var:attachment.filename ?></a> (<?cs var:attachment.size ?>) -<?cs
      if:attachment.description ?><q><?cs var:attachment.description ?></q>,<?cs
      /if ?> added by <?cs var:attachment.author ?> on <?cs
      var:attachment.time ?>.</li><?cs
     /each ?>
    </ul>
  <?cs /if ?>
  <?cs if wiki.action == "view" && (trac.acl.WIKI_MODIFY || trac.acl.WIKI_DELETE)
      && (wiki.readonly == "0" || trac.acl.WIKI_ADMIN) ?>
   <div class="buttons"><?cs
    if:trac.acl.WIKI_MODIFY ?>
     <form method="get" action="<?cs var:wiki.current_href ?>"><div>
      <input type="hidden" name="action" value="edit" />
      <input type="submit" value="<?cs if:wiki.exists ?>Edit<?cs else ?>Create<?cs /if ?> this page" />
     </div></form><?cs
     if:wiki.exists ?>
      <form method="get" action="<?cs var:wiki.attach_href ?>"><div>
       <input type="hidden" name="action" value="new" />
       <input type="submit" value="Attach file" />
      </div></form><?cs
     /if ?><?cs
    /if ?><?cs
    if:wiki.exists && trac.acl.WIKI_DELETE ?>
     <form method="get" action="<?cs var:wiki.current_href ?>"><div id="delete">
      <input type="hidden" name="action" value="delete" />
      <input type="hidden" name="version" value="<?cs var:wiki.version ?>" />
      <input type="submit" name="delete_version" value="Delete this version" />
      <input type="submit" value="Delete page" />
     </div></form>
    <?cs /if ?>
   </div>
  <?cs /if ?>
  <script type="text/javascript">
   addHeadingLinks(document.getElementById("searchable"));
  </script>
 <?cs /if ?>
 <?cs /if ?>
</div>

<?cs include "footer.cs" ?>
