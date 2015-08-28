
init_page = function(){
    $("#wiki_link").change(function(){
        var new_link = $('#wiki_link').val();
        var req_type = "wiki"
        $.ajax({
                url: "/tech_add/json/",
                type: 'POST',
                data: JSON.stringify({
                        type: req_type,
                        link: new_link
                }),
                success: function (jsonResponse) {
                    var objresponse = jsonResponse;
                    console.log(objresponse);
                    $("#wiki_all_block").fadeIn();
                    $("#wiki_all").val(objresponse);
                },
                error: function(){
                    alert("can't get wiki links");
                    $("#wiki_all_block").fadeOut();
                }
               })
    });
};
$(init_page);