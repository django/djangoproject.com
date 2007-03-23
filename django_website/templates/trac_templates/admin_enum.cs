<h2>Manage <?cs var:admin.enum.label_plural ?></h2><?cs

if:admin.enum.name ?>
 <form class="mod" id="modenum" method="post">
  <fieldset>
   <legend>Modify <?cs var:admin.enum.label_singular ?></legend>
   <div class="field">
    <label>Name: <input type="text" name="name"value="<?cs
      var:admin.enum.name ?>" /></label>
   </div>
   <div class="buttons">
    <input type="submit" name="cancel" value="Cancel">
    <input type="submit" name="save" value="Save">
   </div>
  </fieldset>
 </form><?cs

else ?>

 <form class="addnew" id="addenum" method="post">
  <fieldset>
   <legend>Add <?cs var:admin.enum.label_singular ?></legend>
   <div class="field">
    <label>Name:<input type="text" name="name" id="name"></label>
   </div>
   <div class="buttons">
    <input type="submit" name="add" value="Add">
   </div>
  </fieldset>
 </form><?cs
 
 if:len(admin.enums) ?><form method="POST">
  <table class="listing" id="enumlist">
   <thead>
    <tr><th class="sel">&nbsp;</th><th>Name</th>
    <th>Default</th><th>Order</th></tr>
   </thead><tbody><?cs
   each:enum = admin.enums ?>
    <tr>
     <td><input type="checkbox" name="sel" value="<?cs var:enum.name ?>" /></td>
     <td><a href="<?cs var:enum.href ?>"><?cs var:enum.name ?></a></td>
     <td class="default"><input type="radio" name="default" value="<?cs
       var:enum.name ?>"<?cs
       if:enum.is_default ?> checked="checked" <?cs /if ?> /></td>
     <td class="default"><select name="value_<?cs var:enum.value ?>"><?cs
      each:other = admin.enums ?><option<?cs
       if:other.value == enum.value ?> selected="selected"<?cs
       /if ?>><?cs var:other.value ?></option><?cs
      /each ?>
     </select></td>
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
