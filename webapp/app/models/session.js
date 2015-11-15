import DS from 'ember-data';
import Ember from 'ember';
import HasLogicalId from '../mixins/has-logical-id';

export default DS.Model.extend(HasLogicalId, {

    archived: DS.attr('boolean'),
    investigated: DS.attr('boolean'),

    start_time: DS.attr('number'),
    end_time: DS.attr('number'),

    is_abandoned: DS.attr('boolean'),

    num_error_tests: DS.attr('number'),
    num_errors: DS.attr('number'),
    num_failed_tests: DS.attr('number'),
    num_finished_tests: DS.attr('number'),
    num_skipped_tests: DS.attr('number'),

    total_num_tests: DS.attr('number'),

    num_warnings: DS.attr('number'),

    status: DS.attr('string'),

    subjects: DS.attr(),
    user_email: DS.attr(),

    real_email: DS.attr(),

    is_delegate: Ember.computed.notEmpty('real_email'),

    is_running: function() {
        return this.get('status') === 'RUNNING';
    }.property('status'),

    typename: 'session'

});
