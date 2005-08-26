<?cs set:html.stylesheet = 'css/ticket.css' ?>
<?cs include "header.cs" ?>
<?cs include "macros.cs" ?>

<div id="ctxtnav" class="nav">
 <h2>Ticket Navigation</h2>
 <ul><?cs
  if:len(links.prev) ?>
   <li class="first<?cs if:!len(links.next) ?> last<?cs /if ?>">
    <a href="<?cs var:links.prev.0.href ?>" title="<?cs
      var:links.prev.0.title ?>">Previous Ticket</a>
   </li><?cs
  /if ?><?cs
  if:len(links.next) ?>
   <li class="<?cs if:len(links.prev) ?>first <?cs /if ?>last">
    <a href="<?cs var:links.next.0.href ?>" title="<?cs
      var:links.next.0.title ?>">Next Ticket</a>
   </li><?cs
  /if ?>
 </ul>
</div>

<div id="content" class="ticket">
 <div id="searchable">
 <?cs def:ticketprop(label, name, value, fullrow) ?>
  <th id="h_<?cs var:name ?>"><?cs var:$label ?>:</th>
  <td headers="h_<?cs var:name ?>"<?cs if:fullrow ?> colspan="3"<?cs /if ?>><?cs
   if:$value ?><?cs var:$value ?><?cs else ?>&nbsp;<?cs
   /if ?></td><?cs if numprops % #2 && !$last_prop || fullrow ?>
 </tr><tr><?cs /if ?><?cs set numprops = $numprops + #1 - fullrow ?><?cs
 /def ?>

<div id="ticket">
 <div class="date"><?cs var:ticket.opened ?></div>
 <h1>Ticket #<?cs var:ticket.id ?> <?cs
 if:ticket.status == 'closed' ?>(Closed: <?cs var:ticket.resolution ?>)<?cs
 elif:ticket.status != 'new' ?>(<?cs var:ticket.status ?>)<?cs
 /if ?></h1>
 <h2><?cs var:ticket.summary ?></h2>
 <hr />
 <table><tr><?cs
  call:ticketprop("Priority", "priority", ticket.priority, 0) ?><?cs
  call:ticketprop("Reporter", "reporter", ticket.reporter, 0) ?><?cs
  call:ticketprop("Severity", "severity", ticket.severity, 0) ?><?cs
  if ticket.status == "assigned"?><?cs
   call:ticketprop("Assigned to", "assignee", ticket.owner + " (accepted)", 0) ?><?cs
  else ?><?cs
   call:ticketprop("Assigned to", "assignee", ticket.owner, 0) ?><?cs
  /if ?><?cs
  call:ticketprop("Component", "component", ticket.component, 0) ?><?cs
  call:ticketprop("Status", "status", ticket.status, 0) ?><?cs
  call:ticketprop("Version", "version", ticket.version, 0) ?><?cs
  call:ticketprop("Resolution", "resolution", ticket.resolution, 0) ?><?cs
  call:ticketprop("Milestone", "milestone", ticket.milestone, 0) ?><?cs
  set:last_prop = #1 ?><?cs
  call:ticketprop("Keywords", "keywords", ticket.keywords, 0) ?><?cs
  set:last_prop = #0 ?>
 </tr></table><?cs if ticket.custom.0.name ?>
 <hr />
 <table><tr><?cs each:prop = ticket.custom ?><?cs
   if:prop.type == "textarea" ?><?cs
    call:ticketprop(prop.label, prop.name, prop.value, 1) ?><?cs
   else ?><?cs
    call:ticketprop(prop.label, prop.name, prop.value, 0) ?><?cs
   /if?><?cs
  /each ?>
 </tr></table><?cs /if ?>
 <hr />
 <h3>Description<?cs if:ticket.reporter ?> by <?cs
   var:ticket.reporter ?><?cs /if ?>:</h3>
 <div class="description">
  <?cs var:ticket.description.formatted ?>
 </div>
</div>

