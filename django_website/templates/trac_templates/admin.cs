<?cs include "header.cs"?>
<?cs include "macros.cs"?>

<div id="ctxtnav"></div>

<div id="content" class="admin">

 <h1>Administration</h1>

 <div class="tabs"><?cs set:cur_cat_id = '' ?><ul><?cs
  each:page = admin.pages ?><?cs
   if:page.cat_id != cur_cat_id ?><?cs
    if:name(page) != 0 ?></ul></li><?cs /if ?><li<?cs
     if:page.cat_id == admin.active_cat ?> class="active"<?cs
     /if ?>><?cs var:page.cat_label ?><ul><?cs
   /if ?><?cs
   if:page.page_id == admin.active_page ?><li class="active"><?cs
    var:page.page_label ?></li><?cs
   else ?><li><a href="<?cs var:page.href ?>"><?cs
    var:page.page_label ?></a></li><?cs
   /if ?><?cs
   set:cur_cat_id = page.cat_id ?><?cs
  /each ?></ul><li/></ul></div>

 <div class="tabcontents">
  <?cs if:admin.page_template ?><?cs
   include admin.page_template ?><?cs
  else ?><?cs
   var:admin.page_content ?><?cs
  /if ?>
  <br style="clear: right"/>
 </div>
</div>

<?cs include "footer.cs"?>
