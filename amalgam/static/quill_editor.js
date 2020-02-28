var options = {
    modules: {
    toolbar: [
        [{ header: [1, 2, false] }],
        ['bold', 'italic', 'underline','strike'],
        ['image', 'video'],
        ['code-block','blockquote'],
        [{ 'align': [] }],
        [{ 'list': 'ordered'}, { 'list': 'bullet' }]
    ]
  },
  theme: 'snow'
};

var allEditors = document.querySelectorAll(".view_ckcontent");

for (var i = 0; i < allEditors.length; ++i) {
    var quill = new Quill(allEditors[i], options);
    $(allEditors[i]).show();
    let submit_button = document.getElementById('submit');
    var desc_hidden_text_field = document.getElementById('description');
    var cont_hidden_text_field = document.getElementById('content');
    submit_button.onclick = ()=>{
        let editorContent = quill.root.innerHTML;

        if (desc_hidden_text_field != undefined){
            desc_hidden_text_field.value = editorContent;
        }
        else if(cont_hidden_text_field != undefined){
            cont_hidden_text_field.value = editorContent;
        };

    };
};


//All displays
var displayEditors = document.querySelectorAll(".display_editor");
var displayConfig = {
  "theme": "snow",
  "modules": {
      "toolbar": false
  }
};

for (var i=0;i<displayEditors.length; ++i){
    var quill = new Quill(displayEditors[i], displayConfig);
    quill.disable();
    $(displayEditors[i]).show();

};
