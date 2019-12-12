$(window).on('load', function () {
    $('#loading').hide()

});

$(document).ready(function() {
    $(document).on("click", "#submit_type",function() {
        $('#loading').show();
    });

});



var allEditors = document.querySelectorAll('.view_ckcontent');
for (var i = 0; i < allEditors.length; ++i) {
  ClassicEditor.create(allEditors[i],{

    image:{
            resizeUnit: 'px'
        },
        cloudServices: {
            tokenUrl: 'https://44234.cke-cs.com/token/dev/q4279F38NRh9uCkqeJQN2rUvNhll9K9d4vdLbHVuTbgOh6ZUSO0TEsdBS8Sg',
            uploadUrl: 'https://44234.cke-cs.com/easyimage/upload/'
       }
    } )
    .then()
    .catch();
}

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
