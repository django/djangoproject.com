<?cs set:html.stylesheet = 'css/code.css' ?>
<?cs include "header.cs" ?>
<?cs include "macros.cs" ?>

<div id="ctxtnav" class="nav"></div>

<div id="content" class="attachment">

 <h3>Add Attachment to <a href="<?cs
   var:file.attachment_parent_href?>"><?cs var:file.attachment_parent?></a></h3>
 <form id="attachment" method="post" enctype="multipart/form-data" action="<?cs
   var:cgi_location ?>">
  <div class="field">
   <label for="file">File:</label>
   <input type="file" id="file" name="attachment" />
  </div>
  <fieldset>
   <legend>Attachment Info</legend>
   <div class="field">
    <label for="author">Your email or username:</label><br />
    <input type="text" id="author" name="author" class="textwidget" size="30"
        value="<?cs var:attachment.author?>" />
   </div>
   <div class="field">
    <label for="description">Description of the file (optional):</label><br />
    <input type="text" id="description" name="description" class="textwidget"
        size="60" />
   </div><br />
  </fieldset>
  <div class="buttons">
   <input type="hidden" name="mode" value="attachment" />
   <input type="hidden" name="type" value="<?cs var:attachment.type ?>" />
   <input type="hidden" name="id" value="<?cs var:attachment.id ?>" />
   <input type="submit" value="Add Attachment" />
   <input type="submit" name="cancel" value="Cancel" />
  </div>
 </form>

</div>
<?cs include "footer.cs"?>