<?cs if trac.acl.TICKET_MODIFY || ticket.attachments.0.name ?>
<h2>Attachments</h2><?cs
 if ticket.attachments.0.name ?><div id="attachments">
  <ul class="attachments"><?cs each:a = ticket.attachments ?>
   <li><a href="<?cs var:a.href ?>" title="View attachment"><?cs
   var:a.name ?></a> (<?cs var:a.size ?>) - <?cs
   if:a.descr ?><q><?cs var:a.descr ?></q>,<?cs
   /if ?> added by <em><?cs
   var:a.author ?></em> on <em><?cs
   var:a.time ?></em>.</li><?cs
  /each ?></ul><?cs
 /if ?><?cs
 if trac.acl.TICKET_MODIFY ?>
  <form method="get" action="<?cs var:ticket.attach_href ?>">
   <div><input type="submit" value="Attach File" /></div>
  </form><?cs
 /if ?><?cs if ticket.attachments.0.name ?></div><?cs /if ?>
<?cs /if ?>

<?cs if ticket.changes.0.time ?><h2>Changelog</h2>
<div id="changelog">
 <?cs set:comment = "" ?>
 <?cs set:curr_time = "" ?>
 <?cs set:curr_author = "" ?>
 <?cs each:change = ticket.changes ?><?cs
  if $change.time != $curr_time || $change.author != $curr_author ?><?cs
  if:name(change) > 0 ?></ul><?cs /if ?><?cs
   if $comment != "" ?>
    <div class="comment"><?cs var:$comment ?></div><?cs set:comment = "" ?><?cs
   /if ?>
   <?cs set:curr_time = $change.time ?>
   <?cs set:curr_author = $change.author ?>
   <h3 id="change_<?cs var:name(change) ?>" class="change"><?cs
     var:change.date ?>: Modified by <?cs var:curr_author ?></h3>
   <ul class="changes"><?cs
  /if ?><?cs
  if $change.field == "comment" ?><?cs
   set:$comment = $change.new ?><?cs
  elif $change.new == "" ?>
   <li><strong><?cs var:change.field ?></strong> cleared</li><?cs
  elif $change.field == "attachment" ?>
   <li><strong>attachment</strong> added: <?cs var:change.new ?></li><?cs
  elif $change.field == "description" ?>
   <li><strong><?cs var:change.field ?></strong> changed.</li><?cs
  elif $change.old == "" ?>
   <li><strong><?cs var:change.field ?></strong> set to <em><?cs var:change.new ?></em></li><?cs
  else ?>
   <li><strong><?cs var:change.field ?></strong> changed from <em><?cs
     var:change.old ?></em> to <em><?cs var:change.new ?></em></li><?cs
  /if ?><?cs
 /each ?></ul><?cs
 if $comment != "" ?>
  <div class="comment"><?cs var:$comment ?></div><?cs
 /if ?>
</div><?cs /if ?>

