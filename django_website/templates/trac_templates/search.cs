<?cs set:html.stylesheet = 'css/search.css' ?>
<?cs include "header.cs"?>
<script type="text/javascript">
addEvent(window, 'load', function() { document.getElementById('q').focus()}); 
</script>

<div id="ctxtnav" class="nav">
 <h2>Search Navigation</h2>
 <ul><?cs
  if:len(links.prev) ?>
   <li class="first<?cs if:!len(links.next) ?> last<?cs /if ?>">
    <a href="<?cs var:links.prev.0.href ?>" title="<?cs
      var:links.prev.0.title ?>">Previous Page</a>
   </li><?cs
  /if ?><?cs
  if:len(links.next) ?>
   <li class="<?cs if:len(links.prev) ?>first <?cs /if ?>last">
    <a href="<?cs var:links.next.0.href ?>" title="<?cs
      var:links.next.0.title ?>">Next Page</a>
   </li><?cs
  /if ?>
 </ul>
</div>

<div id="content" class="search">

<h1><label for="q">Search</label></h1>
<form action="<?cs var:trac.href.search ?>" method="get">
 <p>
  <input type="text" id="q" name="q" size="40" value="<?cs var:search.q ?>" />
  <input type="submit" value="Search" />
 </p>
 <p><?cs
  if:trac.acl.WIKI_VIEW ?>
   <input type="checkbox" id="wiki" name="wiki" <?cs
     if:search.wiki ?>checked="checked"<?cs /if ?> />
   <label for="wiki">Wiki</label><?cs
  /if ?><?cs
  if:trac.acl.TICKET_VIEW ?>
   <input type="checkbox" id="ticket" name="ticket" <?cs
     if:search.ticket ?>checked="checked"<?cs /if ?> />
   <label for="ticket">Tickets</label><?cs
  /if ?><?cs
  if:trac.acl.CHANGESET_VIEW ?>
   <input type="checkbox" id="changeset" name="changeset" <?cs
     if:search.changeset ?>checked="checked"<?cs /if ?> />
   <label for="changeset">Changesets</label><?cs
  /if ?>
 </p>
</form>

<?cs def result(title, keywords, body, link) ?>
 <dt><a href="<?cs var:link ?>"><?cs var:title ?></a></dt>
 <dd><?cs var:body ?></dd>
 <dd>
  <span class="author">By <?cs var:item.author ?></span> &mdash;
  <span class="date"><?cs var:item.datetime ?></span><?cs
  if:item.keywords ?> &mdash
   <span class="keywords">Keywords: <em><?cs var:item.keywords ?></em></span><?cs
  /if ?>
 </dd>
<?cs /def ?>

<?cs if:len(search.result) ?>
 <hr />
 <h2>Search results <?cs
  if:len(links.prev) || len(links.next) ?>(<?cs
   var:search.result_page * search.results_per_page + 1 ?> - <?cs
   var:search.result_page * search.results_per_page + len(search.result) ?>)<?cs
  /if ?></h2>
 <div id="searchable">
  <dl id="results"><?cs
   each item=search.result ?><?cs
    if:item.type == 1 ?><?cs
     call:result('[' + item.data + ']: ' + item.shortmsg, item.keywords,
                 item.message, item.changeset_href) ?><?cs
    elif:item.type == 2 ?><?cs
     call:result('#' + item.data + ': ' + item.title, item.keywords,
                 item.message, item.ticket_href) ?><?cs
    elif:item.type == 3 ?><?cs
     call:result(item.data + ': ' + item.shortmsg, item.keywords,
                 item.message, item.wiki_href) ?><?cs
    /if ?><?cs
   /each ?>
  </dl>
  <hr />
 </div>
 <?cs if:len(links.prev) || len(links.next) ?>
  <div id="paging" class="nav">
   <ul><?cs
    if:len(links.prev) ?>
     <li class="first<?cs if:!len(links.next) ?> last<?cs /if ?>">
      <a href="<?cs var:links.prev.0.href ?>" title="<?cs
        var:links.prev.0.title ?>">Previous Page</a>
     </li><?cs
    /if ?><?cs
    if:len(links.next) ?>
     <li class="<?cs if:len(links.prev) ?>first <?cs /if ?>last">
      <a href="<?cs var:links.next.0.href ?>" title="<?cs
        var:links.next.0.title ?>">Next Page</a>
     </li><?cs
    /if ?>
   </ul>
  </div>
 <?cs /if ?>

<?cs elif $search.q ?>
 <div id="notfound">No matches found.</div>
<?cs /if ?>

 <div id="help">
  <strong>Note:</strong> See <a href="<?cs var:$trac.href.wiki ?>/TracSearch">TracSearch</a>  for help on searching.
 </div>

</div>
<?cs include "footer.cs"?>
