import Ember from 'ember';

export default Ember.Component.extend({
    tagName: 'span',
    classNames: ['label'],
    classNameBindings: ['label_class'],

    status: null,

    label_class: function() {
	switch(this.get('status').toLowerCase()) {
	case 'success':
	    return 'label-success';
	case 'error':
	case 'failure':
	    return 'label-danger';
	case 'skipped':
	    return 'label-warning';
	default:
	    return 'label-default';
	}
    }.property('status'),
});
