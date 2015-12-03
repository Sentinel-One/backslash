import Ember from 'ember';

import PaginatedFilteredController from '../controllers/paginated_filtered_controller';

export default PaginatedFilteredController.extend({
    collection: Ember.computed.oneWay('sessions'),
});
