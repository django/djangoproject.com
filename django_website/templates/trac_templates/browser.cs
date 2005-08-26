<?cs set:html.stylesheet = 'css/browser.css' ?>
<?cs include: "header.cs"?>
<?cs include "macros.cs"?>

<div id="ctxtnav" class="nav">
 <ul>
  <li class="last"><a href="<?cs var:browser.log_href ?>">Revision Log</a></li>
 </ul>
</div>

<div id="content" class="browser">
 <?cs call:browser_path_links(browser.path, browser) ?>

 <div id="jumprev">
  <form action="<?cs var:browser_current_href ?>" method="get">
   <div>
    <label for="rev">View revision:</label>
    <input type="text" id="rev" name="rev" value="<?cs
      var:browser.revision?>" size="4" />
   </div>
  </form>
 </div>

 <table class="listing" id="dirlist">
  <thead>
   <tr>
    <th class="name<?cs if:browser.order == "name" ?> <?cs
      var:browser.order_dir ?><?cs /if ?>"><a title="Sort by name<?cs
      if:browser.order == "name" && browser.order_dir == "asc" ?> (descending)<?cs
      /if ?>" href="<?cs var:browser.current_href?>?order=name<?cs
      if:browser.order == "name" && browser.order_dir == "asc" ?>&desc=1<?cs
      /if ?>">Name</a>
    </th>
    <th class="rev">Rev</th>
    <th class="age<?cs if:browser.order == "date" ?> <?cs
      var:browser.order_dir ?><?cs /if ?>"><a title="Sort by age<?cs
      if:browser.order == "date" && browser.order_dir == "asc" ?> (descending)<?cs
      /if ?>" href="<?cs var:browser.current_href?>?order=date<?cs
      if:browser.order == "date" && browser.order_dir == "asc" ?>&desc=1<?cs
      /if ?>">Age</a>
    </th>
    <th class="change">Last Change</th>
   </tr>
  </thead>
  <tbody>
   <?cs if:browser.path != "/" ?>
    <tr class="even">
     <td class="name" colspan="4">
      <a class="parent" title="Parent Directory" href="<?cs
        var:browser.parent_href ?>">../</a>
     </td>
    </tr>
   <?cs /if ?>
   <?cs each:item = browser.items ?>
    <tr class="<?cs if:name(item) % #2 ?>even<?cs else ?>odd<?cs /if ?>">
     <td class="name"><?cs
      if:item.is_dir ?><?cs
       if:item.permission ?>
        <a class="dir" title="Browse Directory" href="<?cs
          var:item.browser_href ?>"><?cs var:item.name ?></a><?cs
       else ?>
        <span class="dir" title="Access Denied" href=""><?cs
          var:item.name ?></span><?cs
       /if ?><?cs
      else ?><?cs
       if:item.permission != '' ?>    
        <a class="file" title="View File" href="<?cs
          var:item.browser_href ?>"><?cs var:item.name ?></a><?cs
       else ?>
        <span class="file" title="Access Denied" href=""><?cs
          var:item.name ?></span><?cs
       /if ?><?cs
      /if ?>
     </td>
     <td class="rev"><?cs if:item.permission != '' ?><a title="View Revision Log" href="<?cs
       var:item.log_href ?>"><?cs var:item.created_rev ?></a><?cs else ?><?cs var:item.created_rev ?><?cs /if ?></td>
     <td class="age"><span title="<?cs var:item.date ?>"><?cs
       var:item.age ?></span></td>
     <td class="change">
      <span class="author"><?cs var:item.author ?>:</span>
      <span class="change"><?cs var:item.change ?></span>
     </td>
    </tr>
   <?cs /each ?>
  </tbody>
 </table>

 <div id="help">
  <strong>Note:</strong> See <a href="<?cs var:trac.href.wiki
  ?>/TracBrowser">TracBrowser</a> for help on using the browser.
 </div>

</div>
<?cs include:"footer.cs"?>
