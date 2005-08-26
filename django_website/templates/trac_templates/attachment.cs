<?cs include "header.cs" ?>
<?cs include "macros.cs" ?>

<div id="ctxtnav" class="nav"></div>

<div id="content" class="attachment">

<?cs if:attachment.mode == 'new' ?>
 <h1>Add Attachment to <a href="<?cs var:attachment.parent.href?>"><?cs
   var:attachment.parent.name ?></a></h1>
 <form id="attachment" method="post" enctype="multipart/form-data" action="">
  <div class="field">
   <label>File:<br /><input type="file" name="attachment" /></label>
  </div>
  <fieldset>
   <legend>Attachment Info</legend>
   <div class="field">
    <label>Your email or username:<br />
    <input type="text" name="author" size="30" value="<?cs
      var:attachment.author?>" /></label>
   </div>
   <div class="field">
    <label>Description of the file (optional):<br />
    <input type="text" name="description" size="60" /></label
   </div>
   <div class="options">
    <label><input type="checkbox" name="replace" checked="checked" />
    Replace existing attachment of the same name</label>
   </div>
   <br />
  </fieldset>
  <div class="buttons">
   <input type="hidden" name="action" value="new" />
   <input type="hidden" name="type" value="<?cs var:attachment.parent.type ?>" />
   <input type="hidden" name="id" value="<?cs var:attachment.parent.id ?>" />
   <input type="submit" value="Add attachment" />
   <input type="submit" name="cancel" value="Cancel" />
  </div>
 </form>
<?cs elif:attachment.mode == 'delete' ?>
 <h1><a href="<?cs var:attachment.parent.href ?>"><?cs
   var:attachment.parent.name ?></a>: <?cs var:attachment.filename ?></h1>
 <p><strong>Are you sure you want to delete this attachment?</strong><br />
 This is an irreversible operation.</p>
 <div class="buttons">
  <form method="post" action=""><div id="delete">
   <input type="hidden" name="action" value="delete" />
   <input type="submit" name="cancel" value="Cancel" />
   <input type="submit" value="Delete attachment" />
  </div></form>
 </div><?cs else ?>
 <h1><a href="<?cs var:attachment.parent.href ?>"><?cs
   var:attachment.parent.name ?></a>: <?cs var:attachment.filename ?></h1>
 <div id="preview"><?cs
  if:attachment.preview ?>
   <?cs var:attachment.preview ?><?cs
  elif:attachment.max_file_size_reached ?>
   <strong>HTML preview not available</strong>, since file-size exceeds
   <?cs var:attachment.max_file_size  ?> bytes. You may <a href="<?cs
     var:attachment.raw_href ?>">download the file</a> instead.<?cs
  else ?>
   <strong>HTML preview not available</strong>. To view the file,
   <a href="<?cs var:attachment.raw_href ?>">download the file</a>.<?cs
  /if ?>
 </div>
 <?cs if:attachment.can_delete ?><div class="buttons">
  <form method="get" action=""><div id="delete">
   <input type="hidden" name="action" value="delete" />
   <input type="submit" value="Delete attachment" />
  </div></form>
 </div><?cs /if ?>
<?cs /if ?>

</div>
<?cs include "footer.cs"?>
