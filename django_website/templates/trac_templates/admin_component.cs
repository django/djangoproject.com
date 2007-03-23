<h2>Manage Components</h2><?cs

if admin.component.name ?>
 <form class="mod" id="modcomp" method="post">
  <fieldset>
   <legend>Modify Component:</legend>
   <div class="field">
    <label>Name:<br /><input type="text" name="name" value="<?cs
      var:admin.component.name ?>"></label>
   </div>
   <div class="field">
    <label>Owner:<br /><?cs
     if:len(admin.owners) ?><?cs
      call:hdf_select(admin.owners, "owner", admin.component.owner, 0) ?><?cs
     else ?><input type="text" name="owner" value="<?cs
      var:admin.component.owner ?>" /><?cs
     /if ?></label>
   </div>
   <div class="field">
    <fieldset class="iefix">
     <label for="description">Description (you may use <a tabindex="42" href="<?cs
       var:trac.href.wiki ?>/WikiFormatting">WikiFormatting</a> here):</label>
     <p><textarea id="description" name="description" class="wikitext" rows="6" cols="60"><?cs
       var:admin.component.description ?></textarea></p>
    </fieldset>
   </div>
   <script type="text/javascript" src="<?cs
     var:chrome.href ?>/common/js/wikitoolbar.js"></script>
   <div class="buttons">
    <input type="submit" name="cancel" value="Cancel" />
    <input type="submit" name="save" value="Save" />
   </div>
  </fieldset>
 </form><?cs

else ?>
 <form class="addnew" id="addcomp" method="post">
  <fieldset>
   <legend>Add Component:</legend>
   <div class="field">
    <label>Name:<br /><input type="text" name="name" /></label>
   </div>
   <div class="field">
    <label>Owner:<br /><?cs
     if:len(admin.owners) ?><?cs
      call:hdf_select(admin.owners, "owner", "", 0) ?><?cs
     else ?><input type="text" name="owner" /><?cs
     /if ?></label>
   </div>
   <div class="buttons">
    <input type="submit" name="add" value="Add">
   </div>
  </fieldset>
 </form><?cs

 if:len(admin.components) ?><form method="POST">
  <table class="listing" id="complist">
   <thead>
    <tr><th class="sel">&nbsp;</th><th>Name</th>
    <th>Owner</th><th>Default</th></tr>
   </thead><?cs
   each:comp = admin.components ?>
    <tr>
     <td class="sel"><input type="checkbox" name="sel" value="<?cs
       var:comp.name ?>" /></td>
     <td class="name"><a href="<?cs var:comp.href?>"><?cs
       var:comp.name ?></a></td>
     <td class="owner"><?cs var:comp.owner ?></td>
     <td class="default"><input type="radio" name="default" value="<?cs
       var:comp.name ?>"<?cs
       if:comp.is_default ?> checked="checked" <?cs /if ?>></td>
    </tr><?cs
   /each ?>
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
