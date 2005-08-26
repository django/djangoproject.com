<?cs include "header.cs" ?>
<?cs include "macros.cs" ?>

<div id="ctxtnav" class="nav">
 <h2>Ticket Navigation</h2><?cs
 with:links = chrome.links ?>
  <ul><?cs
   if:len(links.prev) ?>
    <li class="first<?cs if:!len(links.up) && !len(links.next) ?> last<?cs /if ?>">
     &larr; <a href="<?cs var:links.prev.0.href ?>" title="<?cs
       var:links.prev.0.title ?>">Previous Ticket</a>
    </li><?cs
   /if ?><?cs
   if:len(links.up) ?>
    <li class="<?cs if:!len(links.prev) ?>first<?cs /if ?><?cs
                    if:!len(links.next) ?> last<?cs /if ?>">
     <a href="<?cs var:links.up.0.href ?>" title="<?cs
       var:links.up.0.title ?>">Back to Query</a>
    </li><?cs
   /if ?><?cs
   if:len(links.next) ?>
    <li class="<?cs if:!len(links.prev) && !len(links.up) ?>first <?cs /if ?>last">
     <a href="<?cs var:links.next.0.href ?>" title="<?cs
       var:links.next.0.title ?>">Next Ticket</a> &rarr;
    </li><?cs
   /if ?>
  </ul><?cs
 /with ?>
</div>

<div id="content" class="ticket">

 <h1>Ticket #<?cs var:ticket.id ?> <?cs
 if:ticket.type ?>(<?cs var:ticket.type ?>)<?cs /if ?></h1>

<div id="searchable">
<div id="ticket">
 <div class="date">
  <p title="<?cs var:ticket.opened ?>">Opened <?cs var:ticket.opened_delta ?> ago</p><?cs
  if:ticket.lastmod ?>
   <p title="<?cs var:ticket.lastmod ?>">Last modified <?cs var:ticket.lastmod_delta ?> ago</p>
  <?cs /if ?>
 </div>
 <h2 class="summary"><?cs var:ticket.summary ?></h2>
 <h3 class="status">Status: <strong><?cs var:ticket.status ?><?cs
  if:ticket.resolution ?> (<?cs var:ticket.resolution ?>)<?cs
  /if ?></strong></h3>
 <table class="properties">
  <tr>
   <th id="h_reporter">Reported by:</th>
   <td headers="h_reporter"><?cs var:ticket.reporter ?></td>
   <th id="h_owner">Assigned to:</th>
   <td headers="h_owner"><?cs var:ticket.owner ?><?cs
     if:ticket.status == 'assigned' ?> (accepted)<?cs /if ?></td>
  </tr><tr><?cs
  each:field = ticket.fields ?><?cs
   if:!field.skip ?><?cs
    set:num_fields = num_fields + 1 ?><?cs
   /if ?><?cs
  /each ?><?cs
  set:idx = 0 ?><?cs
  each:field = ticket.fields ?><?cs
   if:!field.skip ?><?cs set:fullrow = field.type == 'textarea' ?><?cs
    if:fullrow && idx % 2 ?><th></th><td></td></tr><tr><?cs /if ?>
    <th id="h_<?cs var:name(field) ?>"><?cs var:field.label ?>:</th>
    <td<?cs if:fullrow ?> colspan="3"<?cs /if ?> headers="h_<?cs
      var:name(field) ?>"><?cs var:ticket[name(field)] ?></td><?cs 
    if:idx % 2 || fullrow ?></tr><tr><?cs 
    elif:idx == num_fields - 1 ?><th></th><td></td><?cs
    /if ?><?cs set:idx = idx + #fullrow + 1 ?><?cs
   /if ?><?cs
  /each ?></tr>
 </table>
 <?cs if:ticket.description ?><div class="description">
  <?cs var:ticket.description.formatted ?>
 </div><?cs /if ?>
</div>

<?cs if:ticket.attach_href || len(ticket.attachments) ?>
<h2>Attachments</h2><?cs
 if:len(ticket.attachments) ?><div id="attachments">
  <dl class="attachments"><?cs each:attachment = ticket.attachments ?>
   <dt><a href="<?cs var:attachment.href ?>" title="View attachment"><?cs
   var:attachment.filename ?></a> (<?cs var:attachment.size ?>) - added by <em><?cs
   var:attachment.author ?></em> on <?cs
   var:attachment.time ?>.</dt><?cs
   if:attachment.description ?>
    <dd><?cs var:attachment.description ?></dd><?cs
   /if ?><?cs
  /each ?></dl><?cs
 /if ?><?cs
 if:ticket.attach_href ?>
  <form method="get" action="<?cs var:ticket.attach_href ?>"><div>
   <input type="hidden" name="action" value="new" />
   <input type="submit" value="Attach File" />
  </div></form><?cs
 /if ?><?cs if:len(ticket.attachments) ?></div><?cs /if ?>
<?cs /if ?>

