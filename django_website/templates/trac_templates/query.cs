<?cs set:html.stylesheet = 'css/report.css' ?>
<?cs include:"header.cs" ?>
<?cs include:"macros.cs" ?>

<div id="ctxtnav" class="nav"><?cs if:query.edit_href ?>
 <ul>
  <li class="last"><a href="<?cs var:query.edit_href ?>">Refine Query</a></li>
 </ul>
<?cs /if ?></div>

<div id="content" class="query">
 <h1><?cs var:title ?></h1>

<?cs if:query.action == 'edit' ?>

<form id="query" action="<?cs var:cgi_location ?>" method="post">
 <fieldset>
  <input type="hidden" name="mode" value="query" />
  <input type="hidden" name="order" value="<?cs var:query.order ?>" />
  <?cs if:query.desc ?><input type="hidden" name="desc" value="1" /><?cs /if ?>
  <legend>Ticket Properties</legend>
  <div>
   <label for="component" accesskey="c">Component:</label>
   <?cs call:hdf_select_multiple(query.options.component, 'component', 4) ?>
  </div>
  <div>
   <label for="version" accesskey="v">Version:</label>
   <?cs call:hdf_select_multiple(query.options.version, 'version', 4) ?>
  </div>
  <div>
   <label for="severity" accesskey="e">Severity:</label>
   <?cs call:hdf_select_multiple(query.options.severity, 'severity', 4) ?>
  </div>
  <br />
  <div>
   <label for="keywords">Keywords contain:</label>
   <input type="text" name="keywords" id="keywords" accesskey="k" value="<?cs
     var:query.constraints.keywords.0 ?>" />
  </div>
  <br />
  <div>
   <label for="status" accesskey="s">Status:</label>
   <?cs call:hdf_select_multiple(query.options.status, 'status', 4) ?>
  </div>
  <div>
   <label for="resolution" accesskey="r">Resolution:</label>
   <?cs call:hdf_select_multiple(query.options.resolution, 'resolution', 4) ?>
   <script type="text/javascript">
     var status = document.getElementById("status");
     var updateResolution = function() {
       enableControl('resolution', status.selectedIndex == -1 ||
                                   status.selectedIndex >= 3);
     };
     addEvent(window, 'load', updateResolution);
     addEvent(status, 'change', updateResolution);
   </script>
  </div>
  <div>
   <label for="milestone" accesskey="m">Milestone:</label>
   <?cs call:hdf_select_multiple(query.options.milestone, 'milestone', 4) ?>
  </div>
  <div>
   <label for="priority" accesskey="p">Priority:</label>
   <?cs call:hdf_select_multiple(query.options.priority, 'priority', 4) ?>
  </div>
  <br />
  <div>
   <label for="owner">Assigned to:</label>
   <input type="text" name="owner" id="owner" accesskey="a" value="<?cs
     var:query.constraints.owner.0 ?>" />
  </div>
  <div>
   <label for="reporter">Reported by:</label>
   <input type="text" name="reporter" id="reporter" accesskey="b" value="<?cs
     var:query.constraints.reporter.0 ?>" />
  </div>
  <div>
   <label for="cc">Cc contains:</label>
   <input type="text" name="cc" id="cc" value="<?cs
     var:query.constraints.cc.0 ?>" />
  </div>
  <?cs if:len(query.custom) ?><?cs set:idx = 0 ?><?cs
   each:custom = query.custom ?><?cs
    if:custom.type == 'select' || custom.type == 'radio' ?>
     <?cs if:idx == 0 ?><br /><?cs /if ?><div>
      <label for="<?cs var:custom.name ?>"><?cs var:custom.label ?></label>
      <?cs call:hdf_select_multiple(custom.options, custom.name, 4) ?>
     </div><?cs set:idx = idx + 1 ?><?cs
    /if ?><?cs
   /each ?><?cs set:idx = 0 ?><?cs
   each:custom = query.custom ?><?cs
    if:custom.type == 'text' ?>
     <?cs if:idx == 0 ?><br /><?cs /if ?><div>
      <label for="<?cs var:custom.name ?>"><?cs var:custom.label ?></label>
      <input type="text" name="<?cs var:custom.name ?>" id="<?cs
        var:custom.name ?>" value="<?cs var:query[custom.name] ?>" />
     </div><?cs set:idx = idx + 1 ?><?cs
    /if ?><?cs
   /each ?><?cs
  /if ?>
  <br />
 </fieldset>
 <div class="buttons">
  <input type="submit" name="search" value="Search">
 </div>
</form>

<?cs else ?>

<?cs if:len(query.results) ?>
 <p><?cs var:len(query.results) ?> ticket<?cs if:len(query.results) != 1 ?>s<?cs
 /if ?> matched this query.</p>
 <table id="tktlist" class="listing">
  <thead><tr><?cs each:header = query.headers ?><?cs
   if:name(header) == 0 ?><th class="ticket<?cs
    if:header.order ?> <?cs var:header.order ?><?cs /if ?>">
    <a href="<?cs var:header.href ?>" title="Sort by ID (<?cs
      if:header.order == 'asc' ?>descending<?cs
      else ?>ascending<?cs /if ?>)">Ticket</a>
    </th><?cs
   else ?>
    <th<?cs if:header.order ?> class="<?cs var:header.order ?>"<?cs /if ?>>
     <a href="<?cs var:header.href ?>" title="Sort by <?cs
       var:header.name ?> (<?cs if:header.order == 'asc' ?>descending<?cs
       else ?>ascending<?cs /if ?>)"><?cs var:header.name ?></a>
    </th><?cs
   /if ?>
  <?cs /each ?></tr></thead>
  <tbody>
   <?cs each:result = query.results ?><tr class="<?cs
     if:name(result) % 2 ?>odd<?cs else ?>even<?cs /if ?> <?cs
     var:result.priority ?>">
    <?cs each:header = query.headers ?><?cs
     if:name(header) == 0 ?>
      <td class="ticket"><a href="<?cs var:result.href ?>" title="View ticket"><?cs
        var:result.id ?></a></td><?cs
     else ?>
      <td><?cs if:header.name == 'summary' ?>
       <a href="<?cs var:result.href ?>" title="View ticket"><?cs
         var:result[header.name] ?></a><?cs
      else ?>
       <?cs var:result[header.name] ?><?cs
      /if ?>
      </td><?cs
     /if ?>
    <?cs /each ?>
   </tr><?cs /each ?>
  </tbody>
 </table>
<?cs else ?>
 <p>No tickets matched this query.</p>
<?cs /if ?>

<?cs /if ?>

 <div id="help">
  <strong>Note:</strong> See <a href="<?cs var:$trac.href.wiki ?>/TracQuery">TracQuery</a> 
  for help on using queries.
 </div>

</div>
<?cs include:"footer.cs" ?>
