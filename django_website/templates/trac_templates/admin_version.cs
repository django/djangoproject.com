<h2>Manage Versions</h2><?cs

if:admin.version.name ?>
 <form class="mod" id="modver" method="post">
  <fieldset>
   <legend>Modify Version:</legend>
   <div class="field">
    <label>Name:<br /> <input type="text" name="name"value="<?cs
      var:admin.version.name ?>" /></label>
   </div>
   <div class="field">
    <label>Time:<br />
     <input type="text" name="time" size="<?cs
       var:len(admin.date_hint) ?>" value="<?cs
       var:admin.version.time ?>" title="Format: <?cs var:admin.date_hint ?>" />
     <em>Format: <?cs var:admin.date_hint ?></em>
    </label>
   </div>
   <div class="field">
    <fieldset class="iefix">
     <label for="description">Description (you may use <a tabindex="42" href="<?cs
       var:trac.href.wiki ?>/WikiFormatting">WikiFormatting</a> here):</label>
     <p><textarea id="description" name="description" class="wikitext" rows="6" cols="60"><?cs
       var:admin.version.description ?></textarea></p>
    </fieldset>
   </div>
   <script type="text/javascript" src="<?cs
     var:chrome.href ?>/common/js/wikitoolbar.js"></script>
   <div class="buttons">
    <input type="submit" name="cancel" value="Cancel">
    <input type="submit" name="save" value="Save">
   </div>
  </fieldset>
 </form><?cs

else ?>

 <form class="addnew" id="addver" method="post">
  <fieldset>
   <legend>Add Version:</legend>
   <div class="field">
    <label>Name:<br /><input type="text" name="name" id="name" /></label>
   </div>
   <div class="field">
    <label>
     Time:<br />
     <input type="text" name="time"
       title="Format: <?cs var:admin.date_hint ?>" /><br />
     <em>Format: <?cs var:admin.date_hint ?></em>
    </label>
   </div>
   <div class="buttons">
    <input type="submit" name="add" value="Add" />
   </div>
  </fieldset>
 </form><?cs

 if:len(admin.versions) ?><form method="POST">
  <table class="listing" id="verlist">
   <thead>
    <tr><th class="sel">&nbsp;</th><th>Name</th>
    <th>Time</th><th>Default</th></tr>
   </thead><tbody><?cs
   each:ver = admin.versions ?>
   <tr>
    <td><input type="checkbox" name="sel" value="<?cs var:ver.name ?>" /></td>
    <td><a href="<?cs var:ver.href ?>"><?cs var:ver.name ?></a></td>
    <td><?cs var:ver.time ?></td>
    <td class="default"><input type="radio" name="default" value="<?cs
      var:ver.name ?>"<?cs
      if:ver.is_default ?> checked="checked" <?cs /if ?>></td>
   </tr><?cs
   /each ?></tbody>
  </table>
  <div class="buttons">
   <input type="submit" name="remove" value="Remove selected items" />
   <input type="submit" name="apply" value="Apply changes" />
  </div>
  <p class="help">You can remove all items from this list to completely hide
  this field from the user interface.</p>
 </form><?cs
 else ?>
  <p class="help">As long as you don't add any items to the list, this field
  will remain completely hidden from the user interface.</p><?cs
 /if ?><?cs

/if ?>
