<?cs set:html.stylesheet = 'css/report.css' ?>
<?cs include "header.cs" ?>
<?cs include "macros.cs" ?>

<div id="ctxtnav" class="nav">
 <h2>Report Navigation</h2>
 <ul>
  <?cs if report.edit_href || report.copy_href || report.delete_href ?>
  <li><b>This report:</b>
   <ul>
    <?cs if report.edit_href
      ?><li <?cs if !report.delete_href && !report.copy_href ?>class="last"<?cs /if
        ?>><a href="<?cs var:report.edit_href ?>">Edit</a></li><?cs
     /if ?><?cs
     if report.copy_href ?><li <?cs if !report.delete_href ?>class="last"<?cs /if
        ?>><a href="<?cs var:report.copy_href ?>">Copy</a></li><?cs /if ?><?cs
    if report.delete_href ?><li class="last"><a href="<?cs var:report.delete_href ?>">Delete</a></li><?cs /if ?></ul></li>
  <?cs /if ?>
  <?cs if:report.create_href ?>
   <li><a href="<?cs var:report.create_href ?>">New Report</a></li>
  <?cs /if ?>
  <li class="last"><a href="<?cs var:$trac.href.query ?>">Custom Query</a></li>
 </ul>
</div>

<div id="content" class="report">

<?cs if report.message ?>
 <div class="error"><?cs var report.message ?></div>
