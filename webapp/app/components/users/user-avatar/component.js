import Ember from 'ember';

export default Ember.Component.extend({

    classNames: "user-avatar",
    classNameBindings: ['small', 'large'],

    tooltip: function() {
        const real_email = this.get('real_email'), email = this.get('user_email');

        if (real_email) {
            return email + ' (through ' + real_email + ')';
        }
        return email;
    }.property('user_email', 'real_email'),

    email: null,
    real_email: null,
    admin: false,
    moderator: false,

    user_email: function() {
        if (this.get('user')) {
            return this.get('user.email');
        }
        return this.get('email');
    }.property('user', 'email'),


    is_admin: function() {
        return this._has_role('admin') || this.get('admin');
    }.property('user.user_roles'),

    is_moderator: function() {
        return this._has_role('moderator') || this.get('moderator');
    }.property('user.user_roles'),

    _has_role: function(role) {
        let roles = [];
        let user_roles = this.get('user.user_roles');

        if (!user_roles) {
            return false;
        }
        user_roles.forEach(r => roles.push(r.name));
        return roles.indexOf(role) !== -1;
    }
});
