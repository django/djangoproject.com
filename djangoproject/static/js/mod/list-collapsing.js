define([
  'jquery', //requires jquery
], ($) => {
  class CollapsingList {
    constructor(list) {
      this.list = $(list);
      this.init();
    }

    init() {
      const self = this; //self = this for functions

      this.items = this.list.children('li'); //get items
      this.headings = this.items.children('h2'); //get headings

      this.buttonExpand = $('<span class="expandall">Expand All</span>'); //build buttons
      this.buttonCollapse = $('<span class="collapseall">Collapse All</span>'); //build buttons
      this.buttonContainer = $(
        '<span class="form-controls label"></span>',
      ).insertBefore(this.list); //create a button container
      this.buttonContainer //append container to label
        .append(this.buttonExpand)
        .append(' / ')
        .append(this.buttonCollapse);

      this.list.addClass('active'); //activate the list styles w/ class
      this.headings
        .append(' <i class="collapsing-icon icon icon-plus"></i>')
        .attr('tabindex', '0'); //add icons and tabindexes

      this.headings.on('click', (ev) => {
        const target = $(ev.target).closest('h2');
        const parent = target.closest('li');
        parent.toggleClass('active'); //toggle active class
      });

      this.buttonExpand.on('click', () => {
        //expand all onclick
        self.items.addClass('active');
      });
      this.buttonCollapse.on('click', () => {
        //expand all onclick
        self.items.removeClass('active');
      });

      //expand list item with matching hash id
      if (hash) {
        $(hash).addClass('active');
        const pos = $(hash).position();
        $(globalThis).scrollTop(pos.top);
      }
    }
  }

  const hash = globalThis.location.hash;

  //return a new module for each class detected
  $('.list-collapsing').each(function () {
    return new CollapsingList(this);
  });
});
