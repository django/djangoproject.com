<?cs set:html.stylesheet = 'css/ticket.css' ?>
<?cs include "header.cs" ?>
<?cs include "macros.cs" ?>
<script type="text/javascript">
addEvent(window, 'load', function() { document.getElementById('summary').focus()}); 
</script>

<div id="ctxtnav" class="nav"></div>

<div id="content" class="ticket">

<h3>Create New Ticket:</h3>
<form id="newticket" action="<?cs var:cgi_location ?>#preview" method="post">
 <div class="field">
  <label for="reporter">Your email or username:</label><br />
  <input type="text" id="reporter" name="reporter" size="40" value="<?cs
    var:newticket.reporter ?>" /><br />
 </div>
 <div class="field">
  <label for="summary">Short summary:</label><br />
  <input id="summary" type="text" name="summary" size="80" value="<?cs var:newticket.summary ?>"/>
 </div>
 <div class="field">
  <label for="description">Full description (you may use <a tabindex="42" href="<?cs
    var:$trac.href.wiki ?>/WikiFormatting">WikiFormatting</a> here):</label><br />
  <textarea id="description" name="description" rows="10" cols="78"><?cs
    var:newticket.description ?></textarea><?cs
  call:wiki_toolbar('description') ?><?cs
  if:newticket.description_preview ?>
   <fieldset id="preview">
    <legend>Description Preview</legend>
    <?cs var:newticket.description_preview ?>
   </fieldset><?cs
  /if ?>
 </div>

 <fieldset id="properties">
  <legend>Ticket Properties</legend>
  <input type="hidden" name="mode" value="newticket" />
  <input type="hidden" name="action" value="create" />
  <input type="hidden" name="status" value="new" />
  <div class="col1">
   <label for="component">Component:</label><?cs
   call:hdf_select(newticket.components, "component", newticket.component) ?>
   <br />
   <label for="version">Version:</label><?cs
   call:hdf_select(newticket.versions, "version", newticket.version) ?>
   <br />
   <label for="severity">Severity:</label><?cs
   call:hdf_select(enums.severity, "severity", newticket.severity) ?>
   <br />
   <label for="keywords">Keywords:</label>
   <input type="text" id="keywords" name="keywords" size="20"
       value="<?cs var:newticket.keywords ?>" />
  </div>
  <div class="col2">
   <label for="priority">Priority:</label><?cs
   call:hdf_select(enums.priority, "priority", newticket.priority) ?><br />
   <label for="milestone">Milestone:</label><?cs
   call:hdf_select(newticket.milestones, "milestone", newticket.milestone) ?><br />
   <label for="owner">Assign to:</label>
   <input type="text" id="owner" name="owner" size="20" value="<?cs
     var:newticket.owner ?>" /><br />
   <label for="cc">Cc:</label>
   <input type="text" id="cc" name="cc" size="30" value="<?cs var:newticket.cc ?>" />
  </div>
  <?cs if:len(ticket.custom) ?><div class="custom">
   <?cs call:ticket_custom_props(ticket) ?>
  </div><?cs /if ?>
 </fieldset>

 <div class="buttons">
  <input type="submit" value="Preview" />&nbsp;
  <input type="submit" name="create" value="Submit ticket" />
 </div>
</form>

 <div id="help">
  <strong>Note:</strong> See <a href="<?cs var:$trac.href.wiki
  ?>/TracTickets">TracTickets</a> for help on using tickets.
 </div>
</div>

<?cs include "footer.cs" ?>
