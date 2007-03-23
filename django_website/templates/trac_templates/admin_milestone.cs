<h2>Manage Milestones</h2><?cs

if:admin.milestone.name ?>
 <form class="mod" id="modmil" method="post">
  <fieldset>
   <legend>Modify Milestone:</legend>
   <div class="field">
    <label>Name:<br /> <input type="text" name="name"value="<?cs
      var:admin.milestone.name ?>" /></label>
   </div>
   <div class="field">
    <label>Due:<br />
     <input type="text" id="duedate" name="duedate" size="<?cs
       var:len(admin.date_hint) ?>" value="<?cs
       var:admin.milestone.duedate ?>" title="Format: <?cs var:admin.date_hint ?>" />
     <em>Format: <?cs var:admin.date_hint ?></em>
    </label>
   </div>
   <div class="field">
    <label>
     <input type="checkbox" id="completed" name="completed"<?cs
       if:admin.milestone.completed ?> checked="checked"<?cs /if ?> />
     Completed:<br />
    </label>
    <label>
     <input type="text" id="completeddate" name="completeddate" size="<?cs
       var:len(admin.date_hint) ?>" value="<?cs
       alt:admin.milestone.completed_date ?><?cs
        var:admin.datetime_now ?><?cs
       /alt ?>" title="Format: <?cs
       var:admin.datetime_hint ?>" />
     <em>Format: <?cs var:admin.datetime_hint ?></em>
    </label>
    <script type="text/javascript">
      var completed = document.getElementById("completed");
      var enableCompletedDate = function() {
        enableControl("completeddate", completed.checked);
      };
      addEvent(window, "load", enableCompletedDate);
      addEvent(completed, "click", enableCompletedDate);
    </script>
   </div>
   <div class="field">
    <fieldset class="iefix">
     <label for="description">Description (you may use <a tabindex="42" href="<?cs
       var:trac.href.wiki ?>/WikiFormatting">WikiFormatting</a> here):</label>
     <p><textarea id="description" name="description" class="wikitext" rows="6" cols="60"><?cs
       var:admin.milestone.description ?></textarea></p>
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

 <form class="addnew" id="addmil" method="post">
  <fieldset>
   <legend>Add Milestone:</legend>
   <div class="field">
    <label>Name:<br /><input type="text" name="name" id="name" /></label>
   </div>
   <div class="field">
    <label>
     Due:<br />
     <input type="text" name="duedate"
       title="Format: <?cs var:admin.date_hint ?>" /><br />
     <em>Format: <?cs var:admin.date_hint ?></em>
    </label>
   </div>
   <div class="buttons">
    <input type="submit" name="add" value="Add" />
   </div>
  </fieldset>
 </form><?cs

 if:len(admin.milestones) ?><form method="POST">
  <table class="listing" id="millist">
   <thead>
    <tr><th class="sel">&nbsp;</th><th>Name</th>
    <th>Time</th><th>Default</th></tr>
   </thead><tbody><?cs
   each:milestone = admin.milestones ?>
   <tr>
    <td><input type="checkbox" name="sel" value="<?cs var:milestone.name ?>" /></td>
    <td><a href="<?cs var:milestone.href ?>"><?cs var:milestone.name ?></a></td>
    <td><?cs var:milestone.duedate ?></td>
     <td class="default"><input type="radio" name="default" value="<?cs
       var:milestone.name ?>"<?cs
       if:milestone.is_default ?> checked="checked" <?cs /if ?>></td>
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
