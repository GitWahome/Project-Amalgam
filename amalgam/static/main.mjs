

$(window).on('load', function () {
    $('#loading').hide()

});

$(document).ready(function() {
    $(document).on("click", "#submit_type",function() {
        $('#loading').show();
    });

});


/*******************************
* ACCORDION WITH TOGGLE ICONS
*******************************/
function toggleIcon(e) {
    $(e.target)
        .prev('.panel-heading')
        .find(".more-less")
        .toggleClass('icon-max icon-min');
}
$('.panel-group').on('hidden.bs.collapse', toggleIcon);
$('.panel-group').on('shown.bs.collapse', toggleIcon);

//Activate tooltips
$(document).ready(function() {
    $("body").tooltip({
        selector: '[data-toggle=tooltip]'
    });
});
