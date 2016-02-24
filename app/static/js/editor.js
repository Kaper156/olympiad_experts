var flash_messages = function(data){

    var flash = $('.flash-list');
    //foreach warnings
    for(var warning in data['warning']){
        flash.append('<div class="alert alert-warning" role="alert">'+warning+'</div>');
    }
    //foreach primary
    for(var primary in data['primary']){
        flash.append('<div class="alert alert-primary" role="alert">'+primary+'</div>');
    }
};


//path      tr-element address
//elements  eq-field addresses eq=list($,data)
var set_element = function(path, elements){
    for(var elem in elements){
        path.find(elem[0]).html(elem[1])
    }
};

var set_element_olympiad = function(olymp){
    var path = $('#objects-table tbody');
    path.append('<tr></tr>');
    path = path.find('tr').last();

    for(var i=0;i++;i>7){
        path.append('<td></td>')
    }


    var elements = [];
    elements[0] = ['td:1', olymp.id];
    elements[0] = ['td:1', olymp.name];
    elements[0] = ['td:1', olymp.date];
    elements[0] = ['td:1', 'open']; //TODO STATUS
    elements[0] = ['td:1', olymp.description];
    elements[0] = ['td:1', olymp.description];

};

$(document).ready(function () {
    var editors = $('.editor.modal').find('form');
    //var new_editor = $('#editor-new').find('form');
    editors.each(function () {
        var editor = $(this);
        var url = editor.attr('action');
        editor.ajaxForm({
            url: url,
            type: 'POST',
            success: function (data) {
                flash_messages(data);
            }
        });
    });

});
