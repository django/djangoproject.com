define(['jquery'], function($) {
    var CorporateMembershipJoinForm = function(form) {
        this.form = $(form);
        this.init();
    };
    CorporateMembershipJoinForm.prototype = {
        init: function() {
            var self = this;
            var $amount = self.form.find('#id_amount');
            var $membershipLevel = self.form.find('#id_membership_level');
            $amount.change(function() {
                self.setMembershipLevel($(this), $membershipLevel);
            });
            $membershipLevel.change(function() {
                self.setDonationAmount($(this), $amount);
            });
        },
        setDonationAmount: function($membershipLevel, $amount) {
            var selectedMembership = $membershipLevel.val();
            if (selectedMembership == '5') {
                $amount.val(100000);
            } else if (selectedMembership == '4') {
                $amount.val(30000);
            } else if (selectedMembership == '3') {
                $amount.val(12500);
            } else if (selectedMembership == '2') {
                $amount.val(5000);
            } else if (selectedMembership == '1') {
                $amount.val(2000);
            } else {
                $amount.val('');
            }
        },
        setMembershipLevel: function($amount, $membershipLevel) {
            var amount = parseInt($amount.val());
            if (amount >= 100000) {
                $membershipLevel.val(5);
            } else if (amount >= 30000) {
                $membershipLevel.val(4);
            } else if (amount >= 12500) {
                $membershipLevel.val(3);
            } else if (amount >= 5000) {
                $membershipLevel.val(2);
            } else if (amount >= 2000) {
                $membershipLevel.val(1);
            } else {
                $membershipLevel.val('');
            }
        },
    };
    return new CorporateMembershipJoinForm('.corporate-membership-join-form');
});
