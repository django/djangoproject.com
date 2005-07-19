<?cs include "header.cs"?>

<div id="ctxtnav" class="nav"></div>

<div id="content" class="error">

 <?cs if error.type == "TracError" ?>
  <h3><?cs var:error.title ?></h3>
  <p class="message">
  <?cs var:error.message ?>
  </p>

 <?cs elif error.type == "internal" ?>
  <h3>Oops...</h3>
  <div class="message">
   <strong>Trac detected an internal error:</strong>
   <pre><?cs var:error.message ?></pre>
  </div>
  <p>
   If you think this really should work and you can reproduce it. Then you 
   should consider to report this problem to the Trac team.
  </p>
  <p>
   Go to <a href="<?cs var:trac.href.homepage ?>"><?cs
     var:trac.href.homepage ?></a>  and create a new ticket where you describe
   the problem, how to reproduce it. Don't forget to include the python
   traceback found below.
  </p>

 <?cs elif error.type == "permission" ?>
  <h3>Permission Denied</h3>
  <p class="message">
  This action requires <tt><?cs var:error.action ?></tt> permission.
  </p>
  <div id="help">
   <strong>Note</strong>: See
   <a href="<?cs var:trac.href.wiki ?>/TracPermissions">TracPermissions</a> for
   help on managing Trac permissions.
  </div>

 <?cs /if ?>

 <p>
  <a href="<?cs var:trac.href.wiki ?>/TracGuide">TracGuide</a>
  &mdash; The Trac User and Administration Guide
 </p>

 <?cs if $error.traceback ?>
  <h4>Python traceback</h4>
  <pre><?cs var:error.traceback ?></pre>
 <?cs /if ?>

</div>
<?cs include "footer.cs"?>
