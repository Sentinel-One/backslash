import Ember from 'ember';

export function titleCase(params/*, hash*/) {
    return params[0].replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}

export default Ember.Helper.helper(titleCase);