<?cs if:len(ticket.changes) ?><h2>Change History</h2>
<div id="changelog"><?cs
 each:change = ticket.changes ?>
  <h3 id="change_<?cs var:name(change) ?>" class="change"><?cs
   var:change.date ?>: Modified by <?cs var:change.author ?></h3><?cs
  if:len(change.fields) ?>
   <ul class="changes"><?cs
   each:field = change.fields ?>
    <li><strong><?cs var:name(field) ?></strong> <?cs
    if:name(field) == 'attachment' ?><em><?cs var:field.new ?></em> added<?cs
    elif:field.old && field.new ?>changed from <em><?cs
     var:field.old ?></em> to <em><?cs var:field.new ?></em><?cs
    elif:!field.old && field.new ?>set to <em><?cs var:field.new ?></em><?cs
    elif:field.old && !field.new ?>deleted<?cs
    else ?>changed<?cs
    /if ?>.</li>
    <?cs
   /each ?>
   </ul><?cs
  /if ?>
  <div class="comment"><?cs var:change.comment ?></div><?cs
 /each ?></div><?cs
/if ?>

<?cs if:trac.acl.TICKET_CHGPROP || trac.acl.TICKET_APPEND ?>
<form action="<?cs var:ticket.href ?>#preview" method="post">
 <input type="hidden" name="ts" value="<?cs var:ticket.ts ?>"/>
 <hr />
 <h3><a name="edit" onfocus="document.getElementById('comment').focus()">Add/Change #<?cs
   var:ticket.id ?> (<?cs var:ticket.summary ?>)</a></h3>
 <div class="field">
  <label for="author">Your email or username:</label><br />
  <input type="text" id="author" name="author" size="40"
    value="<?cs var:ticket.reporter_id ?>" /><br />
 </div>
 <div class="field">
  <fieldset class="iefix">
   <label for="comment">Comment (you may use <a tabindex="42" href="<?cs
     var:trac.href.wiki ?>/WikiFormatting">WikiFormatting</a> here):</label><br />
   <p><textarea id="comment" name="comment" class="wikitext" rows="10" cols="78"><?cs
     var:ticket.comment ?></textarea></p>
  </fieldset><?cs
  if ticket.comment_preview ?>
   <fieldset id="preview">
    <legend>Comment Preview</legend>
    <?cs var:ticket.comment_preview ?>
   </fieldset><?cs
  /if ?>
 </div>

 <?cs if:trac.acl.TICKET_CHGPROP ?><fieldset id="properties">
  <legend>Change Properties</legend>
  <table><tr>
   <th><label for="summary">Summary:</label></th>
   <td class="fullrow" colspan="3"><input type="text" id="summary" name="summary" value="<?cs
     var:ticket.summary ?>" size="70" />
   </tr><?cs
   if:len(ticket.fields.type.options) ?>
   <tr>
    <th><label for="type">Type:</label></th>
    <td><?cs 
     call:hdf_select(ticket.fields.type.options, 'type', ticket.type, 0) ?>
    </td>
   </tr><?cs
   /if ?><?cs
   if:trac.acl.TICKET_ADMIN ?><tr>
    <th><label for="description">Description:</label></th>
    <td class="fullrow" colspan="3">
     <textarea id="description" name="description" class="wikitext" rows="10" cols="68"><?cs
        var:ticket.description ?></textarea>
    </td>
   </tr><tr>
    <th><label for="reporter">Reporter:</label></th>
    <td class="fullrow" colspan="3"><input type="text" value="<?cs 
      var:ticket.reporter ?>" id="reporter" name="reporter" size="70" /></td>
   </tr><?cs
   /if ?>
  <tr><?cs set:num_fields = 0 ?><?cs
  each:field = ticket.fields ?><?cs
   if:!field.skip ?><?cs
    set:num_fields = num_fields + 1 ?><?cs
   /if ?><?cs
  /each ?><?cs set:idx = 0 ?><?cs
   each:field = ticket.fields ?><?cs
    if:!field.skip ?><?cs set:fullrow = field.type == 'textarea' ?><?cs
     if:fullrow && idx % 2 ?><?cs set:idx = idx + 1 ?><th class="col2"></th><td></td></tr><tr><?cs /if ?>
     <th class="col<?cs var:idx % 2 + 1 ?>"><?cs
       if:field.type != 'radio' ?><label for="<?cs var:name(field) ?>"><?cs
       /if ?><?cs alt:field.label ?><?cs var:field.name ?><?cs /alt ?>:<?cs
       if:field.type != 'radio' ?></label><?cs /if ?></th>
     <td<?cs if:fullrow ?> colspan="3"<?cs /if ?>><?cs
      if:field.type == 'text' ?><input type="text" id="<?cs
        var:name(field) ?>" name="<?cs
        var:name(field) ?>" value="<?cs var:ticket[name(field)] ?>" /><?cs
      elif:field.type == 'select' ?><select id="<?cs
        var:name(field) ?>" name="<?cs
        var:name(field) ?>"><?cs
        if:field.optional ?><option></option><?cs /if ?><?cs
        each:option = field.options ?><option<?cs
         if:option == ticket[name(field)] ?> selected="selected"<?cs /if ?>><?cs
         var:option ?></option><?cs
        /each ?></select><?cs
      elif:field.type == 'checkbox' ?><input type="hidden" name="checkbox_<?cs
        var:name(field) ?>" /><input type="checkbox" id="<?cs
        var:name(field) ?>" name="<?cs
        var:name(field) ?>" value="1"<?cs
        if:ticket[name(field)] ?> checked="checked"<?cs /if ?> /><?cs
      elif:field.type == 'textarea' ?><textarea id="<?cs
        var:name(field) ?>" name="<?cs
        var:name(field) ?>"<?cs
        if:field.height ?> rows="<?cs var:field.height ?>"<?cs /if ?><?cs
        if:field.width ?> cols="<?cs var:field.width ?>"<?cs /if ?>><?cs
        var:ticket[name(field)] ?></textarea><?cs
      elif:field.type == 'radio' ?><?cs set:optidx = 0 ?><?cs
       each:option = field.options ?><label><input type="radio" id="<?cs
         var:name(field) ?>" name="<?cs
         var:name(field) ?>" value="<?cs var:option ?>"<?cs
         if:ticket[name(field)] == option ?> checked="checked"<?cs /if ?> /> <?cs
         var:option ?></label> <?cs set:optidx = optidx + 1 ?><?cs
        /each ?><?cs
      /if ?></td><?cs
     if:idx % 2 || fullrow ?></tr><tr><?cs 
     elif:idx == num_fields - 1 ?><th class="col2"></th><td></td><?cs
     /if ?><?cs set:idx = idx + #fullrow + 1 ?><?cs
    /if ?><?cs
   /each ?></tr>
  </table>
 </fieldset><?cs /if ?>

 <?cs if:ticket.actions.accept || ticket.actions.reopen ||
         ticket.actions.resolve || ticket.actions.reassign ?>
 <fieldset id="action">
  <legend>Action</legend><?cs
  if:!ticket.action ?><?cs set:ticket.action = 'leave' ?><?cs
  /if ?><?cs
  def:action_radio(id) ?>
   <input type="radio" id="<?cs var:id ?>" name="action" value="<?cs
     var:id ?>"<?cs if:ticket.action == id ?> checked="checked"<?cs
     /if ?> /><?cs
  /def ?>
  <?cs call:action_radio('leave') ?>
   <label for="leave">leave as <?cs var:ticket.status ?></label><br /><?cs
  if:ticket.actions.accept ?><?cs
   call:action_radio('accept') ?>
   <label for="accept">accept ticket</label><br /><?cs
  /if ?><?cs
  if:ticket.actions.reopen ?><?cs
   call:action_radio('reopen') ?>
   <label for="reopen">reopen ticket</label><br /><?cs
  /if ?><?cs
  if:ticket.actions.resolve ?><?cs
   call:action_radio('resolve') ?>
   <label for="resolve">resolve</label><?cs
   if:len(ticket.fields.resolution.options) ?>
    <label for="resolve_resolution">as:</label>
    <?cs call:hdf_select(ticket.fields.resolution.options, "resolve_resolution",
                         ticket.resolve_resolution, 0) ?><br /><?cs
   /if ?><?cs
  /if ?><?cs
  if:ticket.actions.reassign ?><?cs
   call:action_radio('reassign') ?>
   <label for="reassign">reassign</label>
   <label>to:<?cs
   if:len(ticket.fields.owner.options) ?><?cs
    call:hdf_select(ticket.fields.owner.options, "reassign_owner",
                    ticket.reassign_owner, 1) ?><?cs
   else ?>
    <input type="text" id="reassign_owner" name="reassign_owner" size="40" value="<?cs
      var:ticket.reassign_owner ?>" /><?cs
   /if ?></label><?cs
  /if ?><?cs
  if ticket.actions.resolve || ticket.actions.reassign ?>
   <script type="text/javascript"><?cs
    each:action = ticket.actions ?>
     var <?cs var:name(action) ?> = document.getElementById("<?cs var:name(action) ?>");<?cs
    /each ?>
     var updateActionFields = function() {
       <?cs if:ticket.actions.resolve ?> enableControl('resolve_resolution', resolve.checked);<?cs /if ?>
       <?cs if:ticket.actions.reassign ?> enableControl('reassign_owner', reassign.checked);<?cs /if ?>
     };
     addEvent(window, 'load', updateActionFields);<?cs
     each:action = ticket.actions ?>
      addEvent(<?cs var:name(action) ?>, 'click', updateActionFields);<?cs
     /each ?>
   </script><?cs
  /if ?>
 </fieldset><?cs
 else ?>
  <input type="hidden" name="action" value="leave" /><?cs
 /if ?>

 <script type="text/javascript" src="<?cs
   var:htdocs_location ?>js/wikitoolbar.js"></script>

 <div class="buttons">
  <input type="submit" name="preview" value="Preview" />&nbsp;
  <input type="submit" value="Submit changes" />
 </div>
</form>
<?cs /if ?>

 </div>
</div>
<?cs include "footer.cs"?>
