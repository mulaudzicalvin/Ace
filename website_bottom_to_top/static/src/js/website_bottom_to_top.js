odoo.define("website_up_down.updown", function (require) {
    "use strict";

    $(document).ready(function () {
        $("#btn_scroll_up").click(function(ev){
            document.body.scrollTop = 0; // For Chrome, Safari and Opera
            document.documentElement.scrollTop = 0; // For IE and Firefox
         });

        window.onscroll = function() {scrollFunction()};

        function scrollFunction() {

            if (document.body.scrollTop > 200 || document.documentElement.scrollTop > 200) {
                $("#btn_scroll_up").attr('style','display: block');
            } else {
                $("#btn_scroll_up").attr('style','display: none');
            }
        }

        // When the user clicks on the button, scroll to the top of the document
        function topFunction() {
            document.body.scrollTop = 0; // For Chrome, Safari and Opera
            document.documentElement.scrollTop = 0; // For IE and Firefox
        }

    });

});
