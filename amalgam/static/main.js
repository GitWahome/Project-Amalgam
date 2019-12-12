//import Base64UploadAdapter from '@ckeditor/ckeditor5-upload/src/adapters/base64uploadadapter.js';

$(window).on('load', function () {
    $('#loading').hide()

});

$(document).ready(function() {
    $(document).on("click", "#submit_type",function() {
        $('#loading').show();
    });

});

ClassicEditor.create( document.querySelector( '#editor, #content' ),{
        image:{
            resizeUnit: 'px',
            toolbar:['ImageResize','imageUpload','ImageToolBar','imageTextAlternative','|', 'imageStyle:alignLeft', 'imageStyle:full', 'imageStyle:alignRight' ],
            styles: [
                // This option is equal to a situation where no style is applied.
                'full',

                // This represents an image aligned to the left.
                'alignLeft',

                // This represents an image aligned to the right.
                'alignRight'
            ]
        },
        cloudServices: {
            tokenUrl: 'https://44234.cke-cs.com/token/dev/q4279F38NRh9uCkqeJQN2rUvNhll9K9d4vdLbHVuTbgOh6ZUSO0TEsdBS8Sg',
            uploadUrl: 'https://44234.cke-cs.com/easyimage/upload/'
       }
    } )
    .then()
    .catch();

/*******************************
* ACCORDION WITH TOGGLE ICONS
*******************************/
	function toggleIcon(e) {
        $(e.target)
            .prev('.panel-heading')
            .find(".more-less")
            .toggleClass('glyphicon-plus glyphicon-minus');
    }
    $('.panel-group').on('hidden.bs.collapse', toggleIcon);
    $('.panel-group').on('shown.bs.collapse', toggleIcon);