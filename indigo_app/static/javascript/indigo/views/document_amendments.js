(function(exports) {
  "use strict";

  if (!exports.Indigo) exports.Indigo = {};
  Indigo = exports.Indigo;

  /** This handles editing and creation of Amendment instances.
   */
  Indigo.AmendmentView = Backbone.View.extend({
    el: '#amendment-box',
    events: {
      'hidden.bs.modal': 'dismiss',
      'click .btn.save': 'save',
    },
    bindings: {
      '#amendment_date': 'date',
      '#amendment_title': 'amending_title',
      '#amendment_uri': 'amending_uri',
    },

    initialize: function(options) {
      this.document = options.document;
      this.chooser = new Indigo.DocumentChooserView({el: this.$el.find('.document-chooser')});
      this.chooser.on('chosen', this.chosen, this);
    },

    show: function(model) {
      var amending_doc = null;

      this.isNew = !model;
      this.originalModel = model;

      if (model) {
        // clone the amendment and edit the clone
        this.model = model.clone();
        // find the document the model corresponds to
        amending_doc = this.chooser.model.findWhere({frbr_uri: this.model.get('amending_uri')});
      } else {
        this.model = new Indigo.Amendment();
      }

      this.chooser.setFilters({country: this.document.get('country')});
      this.chooser.choose(amending_doc);

      this.stickit();

      this.$el.modal('show');
    },

    save: function(e) {
      if (this.isNew) {
        this.document.get('amendments').add(this.model);
      } else {
        this.originalModel.attributes = _.clone(this.model.attributes);
        this.originalModel.trigger('change');
      }

      this.document.get('amendments').sort();
      this.document.trigger('change change:amendments');
      this.$el.modal('hide');
    },
    
    dismiss: function() {
      this.unstickit();
      this.model = null;
      this.originalModel = null;
    },

    chosen: function() {
      // user chose a new item in the document chooser
      var chosen = this.chooser.chosen;
      if (chosen) {
        this.model.set({
          date: chosen.get('expression_date'),
          amending_title: chosen.get('title'),
          amending_uri: chosen.get('frbr_uri'),
          amending_id: chosen.get('id'),
        });
      }
    }
  });

  /**
   * Handle the document amendments display.
   *
   * Note that the amendments attribute of the document might
   * be changed outside of this view, in particular it could become
   * a new AmendmentList collection. That means we can't attach
   * event handlers, so the views above (and ours) must trigger
   * events on the owning document itself, not just the AmendmentList
   * collection.
   */
  Indigo.DocumentAmendmentsView = Backbone.View.extend({
    el: '.document-amendments-view',
    amendmentExpressionsTemplate: '#amendment-expressions-template',
    events: {
      'click .add-amendment': 'addAmendment',
      'click .edit-amendment': 'editAmendment',
      'click .delete-amendment': 'deleteAmendment',
    },

    initialize: function() {
      this.amendmentExpressionsTemplate = Handlebars.compile($(this.amendmentExpressionsTemplate).html());

      // TODO: sanity check
      this.model.on('change:amendments sync', this.render, this);
      this.model.on('change:frbr_uri', this.frbrChanged, this);
      this.frbrChanged();

      this.box = new Indigo.AmendmentView({model: null, document: this.model});
    },

    frbrChanged: function() {
      if (this.expressionSet) this.stopListening(this.expressionSet);
      this.expressionSet = this.model.collection.expressionSet(this.model.get('frbr_uri'));
      this.listenTo(this.expressionSet, 'add remove reset', this.render);
      this.listenTo(this.expressionSet.amendments, 'change add remove reset', this.render);
      this.render();
    },

    render: function() {
      var self = this;
      var document_id = this.model.get('id');
      var dates = this.expressionSet.allDates(),
          pubDate = this.expressionSet.initialPublicationDate();

      if (pubDate) {
        dates.push(pubDate);
        dates.sort();
      }

      // build up a view of amended expressions
      var amended_expressions = _.map(dates, function(date) {
        var doc = self.expressionSet.atDate(date);
        var info = {
          date: date,
          document: doc && doc.toJSON(),
          current: doc && doc.get('id') == document_id,
          amendments: _.map(self.expressionSet.amendmentsAtDate(date), function(a) { return a.toJSON(); }),
          initial: date == pubDate,
        };
        info.linkable = info.document && !info.current;

        return info;
      });

      this.$('.amendment-expressions').html(this.amendmentExpressionsTemplate({
        amended_expressions: amended_expressions,
      }));

      // update amendment count in nav tabs
      $('.sidebar .nav .amendment-count').text(this.expressionSet.length === 0 ? '' : this.expressionSet.length);
    },

    addAmendment: function(e) {
      e.preventDefault();
      this.box.show(null);
    },

    editAmendment: function(e) {
      e.preventDefault();

      var index = $(e.target).closest('li').data('index');
      var amendment = this.expressionSet.amendments.at(index);

      this.box.show(amendment);
    },

    deleteAmendment: function(e) {
      e.preventDefault();

      var index = $(e.target).closest('li').data('index');
      var amendment = this.expressionSet.amendments.at(index);

      if (confirm("Really delete this amendment?")) {
        this.expressionSet.amendments.remove(amendment);
        // TODO: sanity check
        this.model.trigger('change change:amendments');
      }
    },
  });
})(window);
