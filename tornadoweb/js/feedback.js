var sendFeedback = function sendFeedback(){
    if (! document.getElementById("fb-author").value){
        d3.select("#feedback").append("p").text("author field is required").attr("class", "fb-error");
        return;
    }
    if (!document.getElementById("fb-message").value){
        d3.select("#feedback").append("p").text("Message field is required").attr("class", "fb-error");
        return;
    }
    d3.selectAll(".fb-error").remove();

    var message = {ids: get_ids(),
        text: encodeURIComponent(document.getElementById("fb-message").value),
        author: encodeURIComponent(document.getElementById("fb-author").value)};
    d3.json("/feedback/send/"+JSON.stringify(message), function(err, resp){
        if (err){
            console.log(err)
            d3.select("#feedback").append("p").text("Feedback failed").attr("class", "fb-error");
        } else {
            d3.select("#feedback").append("p").text("Feedback successfully feedbacked.").attr("class", "fb-info");
        }
    });

};

