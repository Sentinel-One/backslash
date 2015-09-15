import Ember from 'ember';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function(params) {
    return Ember.RSVP.hash({
      test: this.store.find('test', params.test_id),
      testErrors: this.store.query('error',{test_id: params.test_id})

    });

  }
});
