<script type="text/javascript">searchHighlight()</script>

<?cs if:len(links.alternate) ?>
<div id="altlinks">
 <h3>Download in other formats:</h3>
 <ul><?cs each:link = links.alternate ?><?cs
  set:isfirst = name(link) == 0 ?><?cs
  set:islast = name(link) == len(links.alternate) - 1?>
  <li<?cs
    if:isfirst || islast ?> class="<?cs
     if:isfirst ?>first<?cs /if ?><?cs
     if:isfirst && islast ?> <?cs /if ?><?cs
     if:islast ?>last<?cs /if ?>"<?cs
    /if ?>>
   <a href="<?cs var:link.href ?>"<?cs if:link.class ?> class="<?cs
    var:link.class ?>"<?cs /if ?>><?cs var:link.title ?></a>
  </li><?cs /each ?>
 </ul>
</div>
<?cs /if ?>


</div>

<div id="footer">
        <div id="metanav" class="nav">
         <h2>Navigation</h2>
         <ul>
          <li class="first"><?cs if:trac.authname == "anonymous" || !trac.authname ?>
            <a href="<?cs var:trac.href.login ?>">Login</a>
          <?cs else ?>
            logged in as <?cs var:trac.authname ?> </li>
            <li><a href="<?cs var:trac.href.logout ?>">Logout</a>
          <?cs /if ?></li>
          <li><a href="<?cs var:trac.href.settings ?>">Settings</a></li>
          <li style="display: none"><a accesskey="6" href="<?cs var:trac.href.wiki ?>/TracGuide">Help/Guide</a></li>
          <li style="display: none"><a accesskey="5" href="http://projects.edgewall.com/trac/wiki/TracFaq">FAQ</a></li>
          <li style="display: none"><a accesskey="0" href="<?cs var:trac.href.wiki ?>/TracAccessibility">Accessibility</a></li>
          <li class="last"><a accesskey="9" href="<?cs var:trac.href.about ?>">About Trac</a></li>
         </ul>
        </div>
</div>


<?cs include "site_footer.cs" ?>
 </body>
</html>
