/**
 * Script to fix doc version switcher according to scroll position
 */
function add_event(html_element, event_name, event_function) {       
   if(html_element.attachEvent) // IE
      html_element.attachEvent("on" + event_name, function() {event_function.call(html_element);}); 
   else if(html_element.addEventListener)
      html_element.addEventListener(event_name, event_function, false); 
} 
function get_window_height() {
  if( typeof( window.innerWidth ) == 'number' ) {
    return window.innerHeight; // Non-IE
  } else if( document.documentElement && ( document.documentElement.clientWidth || document.documentElement.clientHeight ) ) {
    return document.documentElement.clientHeight; //IE 6+ in 'standards compliant mode'
  }
}
var affix_version_update = function(e) {
  var body = document.body,
      html = document.documentElement,
      height = Math.max( body.scrollHeight, body.offsetHeight, html.clientHeight, html.scrollHeight, html.offsetHeight ),
      scrollTop = window.pageYOffset || document.documentElement.scrollTop,
      footer_height = document.getElementById('footer').clientHeight + 10 + document.getElementById('content-secondary').clientHeight,
      window_height = get_window_height(),
      obj = document.getElementById('doc-versions');
 
 if (scrollTop + window_height > height - footer_height) {
    obj.style.bottom = footer_height + "px";
    obj.style.position = "absolute";
 } else {
    obj.style.bottom = "0px";
    obj.style.position = "fixed";
 }
}
var affix_version_position = function(){
  var width = document.getElementById('container').clientWidth,
      obj = document.getElementById('doc-versions');
  obj.style.left = Math.round(width*0.7) + "px";
  obj.style.width = Math.round(width*0.3) + "px";
}
var affix_version_init = function() {
  this.className = this.className + " versions-affix";

  affix_version_position();
  add_event(window, 'scroll', affix_version_update);
  add_event(window, 'resize', affix_version_position);
}

affix_version_init.call( document.getElementById('doc-versions') );