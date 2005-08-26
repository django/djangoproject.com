<?cs set:html.stylesheet = 'css/browser.css' ?>
<?cs include "header.cs"?>
<?cs include "macros.cs"?>

<div id="ctxtnav" class="nav">
 <ul>
  <li class="last"><a href="<?cs
    var:log.items.0.file_href ?>">View Latest Revision</a></li>
 </ul>
</div>

<div id="content" class="log">
 <?cs call:browser_path_links(log.path, log) ?>

 <div id="jumprev">
  <form action="<?cs var:browser_current_href ?>" method="get">
   <div>
    <label for="rev">View revision:</label>
    <input type="text" id="rev" name="rev" value="<?cs
      var:log.items.0.rev ?>" size="4" />
   </div>
  </form>
 </div>

 <table id="chglist" class="listing">
  <thead>
   <tr>
    <th class="data">Date</th>
    <th class="rev">Rev</th>
    <th class="chgset">Chgset</th>
    <th class="author">Author</th>
    <th class="summary">Log Message</th>
   </tr>
  </thead>
  <tbody>
   <?cs each:item = log.items ?>
    <tr class="<?cs if:name(item) % #2 ?>even<?cs else ?>odd<?cs /if ?>">
     <td class="date"><?cs var:item.date ?></td>
     <td class="rev">
      <a href="<?cs var:item.file_href ?>"><?cs var:item.rev ?></a>
     </td>
     <td class="chgset">
      <a class="block-link" href="<?cs var:item.changeset_href ?>"><?cs var:item.rev ?></a>
     </td>
     <td class="author"><?cs var:item.author ?></td>
     <td class="summary"><?cs var:item.log ?></td>
    </tr>
   <?cs /each ?>
  </tbody>
 </table>

</div>
<?cs include "footer.cs"?>
