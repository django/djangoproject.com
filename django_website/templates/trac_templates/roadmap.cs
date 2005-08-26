<?cs set:html.stylesheet = 'css/roadmap.css' ?>
<?cs include "header.cs"?>
<?cs include "macros.cs"?>

<div id="ctxtnav" class="nav">
 <ul>
  <?cs if:roadmap.href.newmilestone ?><li><a href="<?cs
    var:roadmap.href.newmilestone ?>">Add New Milestone</a></li><?cs /if ?>
  <li class="last"><a href="<?cs var:roadmap.href.list ?>"><?cs
    if:roadmap.showall ?>Show All Milestones<?cs
    else ?>Show Upcoming Milestones<?cs /if ?></a></li>
 </ul>
</div>

<div id="content" class="roadmap">
 <h1>Roadmap</h1>

 <ul class="milestones"><?cs each:milestone = roadmap.milestones ?>
  <li class="milestone">
   <div class="info">
    <h2><a href="<?cs var:milestone.href ?>">Milestone: <em><?cs
      var:milestone.name ?></em></a></h2>
    <p class="date"><?cs if:milestone.date ?>
     <?cs var:milestone.date ?><?cs else ?>No date set<?cs /if ?>
    </p>
    <?cs with:stats = milestone.stats ?>
     <?cs if:#stats.total_tickets > #0 ?>
      <div class="progress">
       <div style="width: <?cs var:#stats.percent_complete ?>%"></div>
      </div>
      <p class="percent"><?cs var:#stats.percent_complete ?>%</p>
      <dl>
       <dt>Active tickets:</dt>
       <dd><a href="<?cs var:milestone.queries.active_tickets ?>"><?cs
         var:stats.active_tickets ?></a></dd>
       <dt>Closed tickets:</dt>
       <dd><a href="<?cs var:milestone.queries.closed_tickets ?>"><?cs
         var:stats.closed_tickets ?></a></dd>
      </dl>
     <?cs /if ?>
    <?cs /with ?>
   </div>
   <div class="descr"><?cs var:milestone.descr ?></div>
  </li>
 <?cs /each ?></ul>

 <div id="help">
  <strong>Note:</strong> See <a href="<?cs
    var:trac.href.wiki ?>/TracRoadmap">TracRoadmap</a> for help on using the roadmap.
 </div>

</div>
<?cs include:"footer.cs"?>
