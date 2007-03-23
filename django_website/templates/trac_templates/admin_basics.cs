<h2>Basic Settings</h2>

<form class="mod" id="modbasic" method="post">
 <fieldset>
  <legend>Project</legend>
  <div class="field">
   <label>Name:<br />
    <input type="text" name="name" value="<?cs var:admin.project.name ?>" />
   </label>
  </div>
  <div class="field">
   <label>URL:<br />
    <input type="text" name="url" size="48 "value="<?cs
      var:admin.project.url ?>" />
   </label>
  </div>
  <div class="field">
   <label>Description:<br />
    <textarea name="description" rows="3" cols="80"><?cs
      var:admin.project.description ?></textarea>
   </label>
  </div>
 </fieldset>
 <div class="buttons">
  <input type="submit" value="Apply changes">
 </div>
</form>
