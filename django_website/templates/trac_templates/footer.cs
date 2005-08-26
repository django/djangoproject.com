<script type="text/javascript">searchHighlight()</script><?cs
if:len(chrome.links.alternate) ?>
<div id="altlinks"><h3>Download in other formats:</h3><ul><?cs
 each:link = chrome.links.alternate ?><?cs
  set:isfirst = name(link) == 0 ?><?cs
  set:islast = name(link) == len(chrome.links.alternate) - 1?><li<?cs
    if:isfirst || islast ?> class="<?cs
     if:isfirst ?>first<?cs /if ?><?cs
     if:isfirst && islast ?> <?cs /if ?><?cs
     if:islast ?>last<?cs /if ?>"<?cs
    /if ?>><a href="<?cs var:link.href ?>"<?cs if:link.class ?> class="<?cs
    var:link.class ?>"<?cs /if ?>><?cs var:link.title ?></a></li><?cs
 /each ?></ul></div><?cs
/if ?>

</div>

<div id="footer">
        <div id="metanav" class="nav"><?cs call:nav(chrome.nav.metanav) ?></div>
        </div>      
</div>

<?cs include "site_footer.cs" ?>
 </body>
</html>