<?cs else ?>
 <?cs def:report_hdr(header) ?>
   <?cs if $header ?>
     <?cs if idx > 0 ?>
       </table>
     <?cs /if ?>
   <?cs /if ?>
   <?cs if:header ?><h2><?cs var:header ?></h2><?cs /if ?>
   <?cs if $report.id == -1 ?>
     <table id="reportlist" class="listing">
   <?cs else ?>
     <table id="tktlist" class="listing">
   <?cs /if ?>
    <thead>
     <tr>
       <?cs set numcols = #0 ?>
       <?cs each header = report.headers ?>
         <?cs if $header.fullrow ?>
           </tr><tr><th colspan="100"><?cs var:header ?></th>
         <?cs else ?>
           <?cs if $report.sorting.enabled ?>
             <?cs set vars='' ?>
             <?cs each arg = report.var ?>
               <?cs set vars = vars + '&amp;' + name(arg) + '=' + arg ?>
             <?cs /each ?>
             <?cs set sortValue = '' ?>
             <?cs if $header.asc == '1' ?>
               <?cs set sortValue = '?sort='+$header.real+'&amp;asc=0' ?>
             <?cs else ?>
               <?cs set sortValue = '?sort='+$header.real+'&amp;asc=1' ?>
             <?cs /if ?>
             <?cs if $header ?>
             <th><a href="<?cs var:sortValue ?><?cs var:vars ?>"><?cs var:header ?></a></th>
             <?cs /if ?>
           <?cs elif $header ?>
             <th><?cs var:header ?></th>
           <?cs /if ?>
           <?cs if $header.breakrow ?>
              </tr><tr>
           <?cs /if ?>
         <?cs /if ?>
         <?cs set numcols = numcols + #1 ?>
       <?cs /each ?>
     </tr>
    </thead>
 <?cs /def ?>
 
 <?cs def:report_cell(class,contents) ?>
   <?cs if $cell.fullrow ?>
     </tr><tr class="<?cs var:row_class ?>" style="<?cs var: row_style ?>;border: none; padding: 0;">
      <td class="fullrow" colspan="100">
       <?cs var:$contents ?><hr />
      </td>
   <?cs else ?>
   <td <?cs if $cell.breakrow || $col == $numcols ?>colspan="100" <?cs /if
 ?>class="<?cs var:$class ?>"><?cs if $contents ?><?cs var:$contents ?><?cs /if ?></td>
 
 <?cs if $cell.breakafter ?>
     </tr><tr class="<?cs var: row_class ?>" style="<?cs var: row_style ?>;border: none; padding: 0">
 <?cs /if ?>
   <?cs /if ?>
   <?cs set col = $col + #1 ?>
 <?cs /def ?>
 
 <?cs set idx = #0 ?>
 <?cs set group = '' ?>
 
 <?cs if:report.mode == "list" ?>
  <h1><?cs var:title ?><?cs
   if:report.numrows && report.id != -1 ?><span class="numrows"> (<?cs
    var:report.numrows ?> matches)</span><?cs
   /if ?></h1>
  <?cs if:report.description ?><div id="description"><?cs
    var:report.description ?></div><?cs
   /if ?>

     <?cs each row = report.items ?>
       <?cs if group != row.__group__ || idx == #0 ?>
         <?cs if:idx != #0 ?></tbody><?cs /if ?>
         <?cs set group = row.__group__ ?>
         <?cs call:report_hdr(group) ?>
         <tbody>
       <?cs /if ?>

       <?cs if row.__color__ ?>
         <?cs set rstem='color'+$row.__color__ +'-' ?>
       <?cs else ?>
        <?cs set rstem='' ?>
       <?cs /if ?>
       <?cs if idx % #2 ?>
         <?cs set row_class=$rstem+'even' ?>
       <?cs else ?>
         <?cs set row_class=$rstem+'odd' ?>
       <?cs /if ?>

       <?cs set row_style='' ?>
       <?cs if row.__bgcolor__ ?>
         <?cs set row_style='background: ' + row.__bgcolor__ + ';' ?>
       <?cs /if ?>
       <?cs if row.__fgcolor__ ?>
         <?cs set row_style=$row_style + 'color: ' + row.__fgcolor__ + ';' ?>
       <?cs /if ?>
       <?cs if row.__style__ ?>
         <?cs set row_style=$row_style + row.__style__ + ';' ?>
       <?cs /if ?>

       <tr class="<?cs var: row_class ?>" style="<?cs var: row_style ?>">
       <?cs set idx = idx + #1 ?>
       <?cs set col = #0 ?>
       <?cs each cell = row ?>
         <?cs if cell.hidden || cell.hidehtml ?>
         <?cs elif name(cell) == "ticket" ?>
           <?cs call:report_cell('ticket',
                                 '<a title="View ticket" href="'+
                                 $cell.ticket_href+'">#'+$cell+'</a>') ?>
         <?cs elif name(cell) == "summary" ?>
           <?cs call:report_cell('summary', '<a title="View ticket" href="'+
                                 $cell.ticket_href+'">'+$cell+'</a>') ?>
         <?cs elif name(cell) == "report" ?>
           <?cs call:report_cell('report',
                '<a title="View report" href="'+$cell.report_href+'">{'+$cell+'}</a>') ?>
           <?cs set:report_href=$cell.report_href ?>
         <?cs elif name(cell) == "time" ?>
           <?cs call:report_cell('date', $cell.date) ?>
         <?cs elif name(cell) == "date" || name(cell) == "created" || name(cell) == "modified" ?>
           <?cs call:report_cell('date', $cell.date) ?>
         <?cs elif name(cell) == "datetime"  ?>
           <?cs call:report_cell('date', $cell.datetime) ?>
         <?cs elif name(cell) == "description" ?>
           <?cs call:report_cell('', $cell.parsed) ?>
         <?cs elif name(cell) == "title" && $report.id == -1 ?>
           <?cs call:report_cell('title',
                                 '<a  title="View report" href="'+
                                 $report_href+'">'+$cell+'</a>') ?>
         <?cs else ?>
           <?cs call:report_cell(name(cell), $cell) ?>
         <?cs /if ?>
       <?cs /each ?>
       </tr>
     <?cs /each ?>
    </tbody>
   </table>

   <?cs if $idx == #0 ?>
    <div id="report-notfound">No matches found.</div>
   <?cs /if ?>

 <?cs elif report.mode == "delete" ?>

  <h1><?cs var:title ?></h1>
  <form action="<?cs var:cgi_location ?>" method="post">
   <input type="hidden" name="mode" value="report" />
   <input type="hidden" name="id" value="<?cs var:report.id ?>" />
   <input type="hidden" name="action" value="confirm_delete" />
   <p><strong>Are you sure you want to delete this report?</strong></p>
   <div class="buttons">
    <input type="submit" name="cancel" value="Cancel" />
    <input type="submit" value="Delete Report" />
   </div>
  </form>
 
 <?cs elif report.mode == "editor" ?>
 
   <h1><?cs var:title ?></h1>
   
   <form action="<?cs var:cgi_location ?>" method="post">
    <div>
     <input type="hidden" name="mode" value="report" />
     <input type="hidden" name="id" value="<?cs var:report.id ?>" />
     <input type="hidden" name="action" value="<?cs var:report.action ?>" />
     <div class="field">
      <label for="title">Report Title:</label><br />
      <input type="text" id="title" name="title"
             value="<?cs var:report.title ?>" size="50" /><br />
     </div>
     <div class="field">
      <label for="description">
       Description:</label> (You may use <a tabindex="42" href="<?cs
         var:$trac.href.wiki ?>/WikiFormatting">WikiFormatting</a> here)
      </label><br />
      <textarea id="description" name="description" cols="85" rows="5"><?cs
        var:report.description ?></textarea>
      <?cs call:wiki_toolbar('description') ?>
     </div>
     <div class="field">
      <label for="sql">
       SQL Query for Report:</label><br />
      <textarea id="sql" name="sql" cols="85" rows="20"><?cs
        var:report.sql ?></textarea>
     </div>
     <div class="buttons">
      <input type="submit" value="Save" />
      <input type="submit" name="cancel" value="Cancel" />
     </div>
    </div>
   </form>
 <?cs /if?>
 
 <div id="help">
  <strong>Note:</strong> See <a href="<?cs
    var:trac.href.wiki ?>/TracReports">TracReports</a> for help on using and
  creating reports.
 </div>
 
<?cs /if ?><?cs #report.message ?>

</div>
<?cs include "footer.cs" ?>
