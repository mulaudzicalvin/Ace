odoo.define("sale_order_type.models_cust", function (require){
	
	"use strict";

	var models = require("point_of_sale.models");

	models.load_fields('account.tax','tax_type');

	models.Orderline = models.Orderline.extend({
		_compute_all: function (tax, base_amount, quantity) {
			// this._super(this);
			if(tax.tax_type === 'cgst' || tax.tax_type === 'sgst'){
				if (tax.amount_type === 'fixed') {
		            var sign_base_amount = base_amount >= 0 ? 1 : -1;
		            return (Math.abs(tax.amount) * sign_base_amount) * quantity;
		        }
		        if ((tax.amount_type === 'percent' && !tax.price_include) || (tax.amount_type === 'division' && tax.price_include)){
		            return base_amount * tax.amount / 100;
		        }
		        if (tax.amount_type === 'percent' && tax.price_include){
		            return base_amount - (base_amount / (1 + tax.amount / 100));
		        }
		        if (tax.amount_type === 'division' && !tax.price_include) {
		            return base_amount / (1 - tax.amount / 100) - base_amount;
		        }
		        return false;
		    }
		    return false;
		}
	});
});