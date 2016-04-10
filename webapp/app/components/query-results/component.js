import Ember from 'ember';

export default Ember.Component.extend({

    results: null,
    humanize_times: true,
    show_subjects: true,

    available_page_sizes: [25, 50, 100, 200],


    page: Ember.computed.oneWay('results.meta.page'),
    pages_total: Ember.computed.oneWay('results.meta.pages_total'),
    page_size: null,
    filter_config: Ember.computed.oneWay('results.meta.filter_config'),


    actions: {
        set_page_size(size) {
            this.set('page_size', size);
        },
    },
});
