export function initialize(/* application */) {
	let locale = window.navigator.userLanguage || window.navigator.language;
	moment.locale(locale,{
		longDateFormat : {
	        LT : "HH:mm",
	        LTS : "HH:mm:ss",
	        L : "DD/MM/YYYY",
	        LL : "D MMMM YYYY",
	        LLL : "D MMMM YYYY LT",
	        LLLL : "dddd D MMMM YYYY LT"
	    },
		calendar:{
			sameElse:"L LTS"
		}
	});
}

export default {
  name: 'moment',
  initialize: initialize
};