<?cs if $trac.acl.TICKET_MODIFY ?>
<form action="<?cs var:cgi_location ?>#preview" method="post">
 <hr />
 <h3><a name="edit" onfocus="document.getElementById('comment').focus()">Add/Change #<?cs
   var:ticket.id ?> (<?cs var:ticket.summary ?>)</a></h3>
 <div class="field">
  <input type="hidden" name="mode" value="ticket" />
  <input type="hidden" name="id"   value="<?cs var:ticket.id ?>" />
  <label for="author">Your email or username:</label><br />
  <input type="text" id="author" name="author" size="40"
    value="<?cs var:ticket.reporter_id ?>" /><br />
 </div>
 <div class="field">
  <fieldset class="iefix">
   <label for="comment">Comment (you may use <a tabindex="42" href="<?cs
     var:$trac.href.wiki ?>/WikiFormatting">WikiFormatting</a> here):</label><br />
   <p><textarea id="comment" name="comment" rows="10" cols="78"><?cs
     var:ticket.comment ?></textarea></p><?cs
   call:wiki_toolbar('comment') ?>
  </fieldset><?cs
  if ticket.comment_preview ?>
   <fieldset id="preview">
    <legend>Comment Preview</legend>
    <?cs var:ticket.comment_preview ?>
   </fieldset><?cs
  /if ?>
 </div>

 <fieldset id="properties">
  <legend>Change Properties</legend>
  <div class="main">
   <label for="summary">Summary:</label>
   <input id="summary" type="text" name="summary" size="70" value="<?cs
     var:ticket.summary ?>" /><?cs
   if $trac.acl.TICKET_ADMIN ?>
    <br />
    <label for="description">Description:</label>
    <div style="float: left">
     <textarea id="description" name="description" rows="10" cols="68"><?cs
       var:ticket.description ?></textarea>
     <?cs call:wiki_toolbar('description') ?>
    </div>
    <br style="clear: left" />
    <label for="reporter">Reporter:</label>
    <input id="reporter" type="text" name="reporter" size="70"
           value="<?cs var:ticket.reporter ?>" /><?cs
   /if ?>
  </div>
  <div class="col1">
   <label for="component">Component:</label><?cs
   call:hdf_select(ticket.components, "component", ticket.component) ?>
   <br />
   <label for="version">Version:</label><?cs
   call:hdf_select(ticket.versions, "version", ticket.version) ?>
   <br />
   <label for="severity">Severity:</label><?cs
   call:hdf_select(enums.severity, "severity", ticket.severity) ?>
   <br />
   <label for="keywords">Keywords:</label>
   <input type="text" id="keywords" name="keywords" size="20"
       value="<?cs var:ticket.keywords ?>" />
  </div>
  <div class="col2">
   <label for="priority">Priority:</label><?cs
   call:hdf_select(enums.priority, "priority", ticket.priority) ?><br />
   <label for="milestone">Milestone:</label><?cs
   call:hdf_select(ticket.milestones, "milestone", ticket.milestone) ?><br />
   <label for="owner">Assigned to:</label>
   <input type="text" id="owner" name="owner" size="20" value="<?cs
     var:ticket.owner ?>" disabled="disabled" /><br />
   <label for="cc">Cc:</label>
   <input type="text" id="cc" name="cc" size="30" value="<?cs var:ticket.cc ?>" />
  </div>
  <?cs if:len(ticket.custom) ?><div class="custom">
   <?cs call:ticket_custom_props(ticket) ?>
  </div><?cs /if ?>
 </fieldset>

 <fieldset id="action">
  <legend>Action</legend><?cs
  if:!ticket.action ?><?cs set:ticket.action = 'leave' ?><?cs
  /if ?><?cs
  def:action_radio(id) ?>
   <input type="radio" id="<?cs var:id ?>" name="action" value="<?cs
     var:id ?>"<?cs if:$ticket.action == $id ?> checked="checked"<?cs
     /if ?> /><?cs
  /def ?>
  <?cs call:action_radio('leave') ?>
  <label for="leave">leave as <?cs var:ticket.status ?></label><br /><?cs
  if $ticket.status == "new" ?>
   <?cs call:action_radio('accept') ?>
   <label for="accept">accept ticket</label><br /><?cs
  /if ?><?cs
  if $ticket.status == "closed" ?>
   <?cs call:action_radio('reopen') ?>
   <label for="reopen">reopen ticket</label><br /><?cs
  /if ?><?cs
  if $ticket.status == "new" || $ticket.status == "assigned" || $ticket.status == "reopened" ?>
   <?cs call:action_radio('resolve') ?>
   <label for="resolve">resolve</label>
   <label for="resolve_resolution">as:</label>
   <?cs call:hdf_select(enums.resolution, "resolve_resolution", args.resolve_resolution) ?><br />
   <?cs call:action_radio('reassign') ?>
   <label for="reassign">reassign</label>
   <label for="reassign_owner">to:</label>
   <input type="text" id="reassign_owner" name="reassign_owner" size="40" value="<?cs
     if:args.reassign_to ?><?cs var:args.reassign_to ?><?cs
     else ?><?cs var:trac.authname ?><?cs /if ?>" /><?cs
  /if ?><?cs
  if $ticket.status == "new" || $ticket.status == "assigned" || $ticket.status == "reopened" ?>
   <script type="text/javascript">
     var resolve = document.getElementById("resolve");
     var reassign = document.getElementById("reassign");
     var updateActionFields = function() {
       enableControl('resolve_resolution', resolve.checked);
       enableControl('reassign_owner', reassign.checked);
     };
     addEvent(window, 'load', updateActionFields);
     addEvent(document.getElementById("leave"), 'click', updateActionFields);<?cs
    if $ticket.status == "new" ?>
     addEvent(document.getElementById("accept"), 'click', updateActionFields);<?cs
    /if ?>
    addEvent(resolve, 'click', updateActionFields);
    addEvent(reassign, 'click', updateActionFields);
   </script><?cs
  /if ?>
 </fieldset>

 <div class="buttons">
  <input type="reset" value="Reset" />&nbsp;
  <input type="submit" name="preview" value="Preview" />&nbsp;
  <input type="submit" value="Submit changes" /> 
 </div>
</form>
<?cs /if ?>

 </div>
</div>
<?cs include "footer.cs"?>
